
from django.db import models

class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    subject = models.CharField(max_length=255) 
    
    def __str__(self):
        return f"Message from {self.name}"
class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField(blank=True, null=True)  # Admin can later answer
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question