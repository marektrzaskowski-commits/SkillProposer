import os

from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate

from candidates.agents.BaseAgent import BaseAgent
from candidates.models import Candidate

class TeamCompositionAgent(BaseAgent):
    def __init__(self):                 
        super().__init__()

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