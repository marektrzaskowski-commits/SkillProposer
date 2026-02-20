from django.urls import path
from . import views

app_name = 'candidates'

urlpatterns = [
    path('search/', views.search_candidates, name='search'),
    path('team-composition/', views.propose_team, name='team_composition'),
]