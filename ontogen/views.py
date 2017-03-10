from django.shortcuts import render

from .core import OntologyGenerator

# Create your views here.
def index(request):
    return render(request, 'ontogen/index.html', {})

def generate_ont(request):
    text = request.POST['_text']
    ontology = OntologyGenerator.generate_ontology_from_text(text)
    return render(request, 'ontogen/result.html', {'ontology' : ontology})
