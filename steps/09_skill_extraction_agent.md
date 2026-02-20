### **Krok 9: Tworzenie Agenta Ekstrakcji Umiejętności (Skill Extraction Agent)**

Ten krok polega na stworzeniu agenta, który będzie komunikował się z modelem językowym (LLM), aby wyodrębnić ustrukturyzowane dane z surowego tekstu CV. Użyjemy do tego potężnej techniki LangChain, która pozwala na zdefiniowanie schematu wyjściowego (za pomocą Pydantic), co zmusza model do zwracania danych w spójnym formacie JSON.

**Co masz zrobić:**

1.  **Skonfiguruj dostęp do LLM (OpenAI lub Ollama):**
    *   Musimy poinformować LangChain, jakiego modelu LLM ma używać.
    *   **Stwórz plik `.env`** w głównym katalogu projektu (`C:\Sources\SkillProposer`). Plik ten będzie przechowywał klucze API i inne sekrety.
    *   Dodaj do niego swój klucz API OpenAI (jeśli go używasz):
        ```
        # .env
        OPENAI_API_KEY="sk-..."
        ```
    *   **Zaktualizuj `.gitignore`**, aby plik `.env` nie został przypadkowo wysłany do repozytorium git. Dodaj na końcu pliku `.gitignore` nową linię:
        ```
        .env
        ```
    *   Jeśli używasz **Ollama**, upewnij się, że jest uruchomiony z odpowiednim modelem (np. `llama3`, `mistral`). W kodzie poniżej użyjemy OpenAI jako domyślnego, z fallbackiem na Ollama.

2.  **Zaktualizuj `requirements.txt`:**
    *   Dodaj bibliotekę do obsługi modelu OpenAI.
    *   Otwórz plik `requirements.txt` i dodaj na końcu `langchain-openai`:
        ```txt
        # ... (poprzednie zależności)
        langchain-openai
        ```
    *   Zainstaluj nową zależność:
        ```bash
        pip install -r requirements.txt
        ```

3.  **Stwórz plik dla nowego agenta w `candidates/agents.py`:**
    *   W aplikacji `candidates`, utwórz nowy plik `candidates/agents.py`.

4.  **Zaimplementuj `SkillExtractionAgent`:**
    *   Wklej poniższy kod do `candidates/agents.py`. Dokładnie przeanalizuj komentarze, aby zrozumieć, co robi każda część kodu.

    ```python
    # candidates/agents.py
    import os
    from dotenv import load_dotenv
    from typing import List

    # Importy z Django
    from ingestion.models import Document
    from candidates.models import Candidate

    # Importy z LangChain i Pydantic
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.pydantic_v1 import BaseModel, Field
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import SentenceTransformerEmbeddings, OllamaEmbeddings
    from langchain_openai import ChatOpenAI
    from langchain_community.chat_models import ChatOllama

    # Załaduj zmienne środowiskowe (np. OPENAI_API_KEY) z pliku .env
    load_dotenv()

    # 1. DEFINICJA STRUKTURY DANYCH (PYDANTIC)
    # To jest schemat, który "zamówimy" u naszego LLM.
    class CandidateProfile(BaseModel):
        name: str = Field(description="Pełne imię i nazwisko kandydata")
        email: str = Field(description="Adres e-mail kandydata")
        skills: List[str] = Field(description="Lista kluczowych umiejętności i technologii wymienionych w CV")

    class SkillExtractionAgent:
        def __init__(self):
            # 2. INICJALIZACJA MODELU LLM
            # Próbujemy użyć OpenAI, a jeśli nie jest skonfigurowany, przełączamy na Ollama.
            try:
                # Używamy modelu GPT-4o dla najlepszych rezultatów. temp=0 dla determinizmu.
                self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
                print("Używam modelu ChatOpenAI.")
            except Exception:
                print("Brak konfiguracji OpenAI. Przełączam na ChatOllama.")
                self.llm = ChatOllama(model="llama3", temperature=0) # Użyj swojego modelu Ollama
            
            # Wskazujemy LLM, że ma używać naszego schematu Pydantic do zwracania odpowiedzi.
            self.structured_llm = self.llm.with_structured_output(CandidateProfile)

            # 3. INICJALIZACJA BAZY WEKTOROWEJ (TA SAMA CO W INGESTION)
            # Musimy mieć dostęp do tych samych danych, które przetworzył pierwszy agent.
            try:
                embeddings = OllamaEmbeddings(model="llama2")
            except Exception:
                embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
            
            self.vector_store = Chroma(embedding_function=embeddings, persist_directory="./chroma_db")
            print("SkillExtractionAgent: ChromaDB połączona.")

        def extract_skills_from_document(self, document_id: int):
            """
            Główna metoda do ekstrakcji danych z dokumentu.
            """
            try:
                document = Document.objects.get(id=document_id)
                print(f"Rozpoczynanie ekstrakcji umiejętności z dokumentu: {document.file.name}")

                # 4. TWORZENIE PROMPTU
                prompt = ChatPromptTemplate.from_messages([
                    ("system", "Jesteś ekspertem HR specjalizującym się w analizie CV. Twoim zadaniem jest przeanalizowanie podanego tekstu z CV kandydata i wyodrębnienie z niego kluczowych informacji."),
                    ("human", "Przeanalizuj poniższy tekst z CV i wyodrębnij imię i nazwisko kandydata, jego adres e-mail oraz listę jego najważniejszych umiejętności technicznych i miękkich.\n\nOto tekst z CV:\n```{context}```")
                ])

                # 5. RETRIEVAL (POBIERANIE KONTEKSTU Z BAZY WEKTOROWEJ)
                # Używamy całej treści dokumentu jako kontekstu dla ekstrakcji.
                context = document.extracted_text
                
                # 6. TWORZENIE I URUCHOMIENIE ŁAŃCUCHA (CHAIN)
                chain = prompt | self.structured_llm
                response_profile: CandidateProfile = chain.invoke({"context": context})

                # 7. ZAPIS DANYCH DO BAZY
                candidate, created = Candidate.objects.update_or_create(
                    document=document,
                    defaults={
                        'name': response_profile.name,
                        'email': response_profile.email,
                        'skills': ", ".join(response_profile.skills) # Zapisujemy listę jako string oddzielony przecinkami
                    }
                )

                if created:
                    print(f"Utworzono profil dla kandydata: {response_profile.name}")
                else:
                    print(f"Zaktualizowano profil dla kandydata: {response_profile.name}")

                return candidate

            except Document.DoesNotExist:
                print(f"Dokument o ID {document_id} nie został znaleziony w extract_skills.")
                return None
            except Exception as e:
                print(f"Wystąpił błąd podczas ekstrakcji umiejętności: {e}")
                return None

    ```

5.  **Zintegruj nowego agenta z widokiem `upload_document`:**
    *   Musimy zaktualizować nasz widok w `ingestion/views.py`, aby po zakończeniu pracy pierwszego agenta, uruchamiał drugiego.
    *   Otwórz `ingestion/views.py` i zmodyfikuj go:

    ```python
    # ingestion/views.py
    from django.shortcuts import render, redirect
    from django.urls import reverse
    from .forms import DocumentUploadForm
    from .models import Document
    from .agents import DocumentProcessingAgent
    from candidates.agents import SkillExtractionAgent # <-- IMPORTUJ NOWEGO AGENTA

    def upload_document(request):
        if request.method == 'POST':
            form = DocumentUploadForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file = form.cleaned_data['file']
                document = Document.objects.create(file=uploaded_file)
                
                # Uruchom agenta przetwarzania
                doc_processor = DocumentProcessingAgent()
                doc_processor.process_document(document.id)

                # Uruchom agenta ekstrakcji umiejętności
                skill_extractor = SkillExtractionAgent()
                skill_extractor.extract_skills_from_document(document.id)

                return redirect(reverse('ingestion:upload_success', args=[document.id]))
        else:
            form = DocumentUploadForm()
        return render(request, 'ingestion/upload.html', {'form': form})

    # ... reszta widoków bez zmian ...
    ```
