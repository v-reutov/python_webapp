import re
import json
from django.http import HttpResponse, JsonResponse
from django.utils import formats
from django.forms import inlineformset_factory
from django.shortcuts import render, get_object_or_404
from django.views.generic import detail, edit
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import activate
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt

from .utils.decorators import ajax_only, ajax_login_only
from .utils.decorators import ontogen_login_required, permission_check
from .utils.helpers import ExtraContext
from .core import OntologyGenerator
from . import models
from . import forms


@ontogen_login_required
def index(request):
    activate('ru')
    return render(request, 'ontogen/index.html', {
        'instructions': models.Instruction.objects.all(),
        'patterns': models.Pattern.objects.all()
    })


@ajax_login_only
def ok_response(request):
    return HttpResponse("OK")


@ajax_login_only
def get_tree_data(request):
    tree = []
    tree.append(models.get_resources())
    return HttpResponse(json.dumps(tree), content_type="application/json")


def get_instruction_from_nodes(selected_nodes):
    selected_instruction_id = \
            int(re.findall(r'instruction(\d+)', selected_nodes)[0])
    return models.Instruction.objects.get(pk=selected_instruction_id)


def get_pattern_ids_from_nodes(selected_nodes):
    return [int(pattern_id) for
        pattern_id in re.findall(r'pattern(\d+)', selected_nodes)]


def get_patterns_from_ids(pattern_ids):
    return [models.Pattern.objects.get(
        pk=int(pattern_id)) for pattern_id in pattern_ids]


def get_patterns_from_nodes(selected_nodes):
    selected_patterns = get_pattern_ids_from_nodes(selected_nodes)
    return get_patterns_from_ids(selected_patterns)


@ontogen_login_required
def generate_ont(request):
    selected_nodes = request.POST.get('checked_ids', None)
    context = {}
    context['error_message'] = ""

    try:
        instruction = get_instruction_from_nodes(selected_nodes)
    except (IndexError, TypeError):
        context['error_message'] = _('No instruction was selected')
        return render(request, 'ontogen/result.html', context)

    patterns = get_patterns_from_nodes(selected_nodes)
    if patterns == []:
        context['error_message'] = _('No patterns were selected')
        return render(request, 'ontogen/result.html', context)

    subject_ontology, applied_ontology = \
        OntologyGenerator.generate_ontologies_from_text(instruction.instruction_text, patterns)

    context['subject_ontology'] = subject_ontology
    context['applied_ontology'] = applied_ontology

    rec = models.HistoryRecord()
    rec.user = request.user
    rec.instruction = instruction
    rec.save()
    for pattern in patterns:
        rec.patterns.add(pattern)

    prefix = formats.date_format(rec.datetime, "SHORT_DATETIME_FORMAT")
    sub_ont = json.dumps(
        json.loads(subject_ontology),
        ensure_ascii=False, indent=4)
    sub_ontology = models.Ontology(
        ont=sub_ont, ontology_type='subject',
        name=prefix + " subject-ontology")
    sub_ontology.save()
    rec.results.add(sub_ontology)

    app_ont = json.dumps(
        json.loads(applied_ontology),
        ensure_ascii=False, indent=4)
    app_ontology = models.Ontology(
        ont=app_ont, ontology_type='applied',
        name=prefix + " applied-ontology")
    app_ontology.save()
    rec.results.add(app_ontology)

    context['ontology'] = OntologyGenerator.merge_ontologies(
        subject_ontology, applied_ontology
    )
    context['datetime_prefix'] = rec.datetime

    return render(request, 'ontogen/result_new.html', context)


def PatternCreateUpdateView(request, pattern_id=None):
    """Template for using pattern_form"""
    if pattern_id:
        # update
        pattern = get_object_or_404(models.Pattern, pk=pattern_id)
        header = _('Edit pattern')
        extra_forms = 0
    else:
        # create
        pattern = models.Pattern()
        header = _('Add new pattern')
        extra_forms = 1

    PatternFormSet = inlineformset_factory(
        models.Pattern,
        models.Mapping,
        fields=('mapping_label', 'mapping_value'), extra=extra_forms)

    if request.method == 'POST':
        form = forms.PatternForm(request.POST, instance=pattern)
        if form.is_valid():
            formset = PatternFormSet(
                request.POST, request.FILES, instance=pattern)
            if formset.is_valid():
                form.save()
                formset.save()
                return HttpResponse("OK")
        else:
            formset = PatternFormSet(request.POST, request.FILES)
    else:
        if pattern_id:
            pattern = get_object_or_404(models.Pattern, pk=pattern_id)
        else:
            pattern = models.Pattern()
        form = forms.PatternForm(instance=pattern)
        formset = PatternFormSet(instance=pattern)

    return render(request, 'ontogen/pattern_form.html',
                  {'header': header, 'form': form, 'formset': formset})

"""
Pattern CRUD views
"""


@ajax_login_only
# Translators: used to complete sentence "You don't have enough
# permissions to ..."
@permission_check('ontogen.add_pattern', _('create new patterns'))
def PatternCreateView(request):
    return PatternCreateUpdateView(request)


@method_decorator(ajax_login_only, name='dispatch')
class PatternDetailView(detail.DetailView):
    model = models.Pattern


@ajax_login_only
# Translators: used to complete sentence "You don't have enough
# permissions to ..."
@permission_check('ontogen.change_pattern', _('edit patterns'))
def PatternUpdateView(request, pattern_id):
    return PatternCreateUpdateView(request, pattern_id)


@method_decorator(
    [ajax_login_only,
     # Translators: used to complete sentence "You don't have enough
     # permissions to ..."
     permission_check('ontogen.delete_pattern', _('delete patterns'))],
    name='dispatch')
class PatternDeleteView(edit.DeleteView):
    model = models.Pattern
    success_url = reverse_lazy('ontogen:ok')

"""
Instructions CRUD views
"""


@method_decorator(ajax_only, name='dispatch')
class InstructionDetailView(detail.DetailView):
    model = models.Instruction


@method_decorator(
    [ajax_login_only,
     # Translators: used to complete sentence "You don't have enough
     # permissions to ..."
     permission_check('ontogen.add_instruction', _('add instructions'))],
    name='dispatch')
class InstructionCreateView(ExtraContext, edit.CreateView):
    model = models.Instruction
    fields = ['instruction_label', 'instruction_content']
    success_url = reverse_lazy('ontogen:ok')


@method_decorator(
    [ajax_login_only,
     # Translators: used to complete sentence "You don't have enough
     # permissions to ..."
     permission_check('ontogen.change_instruction', _('edit instructions'))],
    name='dispatch')
class InstructionUpdateView(ExtraContext, edit.UpdateView):
    model = models.Instruction
    fields = ['instruction_label', 'instruction_content']
    success_url = reverse_lazy('ontogen:ok')


@method_decorator(
    [ajax_login_only,
     # Translators: used to complete sentence "You don't have enough
     # permissions to ..."
     permission_check('ontogen.delete_instruction', _('delete instructions'))],
    name='dispatch')
class InstructionDeleteView(edit.DeleteView):
    model = models.Instruction
    success_url = reverse_lazy('ontogen:ok')


@ontogen_login_required
def usage_history(request):
    context = {
        'records': models.HistoryRecord.objects.all().order_by('-datetime')}
    return render(request, 'ontogen/history.html', context)

@ontogen_login_required
def generate_page(request):
    selected_nodes = request.POST.get('checked_ids', None)

    instruction = get_instruction_from_nodes(selected_nodes)
    patterns = get_pattern_ids_from_nodes(selected_nodes)

    return render(request, 'ontogen/generate.html', {
        'instruction': instruction,
        'patterns': json.dumps(patterns),
    })


@csrf_exempt
@ajax_login_only
def generate_subject_ont(request):
    text = request.POST['text']
    pattern_ids = request.POST.getlist('patterns[]')

    print(pattern_ids)

    patterns = get_patterns_from_ids(pattern_ids)
    ont = OntologyGenerator.generate_subject_ontology(text, patterns)

    return JsonResponse({
        'status': 'OK',
        'result': ont,
    })