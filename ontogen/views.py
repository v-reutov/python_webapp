from django.shortcuts import render

from .core import OntologyGenerator
from .models import Pattern, Instruction

def index(request):
    return render(request, 'ontogen/index.html', {
        'instructions' : Instruction.objects.all(), #pylint: disable=E1101
        'patterns' : Pattern.objects.all()          #pylint: disable=E1101
    })

def generate_ont(request):
    selected_instruction_id = request.POST.get('instruction', None)
    selected_patterns = request.POST.getlist('patterns[]')
    context = {}

    if selected_instruction_id and selected_patterns:
        text = Instruction.objects.get(pk=selected_instruction_id).instruction_text #pylint: disable=E1101
        patterns = [Pattern.objects.get(pk=pattern_id) for pattern_id in selected_patterns] #pylint: disable=E1101
        context['ontology'] = OntologyGenerator.generate_ontology_from_text(text, patterns)
    else:
        if not selected_instruction_id:
            context['error_message'] = 'No instruction was selected'
        else:
            context['error_message'] = 'No patterns were selected'

    return render(request, 'ontogen/result.html', context)
