from django.db import models
from django.conf import settings

class Depense(models.Model):
    MODES_PAIEMENT = [
        ('espece', 'Espèces'),
        ('cheque', 'Chèque'),
        ('ccp', 'Ccp'),
    ]
    
    TYPES_DEPENSE = [
        ('أجور العمال', 'أجور العمال'),
        ('الفواتير', 'الفواتير'),
        ('الكراء', 'الكراء'),
        ('سلع تالفة', 'سلع تالفة'),
        ('مصاريف أخرى', 'مصاريف أخرى'),
        ('ديون', 'ديون'),
        ('ديون خاصة', 'ديون خاصة'),
        ('مساهمين', 'مساهمين'),
        
    ]
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='depenses',
        null=True
    )
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    libelle = models.CharField(max_length=255)  # Par exemple : "حسان", "محمد تيارات"
    type_depense = models.CharField(max_length=50, choices=TYPES_DEPENSE)
    mode_paiement = models.CharField(max_length=20, choices=MODES_PAIEMENT)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.libelle} - {self.montant}"
