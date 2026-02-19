### **Krok 1: Konfiguracja środowiska i instalacja zależności**

Twoim pierwszym zadaniem jest stworzenie izolowanego środowiska dla projektu i zainstalowanie w nim wszystkich niezbędnych bibliotek. To zapewni, że nasz projekt będzie miał własne, niezależne zależności, co zapobiega konfliktom z innymi projektami w Pythonie.

**Co masz zrobić:**

1.  **Utwórz i aktywuj wirtualne środowisko:**
    *   Otwórz terminal w głównym folderze projektu (`C:\Sources\SkillProposer`).
    *   Jeśli jeszcze nie masz wirtualnego środowiska, utwórz je komendą: `python -m venv venv`
    *   Aktywuj je. W systemie Windows użyj komendy: `.\venv\Scripts\activate`
    *   Po aktywacji, nazwa środowiska (`venv`) powinna pojawić się na początku wiersza poleceń.

2.  **Zainstaluj podstawowe biblioteki:**
    *   Upewnij się, że twoje środowisko jest aktywne.
    *   Zainstaluj Django, LangChain i LangGraph za pomocą `pip`. Dobrą praktyką jest dodanie ich od razu do pliku `requirements.txt`. Otwórz plik `requirements.txt` i upewnij się, że zawiera poniższe linie (dodaj je, jeśli ich brakuje):

    ```txt
    django
    langchain
    langgraph
    python-dotenv
    ```

    *   Następnie uruchom instalację z pliku, aby mieć pewność, że wszystko jest zainstalowane: `pip install -r requirements.txt`