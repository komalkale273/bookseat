
from django.db import models

class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    subject = models.CharField(max_length=255) 
    
    def __str__(self):
        return f"Message from {self.name}"
