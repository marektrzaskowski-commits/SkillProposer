### **Krok 12: Integracja Bootstrap i Stworzenie Głównego Interfejsu Użytkownika**

W tym kroku ujednolicimy wygląd naszej aplikacji za pomocą popularnego frameworka CSS, Bootstrap. Stworzymy szablon bazowy, który będzie zawierał wspólną nawigację dla całej aplikacji, a następnie dostosujemy istniejące widoki, aby z niego korzystały. Stworzymy też nową stronę główną, która będzie listowała wszystkie wgrane dokumenty.

**Co masz zrobić:**

1.  **Stwórz szablon bazowy (`base.html`):**
    *   W folderze `core`, utwórz foldery `templates/core`, jeśli jeszcze nie istnieją.
    *   Wewnątrz `core/templates/core` stwórz plik `base.html` i wklej do niego poniższy kod. Ten szablon zawiera linki do Bootstrapa z CDN oraz definiuje strukturę nawigacji i główną treść strony.

    ```html
    <!-- core/templates/core/base.html -->
    <!doctype html>
    <html lang="pl">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{% block title %}SkillProposer{% endblock %}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { padding-top: 5rem; }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-md navbar-dark bg-dark fixed-top">
            <div class="container-fluid">
                <a class="navbar-brand" href="{% url 'ingestion:document_list' %}">SkillProposer</a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarsExampleDefault">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarsExampleDefault">
                    <ul class="navbar-nav me-auto mb-2 mb-md-0">
                        <li class="nav-item">
                            <a class="nav-link {% if request.resolver_match.url_name == 'document_list' %}active{% endif %}" href="{% url 'ingestion:document_list' %}">Lista CV</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link {% if request.resolver_match.url_name == 'upload' %}active{% endif %}" href="{% url 'ingestion:upload' %}">Wgraj CV</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link {% if request.resolver_match.url_name == 'propose_team' %}active{% endif %}" href="{% url 'candidates:propose_team' %}">Zaproponuj Zespół</a>
                        </li>
                         <li class="nav-item">
                            <a class="nav-link {% if request.resolver_match.url_name == 'search' %}active{% endif %}" href="{% url 'candidates:search' %}">Szukaj Kandydatów</a>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
        <main class="container">
            <div class="bg-light p-5 rounded">
                {% block content %}{% endblock %}
            </div>
        </main>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    ```

2.  **Stwórz widok i szablon dla strony głównej (Lista CV):**
    *   Otwórz `ingestion/views.py` i dodaj nowy widok `document_list`:

    ```python
    # ingestion/views.py
    # ... (istniejące importy)
    
    def document_list(request):
        documents = Document.objects.all().order_by('-uploaded_at')
        return render(request, 'ingestion/document_list.html', {'documents': documents})
    ```
    *   W `ingestion/templates/ingestion` stwórz nowy plik `document_list.html`:

    ```html
    <!-- ingestion/templates/ingestion/document_list.html -->
    {% extends "core/base.html" %}

    {% block title %}Lista CV - {{ block.super }}{% endblock %}

    {% block content %}
        <h1>Wszystkie przetworzone dokumenty CV</h1>
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Nazwa Pliku</th>
                    <th>Data Wgrania</th>
                    <th>Status Przetwarzania</th>
                </tr>
            </thead>
            <tbody>
                {% for doc in documents %}
                <tr>
                    <td>{{ doc.file.name }}</td>
                    <td>{{ doc.uploaded_at }}</td>
                    <td>
                        <span class="badge 
                            {% if doc.processing_status == 'processed' %}bg-success
                            {% elif doc.processing_status == 'failed' %}bg-danger
                            {% else %}bg-secondary{% endif %}">
                            {{ doc.get_processing_status_display }}
                        </span>
                    </td>
                </tr>
                {% empty %}
                <tr>
                    <td colspan="3">Brak wgranych dokumentów.</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    {% endblock %}
    ```

3.  **Zaktualizuj konfigurację URL:**
    *   Otwórz `ingestion/urls.py` i dodaj ścieżkę do nowego widoku listy:

    ```python
    # ingestion/urls.py
    urlpatterns = [
        path('', views.document_list, name='document_list'), # Strona główna
        path('upload/', views.upload_document, name='upload'),
        path('upload/success/<int:document_id>/', views.upload_success, name='upload_success'),
    ]
    ```
    *   Otwórz `core/urls.py` i upewnij się, że główna ścieżka (`''`) wskazuje na aplikację `ingestion`:

    ```python
    # core/urls.py
    urlpatterns = [
        path('admin/', admin.site.urls),
        path('', include('ingestion.urls')), # Główny punkt wejścia
        path('candidates/', include('candidates.urls')),
    ]
    ```

4.  **Zaktualizuj istniejące szablony, aby dziedziczyły z `base.html`:**
    *   Zmodyfikuj plik `ingestion/templates/ingestion/upload.html`:
        ```html
        {% extends "core/base.html" %}
        {% block title %}Wgraj CV - {{ block.super }}{% endblock %}
        {% block content %}
            <h1>Prześlij plik CV</h1>
            <form method="post" enctype="multipart/form-data">
                {% csrf_token %}
                <div class="mb-3">
                    {{ form.file.label_tag }}
                    {{ form.file }}
                </div>
                <button type="submit" class="btn btn-primary">Prześlij</button>
            </form>
        {% endblock %}
        ```
    *   Zrób to samo dla pozostałych szablonów (`upload_success.html`, `search.html`, `propose_team.html`), otaczając ich treść w `{% extends "core/base.html" %}` i `{% block content %}...{% endblock %}` oraz dodając klasy Bootstrapa dla lepszego wyglądu.

5.  **Uruchom serwer i przetestuj:**
    *   Uruchom serwer: `python manage.py runserver`
    *   Otwórz przeglądarkę pod adresem `http://127.0.0.1:8000/`. Powinieneś zobaczyć nową stronę główną z listą CV i nawigacją.
    *   Przeklikaj się przez wszystkie zakładki, aby upewnić się, że nawigacja działa i wszystkie strony mają spójny wygląd.
