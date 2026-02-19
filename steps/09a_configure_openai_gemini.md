### **Krok 9a: Konfiguracja alternatywnych modeli LLM (OpenAI lub Gemini)**

W tym kroku zmodyfikujemy naszego `SkillExtractionAgent`, aby mógł korzystać z modeli OpenAI (np. GPT-3.5, GPT-4) lub Google (Gemini) zamiast lokalnej instancji Ollama. Użyjemy do tego zmiennych środowiskowych, co jest najlepszą praktyką do zarządzania kluczami API i konfiguracją.

**Co masz zrobić:**

1.  **Zdobądź klucze API:**
    *   **OpenAI:** Zaloguj się na swoje konto na [platform.openai.com](https://platform.openai.com/) i wygeneruj klucz API.
    *   **Google (Gemini):** Zaloguj się do [Google AI Studio](https://aistudio.google.com/) i wygeneruj swój klucz API.

2.  **Skonfiguruj zmienne środowiskowe (plik `.env`):**
    *   W głównym katalogu projektu (`C:\Sources\SkillProposer`), utwórz plik o nazwie `.env` (jeśli jeszcze go nie masz).
    *   Dodaj do niego poniższe zmienne. Wklej swoje klucze API i wybierz dostawcę, z którego chcesz korzystać.

    ```dotenv
    # .env

    # Wybierz dostawcę LLM: "openai", "gemini", lub "ollama"
    LLM_PROVIDER="openai" 

    # Wklej swoje klucze API poniżej
    OPENAI_API_KEY="sk-..."
    GOOGLE_API_KEY="AIzaSy..."
    ```
    *   **Ważne:** Upewnij się, że plik `.env` jest dodany do Twojego pliku `.gitignore`, aby przypadkowo nie wysłać swoich kluczy do publicznego repozytorium!

3.  **Zaktualizuj `requirements.txt` o nowe biblioteki:**
    *   Musimy dodać oficjalne pakiety LangChain do obsługi OpenAI i Google.
    *   Otwórz plik `requirements.txt` i dodaj `langchain-openai` oraz `langchain-google-genai`:

    ```txt
    # ... (istniejące pakiety)
    pydantic
    langchain-openai  # <-- Dodaj to
    langchain-google-genai # <-- Dodaj to
    ```
    *   Zainstaluj nowe zależności:
        ```bash
        pip install -r requirements.txt
        ```

4.  **Zmodyfikuj agenta `candidates/agents.py`:**
    *   Zaktualizujemy konstruktor (`__init__`) agenta, aby na podstawie zmiennej `LLM_PROVIDER` wybierał i konfigurował odpowiedni model.

    ```python
    # candidates/agents.py
    import os
    from dotenv import load_dotenv
    from typing import List
    from langchain_core.pydantic_v1 import BaseModel, Field
    from langchain_core.prompts import ChatPromptTemplate
    # Importy dla różnych modeli
    from langchain_community.chat_models import ChatOllama
    from langchain_openai import ChatOpenAI
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.chains import create_extraction_chain

    # Wczytaj zmienne środowiskowe z pliku .env
    load_dotenv()

    # ... (definicja klasy SkillSet i promptu pozostaje bez zmian) ...
    class SkillSet(BaseModel):
        skills: List[str] = Field(description="A comprehensive list of skills from the CV.")

    prompt_template = "Extract all skills from the CV text:

{text}"
    prompt = ChatPromptTemplate.from_template(prompt_template)


    class SkillExtractionAgent:
        def __init__(self):
            provider = os.getenv("LLM_PROVIDER", "ollama").lower()
            
            print(f"Inicjalizacja agenta z dostawcą LLM: {provider}")

            if provider == "openai":
                # Użyj modelu od OpenAI
                self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
            elif provider == "gemini":
                # Użyj modelu od Google (Gemini)
                self.llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)
            else:
                # Domyślnie użyj Ollama
                self.llm = ChatOllama(model="llama2", temperature=0)

            # Reszta logiki pozostaje taka sama
            self.extraction_chain = create_extraction_chain(
                schema=SkillSet.model_json_schema,
                llm=self.llm,
                prompt=prompt,
            )

        def extract_skills(self, text: str) -> List[str]:
            # ... (ta metoda pozostaje bez zmian) ...
            try:
                result = self.extraction_chain.invoke({"text": text})
                if result and 'text' in result and result['text']:
                    extracted_skills = result['text'][0].get('skills', [])
                    print(f"Wyodrębniono {len(extracted_skills)} umiejętności: {extracted_skills}")
                    return extracted_skills
                return []
            except Exception as e:
                print(f"Błąd podczas ekstrakcji umiejętności: {e}")
                return []
    ```

5.  **Przetestuj przełączanie:**
    *   Uruchom aplikację z `LLM_PROVIDER="openai"` w pliku `.env`. Powinieneś zobaczyć w logach "Inicjalizacja agenta z dostawcą LLM: openai".
    *   Zatrzymaj serwer, zmień w `.env` na `LLM_PROVIDER="gemini"`, uruchom ponownie i sprawdź, czy logi się zgadzają.
