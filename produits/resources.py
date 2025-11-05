# resources.py
from import_export import resources
from .models import Produit

class ProduitResource(resources.ModelResource):
    class Meta:
        model = Produit
        fields = (
            'id', 'reference', 'nom', 'famille', 'magasin__nom', 'marque',
            'codes_barres', 'prix_achat', 'prix_vente_cache',
            'prix_vente_3', 'prix_vente_5', 'prix_vente_8', 'prix_vente_10',
            'quantite',
            'taux_benefice_3', 'taux_benefice_5', 'taux_benefice_8', 'taux_benefice_10', 'taux_benefice_cache'
        )
