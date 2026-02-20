### **Krok 14: Automatyczne Zarządzanie Bootstrapem za pomocą NPM i Django-Compressor**

W tym kroku zautomatyzujemy proces dodawania i aktualizowania Bootstrapa w naszym projekcie. Użyjemy `npm` do zarządzania pakietami front-endowymi i `django-compressor` do ich integracji z szablonami Django. To eliminuje potrzebę ręcznego pobierania plików i ułatwia przyszłe aktualizacje.

**Co masz zrobić:**

1.  **Zainicjuj NPM w projekcie:**
    *   Upewnij się, że masz zainstalowany Node.js i npm (zazwyczaj instalują się razem). Możesz to sprawdzić, wpisując w terminalu `npm -v`.
    *   W głównym katalogu projektu (tam, gdzie jest `manage.py`), uruchom komendę:
        ```bash
        npm init -y
        ```
    *   Ta komenda utworzy plik `package.json`, który będzie śledził nasze zależności front-endowe.

2.  **Zainstaluj Bootstrap za pomocą NPM:**
    *   Teraz, gdy masz już plik `package.json`, możesz zainstalować Bootstrap jak każdy inny pakiet Node.js:
        ```bash
        npm install bootstrap
        ```
    *   Ta komenda pobierze najnowszą wersję Bootstrapa i umieści ją w nowo utworzonym folderze `node_modules`. Folder ten zawiera wszystkie nasze pakiety front-endowe.

3.  **Zaktualizuj `.gitignore`:**
    *   Folder `node_modules` może być bardzo duży i nie powinien być częścią repozytorium Git. Otwórz plik `.gitignore` i dodaj na jego końcu nową linię:
        ```
        /node_modules
        ```

4.  **Zainstaluj i skonfiguruj `django-compressor`:**
    *   `django-compressor` to biblioteka, która potrafi odnaleźć pliki CSS/JS (nawet w `node_modules`), połączyć je w jeden plik i wstawić do szablonu.
    *   Dodaj `django-compressor` do pliku `requirements.txt`.
        ```txt
        # ... (poprzednie zależności)
        django-compressor
        ```
    *   Zainstaluj go:
        ```bash
        pip install -r requirements.txt
        ```
    *   Teraz skonfiguruj go w `core/settings.py`:
        *   Dodaj `'compressor'` do `INSTALLED_APPS`.
        *   Dodaj `compressor.finders.CompressorFinder` do `STATICFILES_FINDERS`. To kluczowy krok, który pozwala compressorowi odnajdywać pliki statyczne.
        *   Włącz `COMPRESS_ENABLED`.

    Otwórz `core/settings.py` i dodaj/zmodyfikuj:
    ```python
    INSTALLED_APPS = [
        # ...
        'django.contrib.staticfiles',
        'compressor', # Dodaj compressor
        'ingestion',
        'candidates',
    ]

    # ...

    STATIC_URL = '/static/'
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

    # Konfiguracja Django-Compressor
    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        'compressor.finders.CompressorFinder',
    )
    COMPRESS_ENABLED = True
    ```

5.  **Zaktualizuj szablon bazowy (`base.html`):**
    *   Teraz, zamiast bezpośrednio linkować pliki, użyjemy tagów `{% compress %}`. `django-compressor` automatycznie znajdzie pliki w `node_modules`.
    *   **Usuń folder `static`**, który stworzyliśmy w poprzednim kroku, aby uniknąć pomyłek. Nie jest już potrzebny do przechowywania Bootstrapa.
    *   Otwórz `core/templates/core/base.html` i zmodyfikuj go:

    ```html
    {% load static compressor %}
    <!doctype html>
    <html lang="pl">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{% block title %}SkillProposer{% endblock %}</title>
        
        {% compress css %}
        <link rel="stylesheet" type="text/css" href="node_modules/bootstrap/dist/css/bootstrap.min.css">
        {% endcompress %}

        <style>
            body { padding-top: 5rem; }
        </style>
    </head>
    <body>
        <!-- ... reszta nawigacji bez zmian ... -->
        <main class="container">
            <div class="bg-light p-5 rounded">
                {% block content %}{% endblock %}
            </div>
        </main>
        
        {% compress js %}
        <script src="node_modules/bootstrap/dist/js/bootstrap.bundle.min.js"></script>
        {% endcompress %}
    </body>
    </html>
    ```
    *   **Co się tu stało?**
        *   Załadowaliśmy `compressor` obok `static`.
        *   Otoczyliśmy tagi `<link>` i `<script>` w bloki `{% compress css %}` i `{% compress js %}`.
        *   Wskazaliśmy bezpośrednią ścieżkę do plików wewnątrz `node_modules`. `django-compressor` jest na tyle inteligentny, że potrafi je tam znaleźć.

6.  **Uruchom `collectstatic` (ważne!):**
    *   `django-compressor` tworzy skompresowane, połączone pliki w locie. Aby to zadziałało poprawnie, szczególnie na produkcji, musisz uruchomić komendę `collectstatic`.
    *   W terminalu wykonaj:
        ```bash
        python manage.py collectstatic --noinput
        ```
    *   Ta komenda zbierze wszystkie potrzebne pliki i przetworzy je, umieszczając wynik w folderze zdefiniowanym w `STATIC_ROOT` (`staticfiles`).

7.  **Uruchom serwer i zweryfikuj:**
    *   `python manage.py runserver`
    *   Otwórz aplikację. Powinna wyglądać i działać tak samo.
    *   W źródle strony zobaczysz teraz linki do skompresowanych plików, np. `<link rel="stylesheet" href="/static/CACHE/css/output.e0b21c38e454.css" type="text/css">`. To dowód na to, że `django-compressor` działa!
