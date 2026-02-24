import logging
import os
from urllib import response

from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate

from candidates.agents.BaseAgent import BaseAgent
from candidates.models import Candidate

class TeamCompositionAgent(BaseAgent):
    def __init__(self):                 
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.vector_storage = Chroma(persist_directory="./chroma_db", embedding_function=SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2"))
    
    def suggest_team_composition(self, required_skills_query: str) -> str:
        skills_str = ", ".join(required_skills_query)
        prompt = f"Given the following list of skills: {skills_str}, suggest an optimal team composition for a project requiring these skills. Provide roles and the number of people needed for each role."
        
        try:
            self.logger.info(f"Suggesting team composition for skills: {skills_str}")
          
            retrieved_docs = self.vector_storage.similarity_search(skills_str, k=5)  # Można wykorzystać do znalezienia podobnych projektów/zespołów w bazie danych
            
            self.logger.info(f"Retrieved {len(retrieved_docs)} similar documents from vector storage.")
            
            unique_document_ids = {doc.metadata['document_id'] for doc in retrieved_docs if 'document_id' in doc.metadata} 

            top_candidates = Candidate.objects.filter(document__id__in=list(unique_document_ids))

            candidates_context = "\n".join([f"- candidate: {c.name}, skills: {c.skills}" for c in top_candidates])

            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", "You are an experienced project manager and team leader. Your task is to create a team composition proposal based on the list of required skills and available candidates."),
                    ("human", "I need to build a team that will have the following key skills:**{required_skills}**.\n\n"
                         "Analyze the following list of available candidates and their skills:\n"
                         "**Available candidates:**\n{candidates_list}\n\n"
                         "Propose an optimal team composition that covers all required skills. Briefly explain why you chose each candidate and what role they could play in the team. If any candidates are not suitable, ignore them. Present the proposal in a clear and readable manner.")])

            chain = prompt | self.llm            
            response = chain.invoke({
                        "required_skills": required_skills_query,
                        "candidates_list": candidates_context})

            self.logger.info(f"Suggested team composition:\n{response}")

            if response:
                return response.content    
            else:                
                return "No team composition could be suggested based on the provided skills and candidates."

        except Exception as e:
            self.logger.error(f"Error during team composition suggestion: {e}")

            return "There was an error suggesting the team composition at this moment."