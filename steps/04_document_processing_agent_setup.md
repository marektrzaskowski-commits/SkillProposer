### **Krok 4: Konfiguracja Agentu Przetwarzania Dokumentów (Document Processing Agent)**

Ten agent będzie odpowiedzialny za wstępne przetwarzanie dokumentów: odczytywanie ich zawartości, ekstrakcję tekstu i aktualizację statusu w bazie danych. Na tym etapie skupimy się na strukturze agenta i jego zdolności do odczytywania plików.

**Co masz zrobić:**

1.  **Stwórz plik agenta:**
    *   W aplikacji `ingestion`, utwórz nowy plik o nazwie `ingestion/agents.py`. Będzie to miejsce, gdzie będziemy definiować naszych agentów.

2.  **Dodaj podstawową klasę agenta w `ingestion/agents.py`:**
    *   W tym pliku zdefiniuj klasę `DocumentProcessingAgent`. Na początku będzie ona bardzo prosta. Będzie zawierała metody do inicjalizacji i podstawowego przetwarzania.

    ```python
    # ingestion/agents.py
    import os
    from django.conf import settings
    from ingestion.models import Document
    # Potencjalne importy dla LangChain/LangGraph - dodamy później
    # from langchain_core.documents import Document as LC_Document
    # from langchain.text_splitter import RecursiveCharacterTextSplitter
    # from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader

    class DocumentProcessingAgent:
        def __init__(self):
            # Tutaj będziemy inicjalizować modele językowe, narzędzia LangChain itp.
            # Na razie pusto
            pass

        def process_document(self, document_id: int):
            """
            Główna metoda do przetwarzania dokumentu.
            """
            try:
                document = Document.objects.get(id=document_id)
                file_path = document.file.path
                print(f"Rozpoczynanie przetwarzania dokumentu: {document.file.name}")

                # Tutaj dodamy logikę wczytywania i ekstrakcji tekstu z różnych formatów
                extracted_text = self._read_document_content(file_path)

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
                Document.objects.filter(id=document_id).update(processing_status='failed')
                return None

        def _read_document_content(self, file_path: str) -> str:
            """
            Prywatna metoda do odczytywania zawartości pliku w zależności od jego typu.
            Na razie będzie to prosta implementacja dla tekstu i docx.
            Rozbudujemy to o obsługę PDF, Markdown, JSON itp.
            """
            file_extension = os.path.splitext(file_path)[1].lower()
            content = ""

            if file_extension == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif file_extension == '.docx':
                # Tutaj będziemy potrzebować biblioteki typu python-docx
                # Na razie placeholder
                content = f"Tekst z pliku DOCX (placeholder): {os.path.basename(file_path)}"
                print(f"UWAGA: Obsługa .docx wymaga biblioteki python-docx. Zainstaluj ją i dodaj logikę do _read_document_content.")
            elif file_extension == '.pdf':
                # Tutaj będziemy potrzebować biblioteki typu pypdf, pypdfium2 lub innych
                # Na razie placeholder
                content = f"Tekst z pliku PDF (placeholder): {os.path.basename(file_path)}"
                print(f"UWAGA: Obsługa .pdf wymaga odpowiedniej biblioteki. Zainstaluj ją i dodaj logikę do _read_document_content.")
            else:
                print(f"Nieobsługiwany typ pliku: {file_extension}. Spróbuj wczytać jako zwykły tekst.")
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    content = f"Nie udało się odczytać pliku {os.path.basename(file_path)} z powodu błędu kodowania."
            return content

    ```

3.  **Dodaj potrzebne biblioteki do `requirements.txt`:**
    *   Zauważ, że w kodzie pojawiły się komentarze o potrzebie instalacji dodatkowych bibliotek, np. `python-docx` i `pypdf` (lub podobnych). Zaktualizuj plik `requirements.txt`, dodając je:
        ```txt
        django
        langchain
        langgraph
        python-dotenv
        python-docx # Do obsługi plików .docx
        pypdf # Do obsługi plików .pdf
        ```
    *   Następnie zainstaluj je w swoim wirtualnym środowisku:
        ```bash
        pip install -r requirements.txt
        ```
    *   **Ważne:** W systemie Windows, instalacja `pypdf` może wymagać zainstalowania Build Tools dla Visual Studio. Jeśli napotkasz błędy podczas instalacji, poszukaj informacji na temat instalacji `pypdf` (lub alternatywy takiej jak `pypdfium2`) dla Twojej platformy.

4.  **Skonfiguruj Django do obsługi plików (opcjonalnie, ale zalecane):**
    *   Aby Django mógł przechowywać wgrywane pliki, musisz zdefiniować `MEDIA_ROOT` i `MEDIA_URL` w `core/settings.py`.
    *   Dodaj te linie na końcu pliku `core/settings.py`:
        ```python
        # Media files (for user uploaded content)
        MEDIA_URL = '/media/'
        MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
        ```
    *   Upewnij się, że masz zaimportowany `os` na górze pliku `settings.py`: `import os` (powinien już tam być).
    *   Dodaj również konfigurację do `core/urls.py`, aby serwer deweloperski mógł obsługiwać pliki mediów:
        ```python
        # core/urls.py
        from django.contrib import admin
        from django.urls import path, include
        from django.conf import settings # Dodaj to
        from django.conf.urls.static import static # Dodaj to

        urlpatterns = [
            path('admin/', admin.site.urls),
            # path('ingestion/', include('ingestion.urls')), # Dodamy później
            # path('candidates/', include('candidates.urls')), # Dodamy później
        ]

        # Dodaj to tylko w trybie deweloperskim, aby serwować pliki mediów
        if settings.DEBUG:
            urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
        ```
