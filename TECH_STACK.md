# Stos technologiczny projektu

Poniżej znajduje się proponowany i używany w projekcie zestaw technologii. Dostosuj według potrzeb.

## Języki programowania
- Python (zalecane 3.8+, preferowane 3.11+)

## Biblioteki i pakiety
- google-generativeai (jeśli używane do modeli generatywnych)
- requests (HTTP klient)
- inne zależności wymienione w `requirements.txt`

## Frameworki i narzędzia
- Visual Studio Code (IDE)
- Git (kontrola wersji)
- virtualenv / venv (izolacja środowiska)
- pip (zarządzanie pakietami)

## Baza danych
- Brak domyślnej bazy w projekcie (można użyć SQLite dla prostoty lub PostgreSQL dla produkcji)

## Konteneryzacja i wdrożenie
- Docker (opcjonalnie do uruchamiania w kontenerach)
- GitHub Actions / inny CI (opcjonalnie do testów i deploya)

## System operacyjny
- Rozwój: Windows (zalecane Powershell / WSL dla zgodności)

## Uruchamianie lokalne (przykład)
1. Utwórz i aktywuj środowisko wirtualne:

   - Windows (Powershell):
     ```powershell
     python -m venv .venv
     .\\.venv\\Scripts\\Activate.ps1
     ```

2. Zainstaluj zależności:

   ```powershell
   pip install -r requirements.txt
   ```

3. Uruchom aplikację zgodnie z dokumentacją projektu.

---
Jeśli chcesz, mogę dopasować ten plik dokładnie do faktycznych zależności projektu (przeanalizować `requirements.txt` lub pliki źródłowe) i zaktualizować listę.
