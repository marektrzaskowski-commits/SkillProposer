import logging
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
        self.logger = logging.getLogger(__name__)
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

        try:
            document = Document.objects.get(id=document_id)    
            file_path = document.file.path
            
            self.logger.info(f"Start processing document: {document.file.name}")

            extracted_document = self.read_document_content(file_path)

            if (extracted_document is None or extracted_document.strip() == ""):
                raise ValueError("UnstructuredFileLoader did not return any content.")

            text_chunks = self.text_splitter.split_text(extracted_document)

            extracted_skills = self.skill_extraction_agent.extract_skills(extracted_document)            

            document.extracted_text = extracted_document
            document.processing_status = 'processed'                
            
            if(extracted_skills):
                formatted_skills = ", ".join(extracted_skills)

                self.store_vectors(document, formatted_skills, text_chunks)    

                candidate, created = Candidate.objects.update_or_create(
                    document=document, 
                    defaults={"name": document.file.name, 
                              "skills": formatted_skills})
                
                self.logger.info(f"Skills extracted from document {document.file.name}: {extracted_skills}")
            else:
                self.logger.info(f"No skills extracted from document {document.file.name}.")        

            document.processed_by_agent = True
            document.save()
            self.logger.info(f"Document {document.file.name} processed successfully.")        
            
            return extracted_document
        except Document.DoesNotExist:
            self.logger.error(f"Document with ID {document_id} not found.")
            return None
        except Exception as e:   
            self.logger.error(f"Error while processing document with ID {document_id}: {e}")
            doc_to_fail = Document.objects.filter(id=document_id).first()
            if doc_to_fail:
                doc_to_fail.processing_status = 'failed'
                doc_to_fail.save()
            return None

    def store_vectors(self, document, skills, text_chunks):
        metadatas = [{"document_id": document.id, "source": document.file.name, "skills": skills} for _ in text_chunks]
            
        self.vectorstore.add_texts(texts=text_chunks, metadatas=metadatas)
        self.vectorstore.persist()
    
    def read_document_content(self, file_path: str):
     
        try:
            loader = UnstructuredFileLoader(file_path)
            loaded_documents = loader.load()

            if not loaded_documents:
                self.logger.warning("Loader did not return any documents.")
                return None
   
            # Combine the content of all loaded parts into a single text
            full_content = "\n\n".join([doc.page_content for doc in loaded_documents])       
            
            return full_content
        except Exception as e:
            self.logger.error(f"Error while reading document {file_path} with UnstructuredFileLoader: {e}")
            return None
    
        