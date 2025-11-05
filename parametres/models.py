from django.db import models

# Create your models here.
class Magasin(models.Model):
    nom = models.CharField(max_length=100, verbose_name="اسم المحل")
    adresse = models.TextField(verbose_name="العنوان")
    
    def __str__(self):
        return self.nom
    
    class Meta:
        verbose_name = "المحل"
        verbose_name_plural = "المحلات"
