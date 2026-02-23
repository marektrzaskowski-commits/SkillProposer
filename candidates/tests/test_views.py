from django.test import TestCase, Client


class CandidateViewTests(TestCase):
   def setUp(self) -> None:
       self.client = Client()
       return super().setUp()
   
   def test_search_candidates(self):
        response = self.client.get('/candidates/search/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'candidates/search.html')