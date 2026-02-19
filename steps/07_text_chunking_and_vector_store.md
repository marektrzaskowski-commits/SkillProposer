### **Krok 7: Dzielenie tekstu na fragmenty (Text Chunking) i Inicjalizacja Vector Store**

Po wczytaniu całej treści dokumentu, jest ona zazwyczaj zbyt długa, aby przekazać ją bezpośrednio do modelu językowego. Dlatego dzielimy ją na mniejsze, "gryzalne" fragmenty (chunks). Te fragmenty zostaną następnie przekształcone w reprezentacje numeryczne (wektory/embeddings) i zapisane w bazie wektorowej, która umożliwi nam szybkie wyszukiwanie odpowiednich fragmentów podczas generowania odpowiedzi (mechanizm RAG).

Zgodnie ze specyfikacją, jako bazę wektorową użyjemy Chroma lub FAISS. Wybierzmy ChromaDB jako domyślną opcję, ponieważ jest łatwa w użyciu i dobrze integruje się z LangChain. Potrzebujemy również modelu embeddings (osadzania), który przekształci tekst w wektory. Użyjemy `OllamaEmbeddings`, jeśli masz uruchomionego lokalnie Ollama, lub `SentenceTransformersEmbeddings` jako fallback (co wymaga instalacji dodatkowej biblioteki i pobrania modelu).

**Co masz zrobić:**

1.  **Zaktualizuj `requirements.txt`:**
    *   Dodaj biblioteki potrzebne do dzielenia tekstu, generowania embeddings i obsługi ChromaDB.
    *   Otwórz plik `requirements.txt` i dodaj/zaktualizuj następujące linie:

    ```txt
    django
    langchain
    langchain-community
    langchain-text-splitters # Zgodnie z poprzednią poprawką
    langgraph
    python-dotenv
    unstructured[docx,pdf,md,json]
    python-magic-bin
    chromadb
    sentence-transformers
    ```

2.  **Zainstaluj nowe zależności:**
    *   W terminalu z aktywnym środowiskiem wirtualnym, uruchom ponownie instalację z pliku `requirements.txt`:
        ```bash
        pip install -r requirements.txt
        ```

3.  **Zaktualizuj `ingestion/agents.py` o Text Splitter i Vector Store:**
    *   Zmodyfikujemy klasę `DocumentProcessingAgent`, aby po ekstrakcji tekstu, dzieliła go na fragmenty i dodawała do bazy wektorowej.
    *   Będziemy potrzebować też prostego modelu `embeddings` do przekształcania tekstu na wektory.
    *   Otwórz plik `ingestion/agents.py` i zaktualizuj go:

    ```python
    # ingestion/agents.py
    import os
    from django.conf import settings
    from ingestion.models import Document
    from langchain_community.document_loaders import UnstructuredFileLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter # Poprawiony import
    from langchain_community.vectorstores import Chroma
    # Wybór modelu embeddings (jeden z dwóch poniżej, lub inny, jeśli masz preferencje)
    from langchain_community.embeddings import OllamaEmbeddings # Jeśli używasz Ollama
    # from langchain_community.embeddings import SentenceTransformerEmbeddings # Alternatywa dla Ollama

    class DocumentProcessingAgent:
        def __init__(self):
            # Inicjalizacja Text Splittera
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,       # Wielkość fragmentu (np. 1000 znaków)
                chunk_overlap=200,     # Ile znaków ma się nakładać między fragmentami
                length_function=len,
                is_separator_regex=False,
            )

            # Inicjalizacja modelu embeddings
            # Wybierz jeden z nich lub dostosuj do swoich potrzeb
            try:
                # Spróbuj użyć Ollama, jeśli jest dostępny (wymaga uruchomionego Ollama z modelem)
                self.embeddings = OllamaEmbeddings(model="llama2") # Użyj swojego modelu Ollama
                print("Używam OllamaEmbeddings.")
            except Exception:
                # Fallback do SentenceTransformers (wymaga ściągnięcia modelu, np. all-MiniLM-L6-v2)
                # Pamiętaj, aby pobrać model, np. SentenceTransformer('all-MiniLM-L6-v2')
                # lub pozwolić LangChain to zrobić przy pierwszym użyciu
                print("Ollama nie jest dostępna lub skonfigurowana. Używam SentenceTransformerEmbeddings (może pobierać model).")
                self.embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

            # Inicjalizacja ChromaDB (na razie w pamięci/lokalnie)
            # W bardziej zaawansowanej wersji możesz chcieć użyć Django-Chroma lub podobnego rozwiązania
            self.vector_store = Chroma(embedding_function=self.embeddings, persist_directory="./chroma_db")
            # Utwórz folder do przechowywania danych ChromaDB
            os.makedirs("./chroma_db", exist_ok=True)
            self.vector_store.persist()
            print("ChromaDB zainicjalizowana.")


        def process_document(self, document_id: int):
            """
            Główna metoda do przetwarzania dokumentu.
            """
            try:
                document = Document.objects.get(id=document_id)
                print(f"Rozpoczynanie przetwarzania dokumentu: {document.file.name}")

                # 1. Wczytaj dokument
                extracted_text = self._read_document_with_langchain(document.file.path)

                if extracted_text is None or not extracted_text.strip():
                    raise ValueError("Brak treści do przetworzenia po ekstrakcji.")

                # 2. Podziel tekst na fragmenty
                # LangChain DocumentLoaders zwracają listę obiektów Document (z LangChain),
                # więc musimy je najpierw przekształcić w listę tekstów
                text_chunks = self.text_splitter.split_text(extracted_text)
                print(f"Podzielono dokument na {len(text_chunks)} fragmentów.")

                # 3. Dodaj fragmenty do bazy wektorowej
                # Możemy dodać metadane, np. ID dokumentu Django, aby później łatwiej powiązać
                metadatas = [{"document_id": document.id, "source": document.file.name} for _ in text_chunks]
                self.vector_store.add_texts(texts=text_chunks, metadatas=metadatas)
                self.vector_store.persist() # Zapisz zmiany w ChromaDB
                print(f"Fragmenty dokumentu {document.file.name} dodane do ChromaDB.")

                document.extracted_text = extracted_text
                document.processing_status = 'processed'
                document.processed_by_agent = True
                document.save()

                print(f"Dokument {document.file.name} przetworzony pomyślnie.")
                return extracted_text

            except Document.DoesNotExist:
                print(f"Dokument o ID {document_id} nie został znaleziony.")
                return None
            except Exception as e:
                print(f"Błąd podczas przetwarzania dokumentu {document_id}: {e}")
                doc_to_fail = Document.objects.filter(id=document_id).first()
                if doc_to_fail:
                    doc_to_fail.processing_status = 'failed'
                    doc_to_fail.save()
                return None

        def _read_document_with_langchain(self, file_path: str) -> str | None:
            """
            Wczytuje zawartość pliku przy użyciu UnstructuredFileLoader.
            Zwraca połączoną treść wszystkich stron/części dokumentu.
            """
            print(f"Wczytywanie pliku za pomocą UnstructuredFileLoader: {file_path}")
            try:
                loader = UnstructuredFileLoader(file_path)
                loaded_documents = loader.load()

                if not loaded_documents:
                    print("Ostrzeżenie: Loader nie zwrócił żadnych dokumentów.")
                    return None

                full_content = "

".join([doc.page_content for doc in loaded_documents])
                return full_content

            except Exception as e:
                print(f"Błąd w UnstructuredFileLoader dla pliku {os.path.basename(file_path)}: {e}")
                return None
    ```