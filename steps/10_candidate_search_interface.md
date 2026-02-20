### **Krok 10: Interfejs Wyszukiwania Kandydatów po Umiejętnościach (Candidate Search Interface)**

Ten krok ma na celu stworzenie prostego interfejsu webowego, który pozwoli użytkownikom (działowi HR) wprowadzić zapytanie o umiejętności, a następnie wyszukać w bazie wektorowej kandydatów posiadających te umiejętności.

**Co masz zrobić:**

1.  **Stwórz formularz wyszukiwania w `candidates/forms.py`:**
    *   W aplikacji `candidates`, utwórz nowy plik o nazwie `candidates/forms.py`.
    *   Dodaj prosty formularz Django do wprowadzania zapytania o umiejętności:

    ```python
    # candidates/forms.py
    from django import forms

    class SkillSearchForm(forms.Form):
        query = forms.CharField(label='Wymagane umiejętności (np. Python, Django, Cloud)', max_length=255)
    ```

2.  **Stwórz widok do wyszukiwania w `candidates/views.py`:**
    *   Otwórz plik `candidates/views.py`.
    *   Zaimplementuj widok `search_candidates`, który będzie renderował formularz, obsługiwał zapytania, wykonywał wyszukiwanie w ChromaDB i wyświetlał wyniki.

    ```python
    # candidates/views.py
    from django.shortcuts import render
    from .forms import SkillSearchForm
    from .models import Candidate
    from ingestion.models import Document # Potrzebne, aby odzyskać pełny dokument, jeśli jest to konieczne

    # Importy z LangChain do obsługi wyszukiwania
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import SentenceTransformerEmbeddings, OllamaEmbeddings

    # Inicjalizacja modelu embeddings i bazy wektorowej (analogicznie do SkillExtractionAgent)
    # Możesz zrefaktoryzować to do wspólnego modułu konfiguracyjnego w przyszłości
    try:
        embeddings_model = OllamaEmbeddings(model="llama2")
        print("Search View: Używam OllamaEmbeddings.")
    except Exception:
        print("Search View: Ollama nie jest dostępna. Używam SentenceTransformerEmbeddings.")
        embeddings_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    vector_store_search = Chroma(embedding_function=embeddings_model, persist_directory="./chroma_db")


    def search_candidates(request):
        form = SkillSearchForm(request.GET or None)
        results = []

        if form.is_valid():
            query = form.cleaned_data['query']
            print(f"Wyszukiwanie kandydatów dla zapytania: '{query}'")

            # Wykonaj wyszukiwanie w bazie wektorowej
            # top_k to liczba najlepszych wyników, które chcemy uzyskać
            retrieved_documents = vector_store_search.similarity_search(query, k=5) 
            
            # retrieved_documents to lista obiektów LangChain Document.
            # Musimy je połączyć z naszymi modelami Django Candidate.
            unique_document_ids = set()
            for doc_lc in retrieved_documents:
                # Metadane powinny zawierać 'document_id' z modelu Django
                if 'document_id' in doc_lc.metadata:
                    unique_document_ids.add(doc_lc.metadata['document_id'])

            # Pobierz kandydatów na podstawie unikalnych ID dokumentów
            if unique_document_ids:
                candidates_from_db = Candidate.objects.filter(document__id__in=list(unique_document_ids)).distinct()
                results = list(candidates_from_db) # Konwertuj QuerySet na listę

            print(f"Znaleziono {len(results)} kandydatów dla zapytania.")

        return render(request, 'candidates/search.html', {'form': form, 'candidates': results})
    ```

3.  **Zaktualizuj `candidates/urls.py`:**
    *   Dodaj ścieżkę do naszego nowego widoku wyszukiwania.
    *   Otwórz `candidates/urls.py` i zaktualizuj go:

    ```python
    # candidates/urls.py
    from django.urls import path
    from . import views

    app_name = 'candidates'

    urlpatterns = [
        path('search/', views.search_candidates, name='search'),
        # Tutaj w przyszłości dodamy widoki, np. do listowania kandydatów.
    ]
    ```

4.  **Stwórz szablon HTML do wyszukiwania:**
    *   W folderze `candidates/templates/candidates` stwórz plik `search.html`.
    *   Dodaj prosty szablon, który wyświetli formularz i wyniki:

    ```html
    <!-- candidates/templates/candidates/search.html -->
    <!DOCTYPE html>
    <html>
    <head>
        <title>Wyszukaj Kandydatów</title>
    </head>
    <body>
        <h1>Wyszukaj Kandydatów po Umiejętnościach</h1>

        <form method="get">
            {% csrf_token %}
            {{ form.as_p }}
            <button type="submit">Szukaj</button>
        </form>

        <hr>

        <h2>Wyniki wyszukiwania:</h2>
        {% if candidates %}
            <ul>
                {% for candidate in candidates %}
                    <li>
                        <strong>{{ candidate.name|default:"Brak imienia" }}</strong> ({{ candidate.email|default:"Brak e-maila" }})<br>
                        Umiejętności: {{ candidate.skills|default:"Brak umiejętności" }}<br>
                        <small>Źródło dokumentu: {{ candidate.document.file.name }}</small>
                    </li>
                {% endfor %}
            </ul>
        {% else %}
            <p>Brak kandydatów spełniających kryteria lub brak przesłanych dokumentów.</p>
        {% endif %}

        <p><a href="{% url 'ingestion:upload' %}">Prześlij nowy dokument CV</a></p>
    </body>
    </html>
    ```

5.  **Uruchom serwer deweloperski i przetestuj:**
    *   Upewnij się, że Twoje wirtualne środowisko jest aktywne.
    *   Uruchom serwer Django: `python manage.py runserver`
    *   Otwórz przeglądarkę i przejdź do `http://127.0.0.1:8000/candidates/search/`.
    *   Wprowadź umiejętności, które powinny znajdować się w przesłanych wcześniej CV.
