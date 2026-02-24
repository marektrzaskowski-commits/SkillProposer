import logging
import os

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from candidates.agents.BaseAgent import BaseAgent
from candidates.agents.SkillSet import SkillSet

class SkillExtractionAgent(BaseAgent):
    def __init__(self):       
        super().__init__()
        self.logger = logging.getLogger(__name__)

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
                self.logger.info(f"extracted {len(extracted_skills)} skills: {extracted_skills}")
                
                return extracted_skills
            return []
        except Exception as e:
            self.logger.error(f"Error during skill extraction: {e}")
            return []
