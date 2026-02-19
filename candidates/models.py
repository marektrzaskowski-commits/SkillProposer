from django.db import models

from ingestion.models import Document

class Candidate(models.Model):
    document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name="candidate_profile")
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name if self.name else f"Candidate from {self.document.file.name}" 