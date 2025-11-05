from django.db import models
from django.utils import timezone
from produits.models import Produit
from parametres.models import Magasin
from authentification.models import CustomUser

from django.utils import timezone

def get_current_time():
    return timezone.now().time()


class Transfert(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT, verbose_name="Produit")
    magasin_source = models.ForeignKey(
        Magasin, on_delete=models.PROTECT,
        related_name='transferts_sortants',
        verbose_name="Magasin source"
    )
    magasin_destination = models.ForeignKey(
        Magasin, on_delete=models.PROTECT,
        related_name='transferts_entrants',
        verbose_name="Magasin destination"
    )
    quantite = models.PositiveIntegerField(verbose_name="Quantité")
    codes_barres_transferes = models.JSONField(default=list, verbose_name="Codes-barres transférés")
    utilisateur = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Utilisateur"
    )
    date = models.DateTimeField(default=timezone.now, verbose_name="Date")
    heure = models.TimeField(default=get_current_time, verbose_name="Time")
    produit_supprime = models.BooleanField(default=False, verbose_name="Produit supprimé")

    class Meta:
        verbose_name = "Transfert"
        verbose_name_plural = "Transferts"
        ordering = ['-date', '-heure']

    def __str__(self):
        return f"Transfert #{self.id} - {self.produit.nom if self.produit else 'Produit supprimé'}"
