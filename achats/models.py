from django.db import models
from produits.models import Produit
from parametres.models import Magasin
from authentification.models import CustomUser,Fournisseur

class Achat(models.Model):
    produit = models.ForeignKey('produits.Produit', on_delete=models.CASCADE)
    fournisseur = models.IntegerField()  # ID du fournisseur depuis Authentification
    magasin = models.ForeignKey('parametres.Magasin', on_delete=models.CASCADE)
    
    quantite = models.IntegerField()
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2, blank=True)  # Calculé
    somme_payee = models.DecimalField(max_digits=12, decimal_places=2)
    somme_restante = models.DecimalField(max_digits=12, decimal_places=2, blank=True)
    
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total = self.quantite * self.prix_achat
        self.somme_restante = self.total - self.somme_payee
        super().save(*args, **kwargs)
# achats/models.py

class AchatGroupe(models.Model):
    fournisseur = models.ForeignKey(
        Fournisseur, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="fournisseur"
    ) 
    utilisateur = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Utilisateur"
    )
    date = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    somme_payee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    somme_restante = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class LigneAchat(models.Model):
    achat_groupe = models.ForeignKey(AchatGroupe, on_delete=models.CASCADE, related_name='achats')
    produit = models.ForeignKey(Produit, on_delete=models.SET_NULL, null=True)
    quantite = models.IntegerField()
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2)
    magasin = models.ForeignKey(Magasin, on_delete=models.SET_NULL, null=True,blank=True)
    nouveaux_codes_barres = models.JSONField(default=list, blank=True, null=True)
