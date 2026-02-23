from django.test import TestCase
from candidates.forms import SkillSearchForm, TeamCompositionForm


class CandidateSearchFormTests(TestCase):
    def test_form_valid(self):      
        form = SkillSearchForm(data={'querySkills': 'Python'})
        self.assertTrue(form.is_valid())    