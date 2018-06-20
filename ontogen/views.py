import re
import json
import uuid
import base64
import datetime

from django.utils import dateformat
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
from django.core.files.base import ContentFile

from .utils.decorators import ajax_only, ajax_login_only
from .utils.decorators import ontogen_login_required, permission_check
from .utils.helpers import ExtraContext
from .utils.simplyfire import *
from .core import OntologyGenerator, OntologyBuilder, constants
from .core.Ontology import Ontology
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
    tree = [get_resources()]
    return HttpResponse(json.dumps(tree), content_type="application/json")


def get_multimedia_data():
    return {
        "text": _("Multimedia data"),
        "type": "pattern-container",
        "children": [
            {
                "id": "obj1",
                "type": "data",
                "text": "test2"
            },
            {
                "id": "obj2",
                "type": "data",
                "text": "test3"
            }
        ],
        "li_attr": {
            "class": "select-multiple capitalized"
        }
    }


def get_resources():
    return {
        "text": _("Resources"),
        "type": "resource-root",
        "children": [
            models.Instruction.get_json_all(),
            models.Pattern.get_json_all(),
            {
                "text": _("Multimedia"),
                "type": "multimedia-container",
                "children": [
                    models.FramesetGranule.get_tree_json_all()
                ],
                "li_attr": {
                    "class": "capitalized container"
                }
            }
        ],
        "li_attr": {
            "class": "capitalized container"
        }
    }


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
    context = {'error_message': ""}

    try:
        instruction = get_instruction_from_nodes(selected_nodes)
    except (IndexError, TypeError):
        context['error_message'] = _('No instruction was selected')
        return render(request, 'ontogen/result.html', context)

    patterns = get_patterns_from_nodes(selected_nodes)
    if not patterns:
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

    pattern_form_set = inlineformset_factory(
        models.Pattern,
        models.Mapping,
        fields=('mapping_label', 'mapping_value'), extra=extra_forms)

    if request.method == 'POST':
        form = forms.PatternForm(request.POST, instance=pattern)
        if form.is_valid():
            formset = pattern_form_set(
                request.POST, request.FILES, instance=pattern)
            if formset.is_valid():
                form.save()
                formset.save()
                return ok_response(request)
        else:
            formset = pattern_form_set(request.POST, request.FILES)
    else:
        if pattern_id:
            pattern = get_object_or_404(models.Pattern, pk=pattern_id)
        else:
            pattern = models.Pattern()
        form = forms.PatternForm(instance=pattern)
        formset = pattern_form_set(instance=pattern)

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

    patterns = get_patterns_from_ids(pattern_ids)
    subject = OntologyGenerator.generate_subject_ontology(text, patterns)

    ont_tag = request.user.username + "_" + dateformat.format(datetime.datetime.now(), 'H.i.s.u')
    subject.tag = ont_tag

    response = SimplyFireClient.post('files/createDirectory', {
        'name': ont_tag
    }, {
        'path': 'resources/images/ont/'
    })

    subject_nodes = []
    for node in subject.nodes:
        if node['name'] != constants.NO_NAME_NODE:
            continue

        out_relations = Ontology.relations_as_dict(subject.out_relations(node))
        name_node = subject.node_by_id(out_relations[constants.NAME_RELATION]['destination_node_id'])
        number_node = subject.node_by_id(out_relations[constants.NUMBER_RELATION]['destination_node_id'])

        subject_nodes.append({
            'name': name_node['name'],
            'number': number_node['name']
        })

    if not response.ok:
        return HttpResponse(status=500)

    return JsonResponse({
        'status': 'OK',
        'result': subject.to_json_string(),
        'subject_nodes': subject_nodes
    })


@csrf_exempt
@ajax_login_only
def generate_task_ont(request):
    try:
        text = request.POST['text']
        patterns = get_patterns_from_ids(request.POST.getlist('patterns[]'))
        subject = request.POST['subject']
    except KeyError:
        return JsonResponse({
            'status': 'FAIL',
            'error': 'Invalid POST arguments given.'
        })

    task, subject, task_nodes = OntologyGenerator.generate_task_ontology(text, patterns, subject)

    return JsonResponse({
        'status': 'OK',
        'result': {
            'applied': 'applied',
            'subject': subject.to_json_string(),
            'task': task.to_json_string(),
            'task_nodes': task_nodes
        }
    })


def django_response(response):
    return HttpResponse(
        content=response.content,
        status=response.status_code,
        content_type=response.headers['Content-Type']
    )


def get_file_from_repository(file_id):
    return django_response(SimplyFireClient.get_file(file_id))


def get_image(request, image_id):
    return get_file_from_repository(image_id)


@csrf_exempt
@ajax_login_only
def post_upload_image(request):
    image_format, image_str = request.POST['image'].split(';base64,')
    ext = image_format.split('/')[-1]

    data = ContentFile(base64.b64decode(image_str), name='temp.' + ext)

    response = SimplyFireClient.post_files('files/upload', {'File': data.file}, {'path': 'resources/images/'})

    return JsonResponse(response.json())


def upload_client_image(image, ont_tag):
    image_format, image_str = image.split(';base64,')
    ext = image_format.split('/')[-1]

    file_name = '{0}.{1}'.format(str(uuid.uuid4()), ext)

    data = ContentFile(base64.b64decode(image_str), name=file_name)
    path = 'resources/images/ont/{}/'.format(ont_tag)
    response = SimplyFireClient.post_files('files/upload', {'File': data}, {'path': path})

    if not response.ok:
        return ""

    return "/ontogen/resources/images/{}/".format(response.json()['response']['id'])


@csrf_exempt
@ajax_login_only
def populate_subject_with_image(request):
    subject_ont = request.POST['subject']
    node_name = request.POST['node']
    image = request.POST['image']

    subject_json = json.loads(subject_ont)
    image_url = upload_client_image(image, subject_json['tag'])

    subject = OntologyBuilder.populate_with_image(subject_ont, node_name, image_url)

    return JsonResponse({
        'status': 'OK',
        'result': {
            'subject': subject.to_json_string(),
        }
    })


def get_frameset(request, frameset_id):
    frameset = get_object_or_404(models.FramesetGranule, pk=frameset_id)
    return JsonResponse(frameset.to_json())


def create_terminal_frameset(name, files):
    path = SimplyFireClient.create_directory(name, 'resources/framesets/')

    frameset = models.FramesetGranule(name=name, type=models.AbstractGranule.TERMINAL_TYPE)
    frameset.first_frame = files[0].name
    frameset.last_frame = files[-1].name
    frameset.save()

    for file in files:
        file_id = SimplyFireClient.upload_file(file, path)
        file_item = models.GranuleItem(url='resources/framesets/frame/{}'.format(file_id), granule=frameset)
        file_item.save()

    return frameset.id


def add_frameset_view(request):
    errors = []

    if request.method == 'POST':
        files = request.FILES.getlist('files')
        name = request.POST.get('name', default='')
        name = name.strip()

        if len(name) == 0:
            errors.append('Не указано имя')

        if len(files) == 0:
            errors.append('Файлы не выбраны')

        if len(errors) == 0:
            try:
                create_terminal_frameset(name, files)
            except SimplyFireError:
                errors.append('Не удалось загрузить файлы')
            else:
                return ok_response(request)

        return JsonResponse({
            'errors': errors
        })

    return render(request, 'ontogen/frameset_create.html')


class FramesetDeleteView(edit.DeleteView):
    model = models.FramesetGranule
    success_url = reverse_lazy('ontogen:ok')


class FramesetDetailView(detail.DetailView):
    model = models.FramesetGranule


def get_frameset_frame(request, frame_id):
    return get_file_from_repository(frame_id)


def get_framesets(request):
    framesets = models.FramesetGranule.objects.all()

    return JsonResponse({
        'framesets': [x.get_tree_json() for x in framesets]
    })


@csrf_exempt
def populate_task_with_method(request):
    task_ont = request.POST['task']
    step_index = request.POST['step_index']

    method = request.POST['method']
    resource = request.POST['resource']

    task = OntologyBuilder.populate_task_with_method(task_ont, step_index, method, resource)

    return JsonResponse({
        'status': 'OK',
        'result': {
            'task': task.to_json_string(),
        }
    })

