from django import forms


class SkillSearchForm(forms.Form):
    querySkills = forms.CharField(label='Skill', max_length=255)

class TeamCompositionForm(forms.Form):
    required_skills = forms.CharField(
        label='Required Skills', 
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        help_text='Enter the required skills for the project, separated by commas.',
        max_length=500)