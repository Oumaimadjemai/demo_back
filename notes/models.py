from django.db import models

class Note(models.Model):
    title = models.CharField(max_length=255)
    subject = models.TextField()
    color = models.CharField(max_length=20, default="#f5f5f5")
    date = models.DateTimeField(auto_now_add=True)  # store creation date

    def __str__(self):
        return self.title
