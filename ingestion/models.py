from django.db import models

class Document(models.Model):
    PROCESSING_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    ]

    file = models.FileField(upload_to='documents/')
    extracted_text = models.TextField(null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_by_agent = models.BooleanField(default=False)
    processing_status = models.CharField(
        max_length=20,
        choices=PROCESSING_STATUS_CHOICES,
        default='pending')

    def __str__(self):
        return f"Document: {self.file.name} (Status: {self.processing_status})"
