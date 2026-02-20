import os
from pydoc import text
from typing import List
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from candidates.models import Candidate

load_dotenv()

class SkillSet(BaseModel):
    skills: List[str] = Field(..., description="List of skills extracted from the job description")

class SkillExtractionAgent:
    def __init__(self):
        provider = os.getenv("LLM_PROVIDER", "openai")
        
        if provider == "openai":
            self.llm = ChatOpenAI(
                model="gpt-3.5-turbo", 
                temperature=0, 
                api_key=os.getenv("OPENAI_API_KEY"))
        elif provider == "google":
            self.llm =  ChatGoogleGenerativeAI(
                model="gemini-pro", 
                temperature=0, 
                google_api_key=os.getenv("GOOGLE_API_KEY"))
        
        self.parser = JsonOutputParser(pydantic_object=SkillSet)    

        prompt_template = ChatPromptTemplate.from_template(
            "Extract all skills from the following job description. Return as JSON.\n"
            "{format_instructions}\n"
            "Job description: {text}"
        )

        self.extraction_chain = (
            prompt_template.partial(format_instructions=self.parser.get_format_instructions())
            | self.llm
            | self.parser
        )

    def extract_skills(self, job_description):
        try:
            result = self.extraction_chain.invoke({"text": job_description})
            # result is a dict with 'skills' key (from SkillSet model)
            if result and isinstance(result, dict) and 'skills' in result:
                extracted_skills = result['skills']
                print(f"Wyodrębniono {len(extracted_skills)} umiejętności: {extracted_skills}")
                return extracted_skills
            return []
        except Exception as e:
            print(f"Błąd podczas ekstrakcji umiejętności: {e}")
            return []


class TeamCompositionAgent:
    def __init__(self):
        provider = os.getenv("LLM_PROVIDER", "openai")
        
        if provider == "openai":
            self.llm = ChatOpenAI(
                model="gpt-3.5-turbo", 
                temperature=0, 
                api_key=os.getenv("OPENAI_API_KEY"))
        elif provider == "google":
            self.llm =  ChatGoogleGenerativeAI(
                model="gemini-pro", 
                temperature=0, 
                google_api_key=os.getenv("GOOGLE_API_KEY"))
        
        self.vector_storage = Chroma(persist_directory="./chroma_db", embedding_function=SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2"))
    
    def suggest_team_composition(self, required_skills_query: str) -> str:
        skills_str = ", ".join(required_skills_query)
        prompt = f"Given the following list of skills: {skills_str}, suggest an optimal team composition for a project requiring these skills. Provide roles and the number of people needed for each role."
        
        try:
            
            retrieved_docs = self.vector_storage.similarity_search(skills_str, k=5)  # Można wykorzystać do znalezienia podobnych projektów/zespołów w bazie danych
            
            unique_document_ids = {doc.metadata['document_id'] for doc in retrieved_docs if 'document_id' in doc.metadata} 

            top_candidates = Candidate.objects.filter(document__id__in=list(unique_document_ids))

            candidates_context = "\n".join([f"- Kandydat: {c.name}, Umiejętności: {c.skills}" for c in top_candidates])

            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", "Jesteś doświadczonym managerem projektu i liderem zespołu. Twoim zadaniem jest stworzenie  propozycji składu zespołu na podstawie listy wymaganych umiejętności i dostępnych kandydatów."),
                    ("human", "Potrzebuję zbudować zespół, który będzie posiadał następujące kluczowe umiejętności:**{required_skills}**.\n\n"
                         "Przeanalizuj poniższą listę dostępnych kandydatów i ich umiejętności:\n"
                         "**Dostępni kandydaci:**\n{candidates_list}\n\n"
                         "Zaproponuj optymalny skład zespołu, który pokryje wszystkie wymagane umiejętności. Krótko uzasadnij, dlaczego wybrałeś każdego z kandydatów i jaką rolę mógłby pełnić w zespole. Jeśli jacyś kandydaci się nie nadają, zignoruj ich. Przedstaw propozycję w klarowny i czytelny sposób.")])

            chain = prompt | self.llm            
            response = chain.invoke({
                        "required_skills": required_skills_query,
                        "candidates_list": candidates_context})

            print(f"Sugerowana kompozycja zespołu:\n{response}")
        
            return response.content    
        except Exception as e:
            print(f"Błąd podczas sugerowania kompozycji zespołu: {e}")
            return "Nie można zasugerować kompozycji zespołu w tym momencie."