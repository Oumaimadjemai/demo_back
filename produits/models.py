
from django.db import models
from parametres.models import Magasin
from django.core.exceptions import ValidationError
import random

# --- Barcode Utilities ---
def compute_ean13_checksum(code12):
    """Calcule le 13e chiffre (checksum) d'un EAN13."""
    if len(code12) != 12 or not code12.isdigit():
        raise ValueError("Code EAN doit contenir 12 chiffres")
    
    pairs = [int(d) for d in code12]
    total = sum(pairs[i] if i % 2 == 0 else pairs[i] * 3 for i in range(12))
    checksum = (10 - total % 10) % 10
    return str(checksum)


def generate_valid_ean13_code():
    """Génère un code EAN13 valide aléatoire."""
    while True:
        base = ''.join(str(random.randint(0, 9)) for _ in range(12))
        checksum = compute_ean13_checksum(base)
        full_code = base + checksum
        if len(full_code) == 13 and full_code.isdigit():
            return full_code


# def generer_codes_barres_uniques(existants, nombre):
#     """Génère `nombre` codes-barres EAN13 uniques, non présents dans `existants` ni dans la base."""
#     from produits.models import Produit  # Lazy import

#     existants_set = set(existants or [])

#     # Inclure tous les codes existants de la base
#     for produit in Produit.objects.all().only("codes_barres"):
#         if produit.codes_barres:
#             existants_set.update(produit.codes_barres)

#     nouveaux_codes = []
#     essais = 0
#     max_essais = nombre * 20

#     while len(nouveaux_codes) < nombre and essais < max_essais:
#         code = generate_valid_ean13_code()
#         if code not in existants_set:
#             nouveaux_codes.append(code)
#             existants_set.add(code)
#         essais += 1

#     if len(nouveaux_codes) < nombre:
#         raise Exception(f"Impossible de générer {nombre} codes-barres uniques après {max_essais} essais")

#     return nouveaux_codes
import random
from django.apps import apps 

def generer_codes_barres_uniques(existants, nombre):
    """Génère `nombre` codes EAN13 uniques sans recharger toute la base."""
    existants_set = set(existants or [])

    # ⚡️ Charger seulement les codes barres existants une seule fois
    tous_codes = Produit.objects.values_list("codes_barres", flat=True)
    for codes in tous_codes:
        if codes:
            existants_set.update(codes)

    nouveaux_codes = set()
    essais = 0
    max_essais = nombre * 50  # tolérance large

    while len(nouveaux_codes) < nombre and essais < max_essais:
        base = ''.join(str(random.randint(0, 9)) for _ in range(12))
        pairs = [int(d) for d in base]
        total = sum(pairs[i] if i % 2 == 0 else pairs[i] * 3 for i in range(12))
        checksum = (10 - total % 10) % 10
        code = base + str(checksum)

        if code not in existants_set and code not in nouveaux_codes:
            nouveaux_codes.add(code)
        essais += 1

    if len(nouveaux_codes) < nombre:
        raise ValueError(f"Impossible de générer {nombre} codes uniques après {max_essais} essais")

    return list(nouveaux_codes)


# --- Product Model ---
from cloudinary.models import CloudinaryField
class Produit(models.Model):
    reference = models.CharField(max_length=100, null=True)
    nom = models.CharField(max_length=100, verbose_name="اسم المنتوج / Nom produit")
    famille = models.CharField(max_length=100, verbose_name="العائلة / Famille")
    magasin = models.ForeignKey(Magasin, on_delete=models.CASCADE, verbose_name="المحل / Magasin")
    marque = models.CharField(max_length=100, verbose_name="العلامة / Marque", blank=True)

    codes_barres = models.JSONField(default=list, verbose_name="أكواد البار", blank=True, null=True)
    # image = models.ImageField(upload_to='produits/', verbose_name="صورة / Image", null=True, blank=True)
    image = CloudinaryField("صورة / Image", blank=True, null=True)

    prix_achat = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    prix_vente_cache = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    prix_vente_3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    prix_vente_5 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    prix_vente_6 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    prix_vente_8 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    prix_vente_9 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    prix_vente_10 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    prix_vente_12 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    prix_vente_15 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    quantite = models.IntegerField(default=0)

    taux_benefice_cache = models.FloatField(null=True, blank=True)
    taux_benefice_3 = models.FloatField(null=True, blank=True)
    taux_benefice_5 = models.FloatField(null=True, blank=True)
    taux_benefice_6 = models.FloatField(null=True, blank=True)
    taux_benefice_8 = models.FloatField(null=True, blank=True)
    taux_benefice_9 = models.FloatField(null=True, blank=True)
    taux_benefice_10 = models.FloatField(null=True, blank=True)
    taux_benefice_12 = models.FloatField(null=True, blank=True)
    taux_benefice_15 = models.FloatField(null=True, blank=True)

    date_creation = models.DateTimeField(auto_now_add=True, null=True)
    date_modification = models.DateTimeField(auto_now=True, null=True)
    est_supprime = models.BooleanField(default=False)

    @property
    def codebar_principal(self):
        return self.codes_barres[0] if self.codes_barres else None

    @property
    def moyenne_pourcentage_facilite(self):
        """Calcule la moyenne des taux définis (ignore les None)."""
        taux = [
            self.taux_benefice_3, self.taux_benefice_5, self.taux_benefice_6,
            self.taux_benefice_8, self.taux_benefice_9, self.taux_benefice_10,
            self.taux_benefice_12, self.taux_benefice_15
        ]
        taux_valides = [t for t in taux if t is not None]
        # return sum(taux_valides) / len(taux_valides) if taux_valides else 0
        if not taux_valides:
            return 0
        moyenne = sum(taux_valides)/len(taux_valides)
        return float(round(moyenne,2))

    def save(self, *args, **kwargs):
        # ✅ Ne recalcule pas les prix, ils viennent du front
        # ✅ Vérifie unicité des codes-barres
        if self.codes_barres:
            autres_produits = Produit.objects.exclude(pk=self.pk)
            for produit in autres_produits:
                if not produit.codes_barres:
                    continue
                doublons = set(self.codes_barres) & set(produit.codes_barres)
                if doublons:
                    raise ValidationError(f"Code-barres déjà utilisé(s) : {', '.join(doublons)}")

        super().save(*args, **kwargs)

    def incrementer_quantite(self, quantite):
        self.quantite += quantite
        self.save()

    def decrementer_quantite(self, quantite):
        self.quantite = max(0, self.quantite - quantite)
        self.save()
