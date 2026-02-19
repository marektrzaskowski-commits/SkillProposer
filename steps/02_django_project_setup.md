### **Krok 2: Inicjalizacja projektu i aplikacji Django**

Teraz, gdy środowisko jest gotowe, stworzymy szkielet naszego projektu Django. Django ma wbudowane narzędzia, które generują potrzebne pliki i foldery, co znacznie przyspiesza start.

**Co masz zrobić:**

1.  **Utwórz projekt Django:**
    *   W terminalu, z aktywnym środowiskiem wirtualnym, upewnij się, że jesteś w głównym katalogu (`C:\Sources\SkillProposer`).
    *   Uruchom komendę, która stworzy projekt o nazwie `core`. Użycie `.` na końcu jest ważne, ponieważ mówi Django, aby utworzył projekt w bieżącym katalogu, a nie w nowym podkatalogu:
        ```bash
        django-admin startproject core .
        ```
    *   Po wykonaniu tej komendy powinieneś zobaczyć nowy folder `core` i plik `manage.py` w głównym katalogu projektu.

2.  **Utwórz aplikacje Django:**
    *   Django dzieli większe projekty na mniejsze "aplikacje". Zgodnie z `Assumptions.md`, będziemy potrzebować co najmniej dwóch głównych aplikacji: jednej do obsługi procesu przyjmowania i przetwarzania dokumentów (`ingestion`) i drugiej do zarządzania danymi kandydatów (`candidates`).
    *   Uruchom następujące komendy, aby je utworzyć:
        ```bash
        python manage.py startapp ingestion
        python manage.py startapp candidates
        ```
    *   Zobaczysz nowe foldery: `ingestion` i `candidates`.

3.  **Zarejestruj nowe aplikacje:**
    *   Każda nowo utworzona aplikacja musi być "zarejestrowana" w projekcie, aby Django o niej wiedział.
    *   Otwórz plik `core/settings.py`.
    *   Znajdź listę o nazwie `INSTALLED_APPS`.
    *   Dodaj nazwy swoich nowych aplikacji na końcu tej listy:
        ```python
        INSTALLED_APPS = [
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            # Twoje nowe aplikacje
            'ingestion',
            'candidates',
        ]
        ```

4.  **Uruchom serwer deweloperski:**
    *   Aby upewnić się, że wszystko działa, uruchom wbudowany w Django serwer deweloperski.
    *   Wykonaj komendę:
        ```bash
        python manage.py runserver
        ```
    *   Jeśli nie widzisz żadnych błędów, otwórz przeglądarkę i wejdź na adres `http://127.0.0.1:8000/`. Powinieneś zobaczyć stronę powitalną Django.
