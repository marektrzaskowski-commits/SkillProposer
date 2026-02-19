### **Krok 9: Agent Ekstrakcji Umiejętności (Skill Extraction Agent)**

Teraz, gdy mamy tekst z CV, musimy "zrozumieć" jego treść. W tym kroku stworzymy nowego agenta, którego jedynym zadaniem będzie analiza tekstu i wyodrębnienie z niego listy umiejętności, technologii i narzędzi. Użyjemy do tego mechanizmu "extraction chains" z LangChain, który pozwala na uzyskanie ustrukturyzowanych danych wyjściowych (np. JSON) z modelu LLM.

**Co masz zrobić:**

1.  **Zaktualizuj `requirements.txt` o Pydantic:**
    *   Aby zdefiniować strukturę danych, której oczekujemy od LLM, użyjemy biblioteki Pydantic.
    *   Otwórz plik `requirements.txt` i dodaj `pydantic`:
    ```txt
    # ... (istniejące pakiety)
    pydantic
    ```
    *   Zainstaluj nową zależność:
        ```bash
        pip install -r requirements.txt
        ```

2.  **Stwórz plik dla nowego agenta w `candidates/agents.py`:**
    *   W aplikacji `candidates`, utwórz nowy plik `candidates/agents.py`. To tutaj będzie mieszkać logika związana z analizą kandydatów.

3.  **Zdefiniuj agenta ekstrakcji umiejętności w `candidates/agents.py`:**
    *   W nowym pliku zdefiniuj klasę `SkillExtractionAgent`. Będzie ona zawierać:
        *   Model Pydantic opisujący strukturę wyjściową (lista umiejętności).
        *   Inicjalizację modelu językowego (użyjemy `ChatOllama`, tak jak w poprzednim kroku).
        *   Prompt, który instruuje LLM, co dokładnie ma zrobić.
        *   Łańcuch ekstrakcji (extraction chain) z LangChain.

    ```python
    # candidates/agents.py
    from typing import List
    from langchain_core.pydantic_v1 import BaseModel, Field
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_community.chat_models import ChatOllama
    from langchain.chains import create_extraction_chain

    # 1. Zdefiniuj strukturę danych wyjściowych za pomocą Pydantic
    class SkillSet(BaseModel):
        """A set of skills extracted from a CV."""
        skills: List[str] = Field(
            description="A list of all technical skills, soft skills, tools, and technologies found in the CV text."
        )

    # Szablon promptu
    prompt_template = """
    You are an expert HR technical recruiter. Your task is to extract all relevant skills from the provided CV text.
    Focus on technical skills (e.g., Python, Django, React), software (e.g., Jira, Git), methodologies (e.g., Agile, Scrum),
    and soft skills (e.g., communication, teamwork).
    
    Return a comprehensive list of these skills.

    CV Text:
    {text}
    """
    prompt = ChatPromptTemplate.from_template(prompt_template)

    class SkillExtractionAgent:
        def __init__(self):
            # Użyj tego samego modelu co w agencie przetwarzania dokumentów
            self.llm = ChatOllama(model="llama2", temperature=0) # Temperatura 0 dla determinizmu

            # 2. Stwórz łańcuch ekstrakcji
            self.extraction_chain = create_extraction_chain(
                schema=SkillSet.model_json_schema, # Użyj schematu z Pydantic
                llm=self.llm,
                prompt=prompt,
            )

        def extract_skills(self, text: str) -> List[str]:
            """
            Uruchamia łańcuch ekstrakcji na podanym tekście i zwraca listę umiejętności.
            """
            try:
                result = self.extraction_chain.invoke({"text": text})
                # Wynik jest listą słowników, musimy wyciągnąć dane
                if result and 'text' in result and result['text']:
                    extracted_skills = result['text'][0].get('skills', [])
                    print(f"Wyodrębniono {len(extracted_skills)} umiejętności: {extracted_skills}")
                    return extracted_skills
                return []
            except Exception as e:
                print(f"Błąd podczas ekstrakcji umiejętności: {e}")
                return []

    ```

4.  **Zintegruj nowego agenta z istniejącym procesem:**
    *   Musimy teraz wywołać naszego nowego agenta zaraz po tym, jak `DocumentProcessingAgent` wyodrębni tekst z CV.
    *   Otwórz plik `ingestion/agents.py` i zmodyfikuj metodę `process_document`.

    ```python
    # ingestion/agents.py
    # ... (istniejące importy)
    from candidates.agents import SkillExtractionAgent # Import nowego agenta
    from candidates.models import Candidate # Import modelu Candidate

    class DocumentProcessingAgent:
        def __init__(self):
            # ... (istniejący kod __init__)
            # Inicjalizuj drugiego agenta od razu
            self.skill_extractor = SkillExtractionAgent()

        def process_document(self, document_id: int):
            try:
                document = Document.objects.get(id=document_id)
                print(f"Rozpoczynanie przetwarzania dokumentu: {document.file.name}")

                # 1. Wczytaj i podziel tekst (jak wcześniej)
                extracted_text = self._read_document_with_langchain(document.file.path)
                if extracted_text is None or not extracted_text.strip():
                    raise ValueError("Brak treści do przetworzenia po ekstrakcji.")
                
                text_chunks = self.text_splitter.split_text(extracted_text)
                metadatas = [{"document_id": document.id, "source": document.file.name} for _ in text_chunks]
                self.vector_store.add_texts(texts=text_chunks, metadatas=metadatas)
                self.vector_store.persist()
                
                document.extracted_text = extracted_text
                document.processing_status = 'processed'
                document.save() # Zapisz dokument przed ekstrakcją umiejętności

                # 2. Uruchom ekstrakcję umiejętności
                print("Uruchamianie agenta ekstrakcji umiejętności...")
                extracted_skills = self.skill_extractor.extract_skills(extracted_text)

                # 3. Zapisz wyniki w modelu Candidate
                if extracted_skills:
                    # Stwórz lub zaktualizuj profil kandydata
                    candidate, created = Candidate.objects.update_or_create(
                        document=document,
                        defaults={'skills': ", ".join(extracted_skills)} # Zapisujemy jako string oddzielony przecinkami
                    )
                    print(f"Zapisano umiejętności dla kandydata powiązanego z dokumentem ID: {document.id}")

                document.processed_by_agent = True # Finalny status
                document.save()
                
                print(f"Dokument {document.file.name} przetworzony w pełni.")
                return extracted_text

            except Exception as e:
                # ... (istniejąca obsługa błędów)
                print(f"Błąd podczas przetwarzania dokumentu {document_id}: {e}")
                doc_to_fail = Document.objects.filter(id=document_id).first()
                if doc_to_fail:
                    doc_to_fail.processing_status = 'failed'
                    doc_to_fail.save()
                return None
            # ... (reszta metody)
    ```

5.  **Przetestuj ponownie:**
    *   Uruchom serwer Django: `python manage.py runserver`.
    *   Przejdź do formularza `http://127.0.0.1:8000/ingestion/upload/`.
    *   Prześlij przykładowe CV (plik `.txt`, `.docx` lub `.pdf` zawierający listę technologii, np. "Skills: Python, Django, JavaScript, React, SQL").
    *   Obserwuj logi w konsoli. Powinieneś zobaczyć komunikaty o ekstrakcji i zapisie umiejętności. Możesz też sprawdzić bazę danych (np. przez `python manage.py shell`), aby zobaczyć, czy obiekt `Candidate` został poprawnie utworzony i wypełniony.

---

Ten krok to serce naszego systemu. Po jego wykonaniu aplikacja nie tylko przechowuje dokumenty, ale zaczyna je rozumieć, wyciągając z nich konkretne, użyteczne informacje. To fundament pod przyszłe funkcje wyszukiwania i budowania zespołów.

Daj znać, jak poszło i czy wyniki ekstrakcji są zadowalające!

---

#### **Dodatkowe wyjaśnienie: Czym jest `create_extraction_chain`?**

W skrócie: **`create_extraction_chain` to specjalistyczne narzędzie LangChain, które zmusza model językowy (LLM) do zwracania odpowiedzi w ściśle określonym, ustrukturyzowanym formacie (najczęściej JSON), zamiast zwykłego, swobodnego tekstu.**

#### Analogia: "Magiczny formularz"

Wyobraź sobie, że dajesz pracownikowi (modelowi LLM) długi, nieuporządkowany dokument (CV) i mówisz mu: "Przeczytaj to i wypisz mi wszystkie umiejętności".

*   **Bez `create_extraction_chain`:** Pracownik może wrócić z odpowiedzią w różnych formach:
    *   "Umiejętności tej osoby to: Python, Django i SQL."
    *   "Znalazłem następujące kompetencje: Python, Django, SQL."
    *   "Oto lista: \n1. Python\n2. Django\n3. SQL"
    Taki tekst jest trudny do przetworzenia przez maszynę. Musiałbyś pisać skomplikowane reguły, aby "wyciągnąć" z tego czystą listę.

*   **Z `create_extraction_chain`:** Dajesz pracownikowi ten sam dokument, ale razem z nim wręczasz mu **precyzyjny formularz do wypełnienia** (nasz schemat Pydantic). Mówisz mu: "Przeczytaj dokument i wpisz wszystkie znalezione umiejętności w to jedno pole formularza, które akceptuje tylko listę słów. Nic więcej."
    Pracownik jest **zmuszony** do zwrócenia idealnie wypełnionego formularza, który wygląda tak:
    ```json
    {
      "skills": ["Python", "Django", "SQL"]
    }
    ```
    Taki wynik jest trywialnie prosty do przetworzenia przez Twój program.

---

### **Jak to działa? Rozbicie na składniki**

Funkcja `create_extraction_chain` potrzebuje trzech głównych składników, które idealnie pasują do naszej analogii:

1.  **`llm` (Pracownik / Ekspert):**
    *   To jest model językowy (`ChatOllama`, `ChatOpenAI`, `ChatGoogleGenerativeAI`), który wykonuje pracę umysłową – czyta i rozumie tekst.

2.  **`schema` (Formularz / Reguły):**
    *   To jest serce mechanizmu. Definiujesz strukturę danych, której oczekujesz. W naszym kodzie zrobiliśmy to za pomocą klasy `SkillSet` z Pydantic:
        ```python
        class SkillSet(BaseModel):
            skills: List[str] = Field(...)
        ```
    *   Mówi to modelowi: "Twój ostateczny wynik **MUSI** być obiektem JSON z jednym kluczem o nazwie `skills`, a jego wartością **MUSI** być lista stringów". To nie jest sugestia, to jest warunek.

3.  **`prompt` (Instrukcje do formularza):**
    *   To jest polecenie, które dajesz pracownikowi. Mówi mu, **jak** ma wypełnić formularz, korzystając z dostarczonego tekstu.
        ```python
        prompt_template = """
        You are an expert HR technical recruiter. (...)
        CV Text:
        {text}
        """
        ```
    *   Ustawia kontekst ("Jesteś rekruterem") i wskazuje, gdzie wstawiony zostanie tekst do analizy (`{text}`).

### **Podsumowując**

Gdy wywołujesz `extraction_chain.invoke({"text": "jakiś tekst CV"})`, LangChain wykonuje za Ciebie następujące kroki:

1.  Bierze szablon `prompt` i wstawia w miejsce `{text}` treść CV.
2.  Bierze schemat `schema` i w tle dołącza do polecenia specjalne instrukcje dla LLM, mówiące mu o wymaganym formacie wyjściowym JSON.
3.  Wysyła to połączone, precyzyjne polecenie do `llm`.
4.  Odbiera od LLM odpowiedź, która jest już idealnie sformatowanym JSON-em.
5.  Automatycznie parsuje ten JSON i zwraca Ci gotowe, czyste dane (w naszym przypadku listę umiejętności).

Dzięki `create_extraction_chain` zadanie, które normalnie wymagałoby skomplikowanego parsowania i obsługi błędów, sprowadza się do zdefiniowania prostego modelu danych i jednego wywołania funkcji.