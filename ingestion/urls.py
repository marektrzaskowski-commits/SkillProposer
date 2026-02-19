from django.urls import path
from . import views

app_name = 'ingestion'

urlpatterns = [
    path('upload/', views.upload_document, name='upload_document'),
    path('upload/success/<int:document_id>/', views.upload_success, name='upload_success'),
]
