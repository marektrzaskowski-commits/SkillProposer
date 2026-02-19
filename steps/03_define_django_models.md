### **Krok 3: Definiowanie modeli danych Django**

W tym kroku stworzymy modele bazodanowe, które będą reprezentować kluczowe encje w naszym systemie: dokumenty i kandydatów. Modele te będą definiować strukturę danych, które nasz system będzie przechowywał i przetwarzał.

**Co masz zrobić:**

1.  **Definiowanie modelu dla dokumentów (`ingestion/models.py`):**
    *   Otwórz plik `ingestion/models.py`.
    *   Dodaj model `Document`, który będzie przechowywał informacje o wgranych plikach CV. Będzie on zawierał pola takie jak:
        *   `file` (FileField): Ścieżka do pliku CV.
        *   `uploaded_at` (DateTimeField): Data i czas wgrania pliku.
        *   `processing_status` (CharField): Status przetwarzania (np. 'pending', 'processed', 'failed').
        *   `extracted_text` (TextField): Pełny tekst wyodrębniony z dokumentu.
        *   `processed_by_agent` (BooleanField): Czy dokument został przetworzony przez agenta (do zarządzania przepływem pracy).

    ```python
    from django.db import models

    class Document(models.Model):
        PROCESSING_STATUS_CHOICES = [
            ('pending', 'Pending'),
            ('processed', 'Processed'),
            ('failed', 'Failed'),
        ]

        file = models.FileField(upload_to='documents/')
        uploaded_at = models.DateTimeField(auto_now_add=True)
        processing_status = models.CharField(
            max_length=20,
            choices=PROCESSING_STATUS_CHOICES,
            default='pending'
        )
        extracted_text = models.TextField(blank=True, null=True)
        processed_by_agent = models.BooleanField(default=False)

        def __str__(self):
            return f"Document: {self.file.name} (Status: {self.processing_status})"
    ```

2.  **Definiowanie modelu dla kandydatów (`candidates/models.py`):**
    *   Otwórz plik `candidates/models.py`.
    *   Dodaj model `Candidate`, który będzie przechowywał podstawowe informacje o kandydacie oraz odniesienie do przetworzonego dokumentu. Będzie zawierał pola takie jak:
        *   `document` (OneToOneField): Link do przetworzonego dokumentu (`ingestion.Document`). Używamy `OneToOneField`, ponieważ jeden dokument odpowiada jednemu kandydatowi.
        *   `name` (CharField): Imię i nazwisko kandydata (opcjonalne, może być uzupełniane po ekstrakcji).
        *   `email` (EmailField): Adres e-mail kandydata (opcjonalne).
        *   `skills` (TextField): Wyekstrahowane umiejętności kandydata (można przechowywać jako JSON lub przecinkami oddzielony tekst, na początek zwykły tekst wystarczy).

    ```python
    from django.db import models
    from ingestion.models import Document # Pamiętaj o imporcie modelu Document

    class Candidate(models.Model):
        document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name='candidate_profile')
        name = models.CharField(max_length=255, blank=True, null=True)
        email = models.EmailField(blank=True, null=True)
        skills = models.TextField(blank=True, null=True) # Przechowujemy umiejętności jako tekst

        def __str__(self):
            return self.name if self.name else f"Candidate from {self.document.file.name}"
    ```

3.  **Utwórz i zastosuj migracje:**
    *   Po zdefiniowaniu modeli, musisz poinformować Django o tych zmianach, aby utworzył odpowiednie tabele w bazie danych.
    *   W terminalu (z aktywnym środowiskiem wirtualnym) uruchom:
        ```bash
        python manage.py makemigrations
        ```
    *   Następnie zastosuj migracje:
        ```bash
        python manage.py migrate
        ```
    *   Sprawdź, czy nie pojawiły się żadne błędy. Jeśli wszystko poszło pomyślnie, Django utworzył pliki migracji i zastosował je do bazy danych.
