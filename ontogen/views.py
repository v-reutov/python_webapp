import re
import json
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.shortcuts import render, get_object_or_404
from django.views.generic import detail, edit
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy

from .utils.decorators import ajax_only, ajax_login_only, ontogen_login_required, permission_check
from .utils.helpers import ExtraContext
from .core import OntologyGenerator
from . import models
from . import forms

@ontogen_login_required
def index(request):
    return render(request, 'ontogen/index.html', {
        'instructions' : models.Instruction.objects.all(), #pylint: disable=E1101
        'patterns' : models.Pattern.objects.all()          #pylint: disable=E1101
    })

@ajax_login_only
def ok_response(request): #pylint: disable=W0613
    return HttpResponse("OK")

@ajax_login_only
def get_tree_data(request): #pylint: disable=W0613
    tree = []
    tree.append(models.get_resources())
    return HttpResponse(json.dumps(tree), content_type="application/json")

@ontogen_login_required
def generate_ont(request):
    selected_nodes = request.POST.get('checked_ids', None)
    context = {}
    context['error_message'] = ""

    try:
        selected_instruction_id = int(re.findall(r'instruction(\d+)', selected_nodes)[0])
    except IndexError:
        context['error_message'] = 'No instruction was selected'
        return render(request, 'ontogen/result.html', context)

    selected_patterns = \
        [int(pattern_id) for pattern_id in re.findall(r'pattern(\d+)', selected_nodes)]
    if selected_patterns == []:
        context['error_message'] = 'No patterns were selected'
        return render(request, 'ontogen/result.html', context)

    text = models.Instruction.objects.get(pk=selected_instruction_id).instruction_text #pylint: disable=E1101
    patterns = [models.Pattern.objects.get(pk=pattern_id) for pattern_id in selected_patterns] #pylint: disable=E1101
    context['ontology'] = OntologyGenerator.generate_ontology_from_text(text, patterns)

    return render(request, 'ontogen/result.html', context)

def PatternCreateUpdateView(request, pattern_id=None):
    """Template for using pattern_form"""
    if pattern_id:
        # update
        pattern = get_object_or_404(models.Pattern, pk=pattern_id)
        header = 'Edit pattern'
        extra_forms = 0
    else:
        # create
        pattern = models.Pattern()
        header = 'Add new pattern'
        extra_forms = 1

    PatternFormSet = inlineformset_factory(
        models.Pattern,
        models.Mapping,
        fields=('mapping_label', 'mapping_value'), extra=extra_forms)

    if request.method == 'POST':
        form = forms.PatternForm(request.POST, instance=pattern)
        if form.is_valid():
            formset = PatternFormSet(request.POST, request.FILES, instance=pattern)
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
                  {'header': header, 'form' : form, 'formset' : formset})

"""
Pattern CRUD views
"""
@ajax_login_only
@permission_check('ontogen.add_pattern', 'create new patterns')
def PatternCreateView(request):
    return PatternCreateUpdateView(request)

@method_decorator(ajax_login_only, name='dispatch')
class PatternDetailView(detail.DetailView):
    model = models.Pattern

@ajax_login_only
@permission_check('ontogen.change_pattern', 'edit patterns')
def PatternUpdateView(request, pattern_id):
    return PatternCreateUpdateView(request, pattern_id)

@method_decorator(
    [ajax_login_only, permission_check('ontogen.delete_pattern', 'delete patterns')],
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
    [ajax_login_only, permission_check('ontogen.add_instruction', 'add instructions')],
    name='dispatch')
class InstructionCreateView(ExtraContext, edit.CreateView):
    model = models.Instruction
    fields = ['instruction_label', 'instruction_text']
    success_url = reverse_lazy('ontogen:ok')

@method_decorator(
    [ajax_login_only, permission_check('ontogen.change_instruction', 'edit instructions')],
    name='dispatch')
class InstructionUpdateView(ExtraContext, edit.UpdateView):
    model = models.Instruction
    fields = ['instruction_label', 'instruction_text']
    success_url = reverse_lazy('ontogen:ok')

@method_decorator(
    [ajax_login_only, permission_check('ontogen.delete_instruction', 'delete instructions')],
    name='dispatch')
class InstructionDeleteView(edit.DeleteView):
    model = models.Instruction
    success_url = reverse_lazy('ontogen:ok')
