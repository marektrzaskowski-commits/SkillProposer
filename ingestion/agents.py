import os
from django.conf import settings
from candidates.agents.SkillExtractionAgent import SkillExtractionAgent
from candidates.models import Candidate
from ingestion.models import Document
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings


class DocumentProcessingAgent:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
             chunk_size=1000, 
             chunk_overlap=200,
             length_function=len,
             is_separator_regex=True)
        
        self.embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

        self.vectorstore = Chroma(embedding_function=self.embeddings, persist_directory="./chroma_db")
        os.makedirs("./chroma_db", exist_ok=True)
        self.vectorstore.persist()

        self.skill_extraction_agent = SkillExtractionAgent()

        pass

    def process_document(self, document_id: int): 
        """Główna metoda do przetwarzania dokumentu."""

        try:
            document = Document.objects.get(id=document_id)    
            file_path = document.file.path
            print(f"Start processing document: {document.file.name}")

            extracted_document = self._read_document_with_langchain(file_path)

            if (extracted_document is None or extracted_document.strip() == ""):
                raise ValueError("UnstructuredFileLoader nie zwrócił żadnej treści.")

            text_chunks = self.text_splitter.split_text(extracted_document)

            metadatas = [{"document_id": document.id, "source": document.file.name} for _ in text_chunks]
            
            self.vectorstore.add_texts(texts=text_chunks, metadatas=metadatas)
            self.vectorstore.persist()

            document.extracted_text= extracted_document
            document.processing_status = 'processed'
                
            extracted_skills = self.skill_extraction_agent.extract_skills(extracted_document)
            
            if(extracted_skills):
                candidate, created = Candidate.objects.update_or_create(
                    document=document, 
                    defaults={"name": document.file.name, 
                              "skills": ",".join(extracted_skills)})
                print(f"Skills extracted from document {document.file.name}: {extracted_skills}")
            else:
                print(f"No skills extracted from document {document.file.name}.")        

            document.processed_by_agent = True
            document.save()
            print(f"Document {document.file.name} processed successfully.")        
            
            return extracted_document
        except Document.DoesNotExist:
            print(f"Dokument o ID {document_id} nie został znaleziony.")
            return None
        except Exception as e:   
            print(f"Wystąpił błąd podczas przetwarzania dokumentu o ID {document_id}: {e}")
            doc_to_fail = Document.objects.filter(id=document_id).first()
            if doc_to_fail:
                doc_to_fail.processing_status = 'failed'
                doc_to_fail.save()
            return None
    
    def _read_document_with_langchain(self, file_path: str):
        """
        Prywatna metoda do odczytywania zawartości pliku w zależności od jego typu.
        Na razie będzie to prosta implementacja dla tekstu i docx.
        Rozbudujemy to o obsługę PDF, Markdown, JSON itp.
       """
        try:
            loader = UnstructuredFileLoader(file_path)
            loaded_documents = loader.load()

            if not loaded_documents:
                print("Ostrzeżenie: Loader nie zwrócił żadnych dokumentów.")
                return None
   
            # Łączymy treść wszystkich załadowanych części w jeden tekst
            full_content = "\n\n".join([doc.page_content for doc in loaded_documents])       
            
            return full_content
        except Exception as e:
            print(f"Błąd podczas odczytywania dokumentu {file_path} za pomocą UnstructuredFileLoader: {e}")
            return None
    
        