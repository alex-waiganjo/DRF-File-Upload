from django.db import models

class File(models.Model):
    FILE_TYPE_CHOICES = (
        ('excel', 'Excel'),
        ('pdf', 'PDF')
    )
    
    file = models.FileField(upload_to='uploads/')
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.name} ({self.file_type})"
