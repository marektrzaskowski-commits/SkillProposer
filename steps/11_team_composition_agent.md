### **Krok 11: Agent do Proponowania Składu Zespołu (Team Composition Agent)**

W tym kroku stworzymy trzeciego, najbardziej zaawansowanego agenta. Jego zadaniem będzie przyjmowanie zapytania o potrzebne umiejętności, znajdowanie pasujących kandydatów w naszej bazie, a następnie generowanie propozycji składu zespołu wraz z uzasadnieniem.

**Co masz zrobić:**

1.  **Zaimplementuj `TeamCompositionAgent` w `candidates/agents.py`:**
    *   Otwórz plik `candidates/agents.py` i dodaj nową klasę agenta. Będzie ona miała podobną strukturę do `SkillExtractionAgent`, ale z inną logiką i promptem.
    *   Dodaj poniższy kod na końcu pliku `candidates/agents.py`:

    ```python
    # candidates/agents.py
    # ... (istniejące importy i kod)

    # Nowy agent
    class TeamCompositionAgent:
        def __init__(self):
            # Inicjalizacja LLM (tak jak w poprzednim agencie)
            try:
                self.llm = ChatOpenAI(model="gpt-4o", temperature=0.5) # Dajemy modelowi trochę więcej kreatywności
                print("TeamCompositionAgent: Używam modelu ChatOpenAI.")
            except Exception:
                print("TeamCompositionAgent: Brak konfiguracji OpenAI. Przełączam na ChatOllama.")
                self.llm = ChatOllama(model="llama3", temperature=0.5)
            
            # Inicjalizacja bazy wektorowej do wyszukiwania kandydatów
            try:
                embeddings = OllamaEmbeddings(model="llama2")
            except Exception:
                embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
            
            self.vector_store = Chroma(embedding_function=embeddings, persist_directory="./chroma_db")
            print("TeamCompositionAgent: ChromaDB połączona.")

        def propose_team(self, required_skills_query: str) -> str:
            """

            Główna metoda do tworzenia propozycji zespołu.
            """
            try:
                print(f"Rozpoczynanie tworzenia propozycji zespołu dla: '{required_skills_query}'")

                # 1. WYSZUKAJ KANDYDATÓW W BAZIE WEKTOROWEJ
                retrieved_docs = self.vector_store.similarity_search(required_skills_query, k=10) # Szukamy 10 najlepszych fragmentów

                # 2. ZBIERZ UNIKALNYCH KANDYDATÓW Z BAZY DANYCH DJANGO
                unique_document_ids = {doc.metadata['document_id'] for doc in retrieved_docs if 'document_id' in doc.metadata}
                
                if not unique_document_ids:
                    return "Nie znaleziono żadnych kandydatów pasujących do podanych umiejętności."

                top_candidates = Candidate.objects.filter(document__id__in=list(unique_document_ids))

                # 3. PRZYGOTUJ KONTEKST DLA LLM
                candidates_context = "
".join(
                    [f"- Kandydat: {c.name}, Umiejętności: {c.skills}" for c in top_candidates]
                )

                # 4. STWÓRZ PROMPT
                prompt = ChatPromptTemplate.from_messages([
                    ("system", "Jesteś doświadczonym managerem projektu i liderem zespołu. Twoim zadaniem jest stworzenie propozycji składu zespołu na podstawie listy wymaganych umiejętności i dostępnych kandydatów."),
                    ("human", 
                     "Potrzebuję zbudować zespół, który będzie posiadał następujące kluczowe umiejętności: **{required_skills}**.

"
                     "Przeanalizuj poniższą listę dostępnych kandydatów i ich umiejętności:
"
                     "**Dostępni kandydaci:**
{candidates_list}

"
                     "Zaproponuj optymalny skład zespołu, który pokryje wszystkie wymagane umiejętności. Krótko uzasadnij, dlaczego wybrałeś każdego z kandydatów i jaką rolę mógłby pełnić w zespole. Jeśli jacyś kandydaci się nie nadają, zignoruj ich. Przedstaw propozycję w klarowny i czytelny sposób.")
                ])

                # 5. UTWÓRZ I URUCHOM ŁAŃCUCH (CHAIN)
                chain = prompt | self.llm
                response = chain.invoke({
                    "required_skills": required_skills_query,
                    "candidates_list": candidates_context
                })

                return response.content

            except Exception as e:
                print(f"Wystąpił błąd podczas tworzenia propozycji zespołu: {e}")
                return "Wystąpił nieoczekiwany błąd podczas generowania propozycji zespołu."
    ```

2.  **Stwórz nowy widok i formularz do obsługi tego agenta:**
    *   Otwórz plik `candidates/forms.py` i dodaj nowy formularz:

    ```python
    # candidates/forms.py
    # ... (istniejący kod)

    class TeamCompositionForm(forms.Form):
        required_skills = forms.CharField(
            label='Wymagane umiejętności dla zespołu (np. Python, analityk danych, zarządzanie projektem)',
            widget=forms.Textarea(attrs={'rows': 3}),
            max_length=500
        )
    ```
    *   Otwórz plik `candidates/views.py` i dodaj nowy widok:

    ```python
    # candidates/views.py
    # ... (istniejący kod)
    from .forms import TeamCompositionForm # Dodaj import
    from .agents import TeamCompositionAgent # Dodaj import

    def propose_team_view(request):
        form = TeamCompositionForm(request.POST or None)
        proposal = ""

        if form.is_valid():
            required_skills = form.cleaned_data['required_skills']
            agent = TeamCompositionAgent()
            proposal = agent.propose_team(required_skills)
        
        return render(request, 'candidates/propose_team.html', {'form': form, 'proposal': proposal})
    ```

3.  **Dodaj URL do nowego widoku:**
    *   Zaktualizuj `candidates/urls.py`, dodając nową ścieżkę:

    ```python
    # candidates/urls.py
    # ... (istniejący kod)

    urlpatterns = [
        path('search/', views.search_candidates, name='search'),
        path('propose-team/', views.propose_team_view, name='propose_team'), # <-- DODAJ TĘ LINIĘ
    ]
    ```

4.  **Stwórz szablon HTML:**
    *   W folderze `candidates/templates/candidates` utwórz nowy plik `propose_team.html`:

    ```html
    <!-- candidates/templates/candidates/propose_team.html -->
    <!DOCTYPE html>
    <html>
    <head>
        <title>Zaproponuj Skład Zespołu</title>
        <style>
            body { font-family: sans-serif; line-height: 1.6; }
            .proposal { background-color: #f0f8ff; border-left: 5px solid #007bff; padding: 15px; margin-top: 20px; white-space: pre-wrap; }
        </style>
    </head>
    <body>
        <h1>Zaproponuj Skład Zespołu</h1>

        <form method="post">
            {% csrf_token %}
            {{ form.as_p }}
            <button type="submit">Generuj Propozycję</button>
        </form>

        {% if proposal %}
            <hr>
            <h2>Propozycja Zespołu:</h2>
            <div class="proposal">
                {{ proposal }}
            </div>
        {% endif %}

        <hr>
        <p><a href="{% url 'candidates:search' %}">Wyszukaj pojedynczych kandydatów</a></p>
        <p><a href="{% url 'ingestion:upload' %}">Prześlij nowy dokument CV</a></p>
    </body>
    </html>
    ```

---