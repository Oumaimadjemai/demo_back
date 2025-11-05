from django.db import models
from authentification.models import Client  # à adapter à ton projet
from produits.models import Produit
from parametres.models import Magasin
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.db.models.functions import Coalesce
from django.db.models import DecimalField, Sum
User = get_user_model()
class VenteFacilite(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="الزبون")
    date_debut = models.DateField()
    date_fin = models.DateField()
    nombre_mois = models.PositiveIntegerField()
    montant_total = models.DecimalField(max_digits=1000, decimal_places=0)
    montant_verse = models.DecimalField(max_digits=1000, decimal_places=0, default=0)
    montant_paye_effectif = models.DecimalField(max_digits=1000, decimal_places=0, default=0)  # <-- Nouveau champ
    montant_restant = models.DecimalField(max_digits=1000, decimal_places=0)
    montant_mensuel = models.DecimalField(max_digits=1000, decimal_places=0)
    montants_par_mois = models.JSONField(default=list)
    mois_status = models.JSONField(default=list, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    last_payment_date = models.DateField(null=True, blank=True)
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="المستخدم")
    solde_regle = models.BooleanField(default=False)
    class Meta:
        ordering=['-id']
    def save(self, *args, **kwargs):
        # Initialize month statuses if empty
        if not self.mois_status or len(self.mois_status) != self.nombre_mois:
            self.mois_status = ["pending"] * self.nombre_mois
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.client} - {self.nombre_mois} mois"
    
    @property
    def dette_totale_client(self):
       return VenteFacilite.objects.filter(client=self.client).aggregate(
        total=Coalesce(
            Sum('montant_total', output_field=DecimalField(max_digits=1000, decimal_places=0)),
            0,
            output_field=DecimalField(max_digits=1000, decimal_places=0)
        )
    )['total']

    @property
    def dette_actuelle_client(self):
      return VenteFacilite.objects.filter(client=self.client).aggregate(
        total=Coalesce(
            Sum('montant_restant', output_field=DecimalField(max_digits=1000, decimal_places=0)),
            0,
            output_field=DecimalField(max_digits=1000, decimal_places=0)
        )
    )['total']
    def effectuer_paiement_mensuel(self):
        """Soustrait le montant mensuel du restant et met à jour la date de paiement"""
        if self.montant_restant > 0:
            paiement = min(self.montant_mensuel, self.montant_restant)
            self.montant_paye_effectif += paiement
            self.montant_restant -= paiement
            self.last_payment_date = now().date()
            self.save()
            return paiement
        return 0

class LigneVenteFacilite(models.Model):
    vente = models.ForeignKey(VenteFacilite, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    sous_total = models.DecimalField(max_digits=10, decimal_places=2)
    codes_barres_utilises = models.JSONField(default=list, blank=True)


    def save(self, *args, **kwargs):
        self.sous_total = self.quantite * self.prix_unitaire
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.produit.nom} x {self.quantite}"


from django.db import models
from django.utils.timezone import now

class PaiementVente(models.Model):
    vente = models.ForeignKey("VenteFacilite", on_delete=models.CASCADE, related_name="paiements")
    montant = models.DecimalField(max_digits=10, decimal_places=0)
    date_paiement = models.DateTimeField(default=now)
    
    # ✅ Add month and status
    month_index = models.PositiveSmallIntegerField(default=0,null=True,blank=True)  # 0-11 (Jan=0)
    status = models.CharField(max_length=20, default="pending")  # pending, paid, unpaid

    def __str__(self):
        return f"Paiement {self.montant} pour {self.vente.client} mois {self.month_index+1}"


# User = get_user_model()
class VenteCache(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="الزبون")
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="المستخدم")
    date_vente = models.DateTimeField(auto_now_add=True)

    montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Vente {self.id} - {self.client} - {self.date_vente.date()}"


class LigneVenteCache(models.Model):
    vente = models.ForeignKey(VenteCache, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    sous_total = models.DecimalField(max_digits=10, decimal_places=2)
    codes_barres_utilises = models.JSONField(default=list)

    def save(self, *args, **kwargs):
        self.sous_total = self.prix_unitaire * self.quantite
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.produit.nom} x {self.quantite}"
    

