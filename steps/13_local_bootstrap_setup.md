### **Krok 13: Serwowanie plików Bootstrapa lokalnie (Zarządzanie plikami statycznymi)**

W tym kroku pobierzemy pliki CSS i JavaScript Bootstrapa, umieścimy je w naszym projekcie i skonfigurujemy Django tak, aby serwował je samodzielnie, zamiast pobierać je z internetu (CDN) przy każdym załadowaniu strony.

**Co masz zrobić:**

1.  **Pobierz pliki Bootstrapa:**
    *   Przejdź na oficjalną stronę Bootstrapa: [https://getbootstrap.com/](https://getbootstrap.com/)
    *   Znajdź sekcję "Download" i pobierz "Compiled CSS and JS".
    *   Rozpakuj pobrane archiwum. W środku znajdziesz foldery `css` i `js`.

2.  **Stwórz folder na pliki statyczne w projekcie:**
    *   W głównym katalogu projektu (na tym samym poziomie co `manage.py`), utwórz nowy folder o nazwie `static`.
    *   Wewnątrz folderu `static` utwórz dwa podfoldery: `css` i `js`.
    *   Skopiuj plik `bootstrap.min.css` z rozpakowanego archiwum do folderu `static/css`.
    *   Skopiuj plik `bootstrap.bundle.min.js` (jest ważny, bo zawiera też Popper.js) do folderu `static/js`.

    Twoja struktura folderów powinna wyglądać tak:
    ```
    SkillProposer/
    ├── static/
    │   ├── css/
    │   │   └── bootstrap.min.css
    │   └── js/
    │       └── bootstrap.bundle.min.js
    ├── core/
    ├── ingestion/
    ├── candidates/
    └── manage.py
    ```

3.  **Skonfiguruj Django do obsługi plików statycznych:**
    *   Otwórz plik `core/settings.py`.
    *   Na końcu pliku dodaj lub zmodyfikuj następujące zmienne:
        *   `STATIC_URL`: Powinna już istnieć, upewnij się, że ma wartość `'/static/'`.
        *   `STATICFILES_DIRS`: To jest najważniejsza zmiana. Mówi ona Django, gdzie (oprócz folderów `static` wewnątrz aplikacji) ma szukać plików statycznych podczas developmentu.
        *   `STATIC_ROOT`: To ustawienie jest używane na produkcji. Definiuje folder, do którego Django zbierze *wszystkie* pliki statyczne z całego projektu za pomocą komendy `collectstatic`.

    Dodaj na końcu `core/settings.py` (upewnij się, że masz `import os` na górze pliku):
    ```python
    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/5.0/howto/static-files/

    STATIC_URL = '/static/'

    # Folder, w którym Django będzie szukał dodatkowych plików statycznych (nasz folder `static`)
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'static'),
    ]

    # Folder, do którego `collectstatic` zbierze wszystkie pliki na produkcję
    # Ważne: nie powinien być taki sam jak folder w STATICFILES_DIRS
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    ```

4.  **Zaktualizuj szablon bazowy (`base.html`):**
    *   Teraz musimy zamienić linki do CDN na linki do naszych lokalnych plików. Użyjemy do tego tagu szablonu `{% static %}`.
    *   Otwórz plik `core/templates/core/base.html`.
    *   Na samej górze pliku, zaraz pod `<!doctype html>`, dodaj `{% load static %}`.
    *   Zamień linki do CSS i JS:

    **Zmień to:**
    ```html
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    ```
    **Na to:**
    ```html
    <link href="{% static 'css/bootstrap.min.css' %}" rel="stylesheet">
    ```

    **I zmień to:**
    ```html
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    ```
    **Na to:**
    ```html
    <script src="{% static 'js/bootstrap.bundle.min.js' %}"></script>
    ```
    *   Cały plik `base.html` powinien wyglądać mniej więcej tak:
    ```html
    {% load static %}
    <!doctype html>
    <html lang="pl">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{% block title %}SkillProposer{% endblock %}</title>
        <link href="{% static 'css/bootstrap.min.css' %}" rel="stylesheet">
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
        <script src="{% static 'js/bootstrap.bundle.min.js' %}"></script>
    </body>
    </html>
    ```

5.  **Uruchom serwer i zweryfikuj:**
    *   Uruchom serwer deweloperski: `python manage.py runserver`
    *   Otwórz aplikację w przeglądarce. Powinna wyglądać dokładnie tak samo.
    *   Aby się upewnić, że pliki są serwowane lokalnie, kliknij prawym przyciskiem myszy na stronie i wybierz "Wyświetl źródło strony" lub "Zbadaj element". W źródle strony powinieneś zobaczyć ścieżki takie jak `/static/css/bootstrap.min.css`, a nie `https://cdn.jsdelivr.net/...`.
