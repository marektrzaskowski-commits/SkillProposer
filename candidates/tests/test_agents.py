from unittest.mock import patch, MagicMock

from django.test import TestCase

from ..agents.SkillExtractionAgent import SkillExtractionAgent


class SkillExtractionAgentTest(TestCase):
    def setUp(self) -> None:
        self.agent = SkillExtractionAgent()
        return super().setUp()
    

    @patch('candidates.agents.ChatOpenAI') 
    @patch('candidates.agents.LLMChain')   
    def test_skill_extraction(self, mock_llm_chain, mock_chat_openai):
        
        mock_llm_instance = MagicMock()
        mock_chat_openai.return_value = mock_llm_instance
        
        mock_llm_chain_instance = MagicMock()
        mock_llm_chain.return_value = mock_llm_chain_instance

        skills = self.agent.extract_skills("This is a test document with skills like Python and Django.")

        self.assertIsInstance(skills, list)
        self.assertIn("Python", skills)

        mock_chat_openai.assert_called_once()   
        mock_llm_chain.assert_called_once()     
    
    