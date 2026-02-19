import os
from pydoc import text
from typing import List
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

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
