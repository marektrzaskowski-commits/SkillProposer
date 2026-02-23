from pydoc import doc

from django.test import TestCase

from candidates.models import Candidate
from ingestion.models import Document


class CandidateModelTests(TestCase):
    def setUp(self):
        self.document = Document.objects.create(            
            file="test_document.pdf",
            extracted_text="This is a test document.",  
        )

        self.candidate = Candidate.objects.create(
            document=self.document,
            name="John Doe",
            email="name@example.com",
            skills="Python, Django"
        )        
        pass

    def test_candidate_creation(self):
        self.assertIsInstance(self.candidate, Candidate)
        self.assertEqual(self.candidate.document.extracted_text, "This is a test document.")
        self.assertEqual(self.candidate.name, "John Doe")
        self.assertEqual(self.candidate.email, "name@example.com")
        self.assertEqual(self.candidate.skills, "Python, Django")
