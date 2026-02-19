### **Krok 8: Widok do przesyłania dokumentów w Django (Document Upload View)**

W tym kroku stworzymy prosty formularz w Django, który pozwoli użytkownikom przesyłać pliki CV. Następnie zaimplementujemy widok (view), który obsłuży ten formularz, zapisze plik w bazie danych i zainicjuje proces przetwarzania przez naszego `DocumentProcessingAgent`.

**Co masz zrobić:**

1.  **Stwórz formularz do uploadu w `ingestion/forms.py`:**
    *   W aplikacji `ingestion`, utwórz nowy plik o nazwie `ingestion/forms.py`.
    *   Dodaj prosty formularz Django do przesyłania plików:

    ```python
    # ingestion/forms.py
    from django import forms

    class DocumentUploadForm(forms.Form):
        file = forms.FileField(label='Wybierz plik CV')
    ```

2.  **Stwórz widok w `ingestion/views.py`:**
    *   Otwórz plik `ingestion/views.py`.
    *   Zaimplementuj widok `upload_document`, który będzie renderował formularz i obsługiwał jego przesłanie. Po pomyślnym przesłaniu, widok zapisze dokument w bazie danych i zainicjuje naszego agenta.

    ```python
    # ingestion/views.py
    from django.shortcuts import render, redirect
    from django.urls import reverse
    from .forms import DocumentUploadForm
    from .models import Document
    from .agents import DocumentProcessingAgent # Import naszego agenta

    def upload_document(request):
        if request.method == 'POST':
            form = DocumentUploadForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file = form.cleaned_data['file']
                document = Document.objects.create(file=uploaded_file)
                
                # --- TUTAJ URUCHAMIAMY NASZEGO AGENTA ---
                # UWAGA: Na razie agent jest uruchamiany synchronicznie. 
                # W prawdziwej aplikacji, to powinno być zadanie asynchroniczne (np. Celery, RQ),
                # aby nie blokować serwera webowego.
                agent = DocumentProcessingAgent()
                agent.process_document(document.id)
                # ----------------------------------------

                return redirect(reverse('ingestion:upload_success', args=[document.id]))
        else:
            form = DocumentUploadForm()
        return render(request, 'ingestion/upload.html', {'form': form})

    def upload_success(request, document_id):
        # Prosty widok potwierdzający upload
        document = Document.objects.get(id=document_id)
        return render(request, 'ingestion/upload_success.html', {'document': document})
    ```

3.  **Zaktualizuj `ingestion/urls.py`:**
    *   Musimy dodać ścieżki (URLs) do naszych nowych widoków.
    *   Otwórz `ingestion/urls.py` i zaktualizuj go:

    ```python
    # ingestion/urls.py
    from django.urls import path
    from . import views

    app_name = 'ingestion'

    urlpatterns = [
        path('upload/', views.upload_document, name='upload'),
        path('upload/success/<int:document_id>/', views.upload_success, name='upload_success'),
    ]
    ```

4.  **Stwórz szablony HTML:**
    *   W folderze `ingestion`, utwórz nowy folder o nazwie `templates`.
    *   Wewnątrz `templates`, utwórz kolejny folder o nazwie `ingestion`.
    *   W folderze `ingestion/templates/ingestion` stwórz dwa pliki:
        *   `upload.html` (formularz do przesyłania):

        ```html
        <!-- ingestion/templates/ingestion/upload.html -->
        <!DOCTYPE html>
        <html>
        <head>
            <title>Prześlij CV</title>
        </head>
        <body>
            <h1>Prześlij plik CV</h1>
            <form method="post" enctype="multipart/form-data">
                {% csrf_token %}
                {{ form.as_p }}
                <button type="submit">Prześlij</button>
            </form>
        </body>
        </html>
        ```
        *   `upload_success.html` (strona potwierdzenia):

        ```html
        <!-- ingestion/templates/ingestion/upload_success.html -->
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sukces</title>
        </head>
        <body>
            <h1>Plik przesłany pomyślnie!</h1>
            <p>Dokument "{{ document.file.name }}" (ID: {{ document.id }}) został pomyślnie wgrany i rozpoczęto jego przetwarzanie.</p>
            <p><a href="{% url 'ingestion:upload' %}">Prześlij kolejny plik</a></p>
        </body>
        </html>
        ```

5.  **Uruchom serwer deweloperski i przetestuj:**
    *   Upewnij się, że Twoje wirtualne środowisko jest aktywne.
    *   Uruchom serwer Django: `python manage.py runserver`
    *   Otwórz przeglądarkę i przejdź do `http://127.0.0.1:8000/ingestion/upload/`.
    *   Spróbuj przesłać plik (np. prosty plik `.txt` lub `.docx`). Sprawdź logi w terminalu, aby zobaczyć komunikaty z agenta.
