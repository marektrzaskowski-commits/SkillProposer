from django.shortcuts import redirect, render
from django.urls import reverse
from regex import D

from ingestion.agents import DocumentProcessingAgent
from ingestion.forms import DocumentUploadForm
from ingestion.models import Document


def upload_document(request):

    print("Ingestion views loaded")
    
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid(): 
            upload_document = form.cleaned_data['file']
            documentEntity = Document.objects.create(file=upload_document)

            agent = DocumentProcessingAgent()
            agent.process_document(documentEntity.id)

            return redirect(reverse('ingestion:upload_success', args=[documentEntity.id]))
    else:
        form = DocumentUploadForm()
    
    return render(request, 'ingestion/upload.html', {'form': form})

def upload_success(request, document_id):
    document = Document.objects.get(id=document_id)
    return render(request, 'ingestion/upload_success.html', {'document': document})
