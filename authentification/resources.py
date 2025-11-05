from import_export import resources
from .models import *

class ClientResource(resources.ModelResource):
    class Meta:
        model = Client
        fields = (
            'id', 'nom_famille_fr','nom_famille_ar', 'prenom_fr','nom_pere','nom_mere', 'ccp','cle'
            'nom_famille_ar', 'prenom_ar', 'adresse', 'telephone',
            'numero_national', 'profession', 'revenu', 
            'numero_piece_identite', 'type_piece_identite',
            'date_naissance', 'lieu_naissance','date_emission_piece','jour',
            'lieu_emission_piece','dette_initiale','note'
        )


class FournisseurResource(resources.ModelResource):
    class Meta:
        model = Fournisseur
        fields = ('id', 'nom', 'adresse', 'telephone', 'wilaya','dettes_initiales')
