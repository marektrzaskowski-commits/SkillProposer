from functools import lru_cache

from django.shortcuts import render
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma

from candidates.agents.TeamCompositionAgent import TeamCompositionAgent
from candidates.forms import SkillSearchForm, TeamCompositionForm
from candidates.models import Candidate

@lru_cache(maxsize=1)
def get_vector_storage():
    embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_storage = Chroma(persist_directory="./chroma_db", embedding_function=embedding_model)
    return vector_storage

def search_candidates(request):
    if request.method == 'POST':
        form = SkillSearchForm(request.POST)
        if form.is_valid():
            query_skills = form.cleaned_data['querySkills']
            vector_storage = get_vector_storage()
            
            searched_result = vector_storage.similarity_search(query_skills, k=10)  # Przykładowo zwróć 10 najbardziej podobnych kandydatów

            document_ids = [doc.metadata.get("document_id") for doc in searched_result]

## uzyc kontentu z chroma
## napisac prompta do openai z opisem outputu i wykorzystac go do wygenerowania odpowiedzi



            unique_ids = list(dict.fromkeys(filter(None, document_ids)))

            if ((unique_ids is not None) and len(unique_ids) > 0):
                candidates_list = list(Candidate.objects.filter(document_id__in=unique_ids).distinct())

            return render(request, 'candidates/search.html', {'form': form, 'candidates': candidates_list})
    else:
        form = SkillSearchForm()
    
    return render(request, 'candidates/search.html', {'form': form})

def propose_team(request):
    if request.method == 'POST':
        form = TeamCompositionForm(request.POST)
        if form.is_valid():
            required_skills = form.cleaned_data['required_skills']
            
            agent = TeamCompositionAgent()
            team_composition = agent.suggest_team_composition(required_skills)

            return render(request, 'candidates/team_composition.html', {'form': form, 'team_composition': team_composition})
    else:
        form = TeamCompositionForm()
    
    return render(request, 'candidates/team_composition.html', {'form': form})