from rest_framework import serializers
from .models import Achat
from parametres.models import Magasin
from parametres.serializers import MagasinSerializer
from authentification.models import CustomUser
from authentification.serializers import CustomUserSerializer,FournisseurSerializer
from produits.serializers import ProduitMiniSerializer  # ⚠️ tu dois avoir celui-ci  # à créer si tu ne l'as pas
from produits.models import generer_codes_barres_uniques
class AchatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achat
        fields = '__all__'
        read_only_fields = ['total', 'somme_restante']

    def create(self, validated_data):
        validated_data['total'] = validated_data['quantite'] * validated_data['prix_achat']
        validated_data['somme_restante'] = validated_data['total'] - validated_data['somme_payee']
        return super().create(validated_data)

from rest_framework import serializers
from .models import AchatGroupe, LigneAchat
from produits.models import Produit
from parametres.models import Magasin
from parametres.serializers import MagasinSerializer
from authentification.serializers import CustomUserSerializer, FournisseurSerializer
from produits.serializers import ProduitMiniSerializer

class LigneAchatSerializer(serializers.ModelSerializer):
    produit_detail = ProduitMiniSerializer(source='produit', read_only=True)
    magasin_detail = MagasinSerializer(source='magasin', read_only=True)

    class Meta:
        model = LigneAchat
        fields = [
            'id',
            'produit', 'produit_detail',
            'magasin', 'magasin_detail',
            'quantite',
            'prix_achat',
            'nouveaux_codes_barres',  # ✅ persistant dans la DB
        ]
        extra_kwargs = {
            'magasin': {'required': False}
        }
# class AchatGroupeSerializer(serializers.ModelSerializer):
#     achats = LigneAchatSerializer(many=True)
#     total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
#     somme_restante = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
#     utilisateur_detail = CustomUserSerializer(source='utilisateur', read_only=True)
#     fournisseur_detail = FournisseurSerializer(source='fournisseur', read_only=True)
#     date_formatee = serializers.SerializerMethodField()
    
#     class Meta:
#         model = AchatGroupe
#         fields = ['id', 'fournisseur', 'fournisseur_detail', 'utilisateur', 'utilisateur_detail', 
#                  'date', 'date_formatee', 'achats', 'total', 'somme_payee', 'somme_restante']
#         read_only_fields = ['utilisateur', 'date', 'date_formatee']

#     def get_date_formatee(self, obj):
#         return obj.date.strftime('%d/%m/%Y') if obj.date else None

#     def create(self, validated_data):
#         achats_data = validated_data.pop('achats')
#         user = self.context['request'].user
#         somme_totale = 0

#         achat_groupe = AchatGroupe.objects.create(utilisateur=user, **validated_data)
#         lignes_achat_serialisables = []
#         for ligne in achats_data:
#             produit = ligne['produit']
#             quantite = ligne['quantite']
#             prix = ligne['prix_achat']
#             somme_totale += quantite * prix
            
#             if 'magasin' not in ligne or ligne['magasin'] is None:
#                 ligne['magasin'] = Magasin.objects.first()

#             anciens_codes = produit.codes_barres or []
#             nouveaux_codes = generer_codes_barres_uniques(anciens_codes, quantite)
#             produit.codes_barres = anciens_codes + nouveaux_codes
#             produit.incrementer_quantite(quantite)
#             produit.save()

# # Injection temporaire pour que le serializer mini affiche les nouveaux codes-barres
#             produit.nouveaux_codes_barres = nouveaux_codes



#             ligne_achat = LigneAchat.objects.create(
#     achat_groupe=achat_groupe,
#     nouveaux_codes_barres=nouveaux_codes,   # ✅ sauvegarde en base
#     **ligne
# )
#             # ligne_achat.nouveaux_codes_barres = nouveaux_codes  # 👈 injecté dans l'instance
#             # setattr(ligne_achat, "nouveaux_codes_barres", nouveaux_codes)
#             lignes_achat_serialisables.append(ligne_achat)
#         achat_groupe.total = somme_totale
#         achat_groupe.somme_restante = somme_totale - achat_groupe.somme_payee
#         achat_groupe.save()
#         self._achats_with_extra = lignes_achat_serialisables

#         return achat_groupe

#     def update(self, instance, validated_data):
#         achats_data = validated_data.pop('achats', [])
        
#         # Update main AchatGroupe fields
#         instance.fournisseur = validated_data.get('fournisseur', instance.fournisseur)
#         instance.somme_payee = validated_data.get('somme_payee', instance.somme_payee)
        
#         # Handle achats updates
#         existing_achats = {achat.id: achat for achat in instance.achats.all()}
#         updated_achats = []
#         somme_totale = 0
        
#         for achat_data in achats_data:
#             achat_id = achat_data.get('id', None)
            
#             if achat_id and achat_id in existing_achats:
#                 # Update existing achat
#                 achat = existing_achats[achat_id]
#                 old_quantite = achat.quantite
                
#                 for attr, value in achat_data.items():
#                     setattr(achat, attr, value)
#                 achat.save()
                
#                 # Update product quantity (difference between new and old)
#                 quantite_diff = achat.quantite - old_quantite
#                 achat.produit.incrementer_quantite(quantite_diff)
                
#                 updated_achats.append(achat.id)
#                 somme_totale += achat.quantite * achat.prix_achat
#             else:
#                 # Create new achat
#                 if 'magasin' not in achat_data or achat_data['magasin'] is None:
#                     achat_data['magasin'] = Magasin.objects.first()
                
#                 achat = LigneAchat.objects.create(achat_groupe=instance, **achat_data)
#                 achat.produit.incrementer_quantite(achat.quantite)
#                 updated_achats.append(achat.id)
#                 somme_totale += achat.quantite * achat.prix_achat
        
#         # Delete achats that weren't included in the update
#         for achat_id, achat in existing_achats.items():
#             if achat_id not in updated_achats:
#                 achat.produit.incrementer_quantite(-achat.quantite)  # Decrement stock
#                 achat.delete()
        
#         # Update totals
#         instance.total = somme_totale
#         instance.somme_restante = somme_totale - instance.somme_payee
#         instance.save()
        
#         return instance
#     def to_representation(self, instance):
#       data = super().to_representation(instance)

#       if hasattr(self, '_achats_with_extra'):
#         # On sérialise les lignes avec les nouveaux codes-barres
#         data['achats'] = LigneAchatSerializer(self._achats_with_extra, many=True).data

#       return data
class AchatGroupeSerializer(serializers.ModelSerializer):
    achats = LigneAchatSerializer(many=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    somme_restante = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    utilisateur_detail = CustomUserSerializer(source='utilisateur', read_only=True)
    fournisseur_detail = FournisseurSerializer(source='fournisseur', read_only=True)
    date_formatee = serializers.SerializerMethodField()
    
    class Meta:
        model = AchatGroupe
        fields = [
            'id', 'fournisseur', 'fournisseur_detail',
            'utilisateur', 'utilisateur_detail',
            'date', 'date_formatee',
            'achats', 'total', 'somme_payee', 'somme_restante'
        ]
        read_only_fields = ['utilisateur', 'date', 'date_formatee']

    def get_date_formatee(self, obj):
        return obj.date.strftime('%d/%m/%Y') if obj.date else None

    # -----------------------
    # CREATE
    # -----------------------
    def create(self, validated_data):
        achats_data = validated_data.pop('achats')
        user = self.context['request'].user
        somme_totale = 0

        achat_groupe = AchatGroupe.objects.create(utilisateur=user, **validated_data)
        lignes_achat_serialisables = []

        for ligne in achats_data:
            produit = ligne['produit']
            quantite = ligne['quantite']
            prix = ligne['prix_achat']
            somme_totale += quantite * prix

            if 'magasin' not in ligne or ligne['magasin'] is None:
                ligne['magasin'] = Magasin.objects.first()

            # ✅ Génération codes-barres uniques
            anciens_codes = produit.codes_barres or []
            nouveaux_codes = generer_codes_barres_uniques(anciens_codes, quantite)

            # ✅ Mise à jour produit
            produit.codes_barres = anciens_codes + nouveaux_codes
            produit.incrementer_quantite(quantite)

            # ✅ Ligne achat + sauvegarde des codes
            ligne_achat = LigneAchat.objects.create(
                achat_groupe=achat_groupe,
                nouveaux_codes_barres=nouveaux_codes,
                **ligne
            )
            lignes_achat_serialisables.append(ligne_achat)

        achat_groupe.total = somme_totale
        achat_groupe.somme_restante = somme_totale - achat_groupe.somme_payee
        achat_groupe.save()
        self._achats_with_extra = lignes_achat_serialisables

        return achat_groupe

    # -----------------------
    # UPDATE
    # -----------------------
    def update(self, instance, validated_data):
        achats_data = validated_data.pop('achats', [])
        instance.fournisseur = validated_data.get('fournisseur', instance.fournisseur)
        instance.somme_payee = validated_data.get('somme_payee', instance.somme_payee)

        existing_achats = {achat.id: achat for achat in instance.achats.all()}
        updated_achats = []
        somme_totale = 0

        for achat_data in achats_data:
            achat_id = achat_data.get('id', None)

            if achat_id and achat_id in existing_achats:
                # ✅ Update existant
                achat = existing_achats[achat_id]
                old_quantite = achat.quantite
                old_codes = achat.nouveaux_codes_barres or []

                for attr, value in achat_data.items():
                    setattr(achat, attr, value)
                achat.save()

                # Différence quantité
                quantite_diff = achat.quantite - old_quantite
                if quantite_diff > 0:
                    # Ajout de nouveaux codes
                    nouveaux_codes = generer_codes_barres_uniques(achat.produit.codes_barres, quantite_diff)
                    achat.produit.codes_barres.extend(nouveaux_codes)
                    achat.nouveaux_codes_barres.extend(nouveaux_codes)
                    achat.produit.incrementer_quantite(quantite_diff)
                elif quantite_diff < 0:
                    # Suppression de codes existants
                    retirer = min(len(old_codes), -quantite_diff)
                    codes_a_supprimer = old_codes[:retirer]
                    achat.produit.codes_barres = [c for c in achat.produit.codes_barres if c not in codes_a_supprimer]
                    achat.nouveaux_codes_barres = [c for c in achat.nouveaux_codes_barres if c not in codes_a_supprimer]
                    achat.produit.decrementer_quantite(retirer)

                achat.produit.save()

                updated_achats.append(achat.id)
                somme_totale += achat.quantite * achat.prix_achat

            else:
                # ✅ Nouveau achat
                if 'magasin' not in achat_data or achat_data['magasin'] is None:
                    achat_data['magasin'] = Magasin.objects.first()

                produit = achat_data['produit']
                quantite = achat_data['quantite']
                nouveaux_codes = generer_codes_barres_uniques(produit.codes_barres, quantite)

                produit.codes_barres.extend(nouveaux_codes)
                produit.incrementer_quantite(quantite)
                produit.save()

                achat = LigneAchat.objects.create(
                    achat_groupe=instance,
                    nouveaux_codes_barres=nouveaux_codes,
                    **achat_data
                )
                updated_achats.append(achat.id)
                somme_totale += achat.quantite * achat.prix_achat

        # ✅ Suppression des achats non envoyés
        for achat_id, achat in existing_achats.items():
            if achat_id not in updated_achats:
                produit = achat.produit
                # Retirer les codes-barres liés
                if achat.nouveaux_codes_barres:
                    produit.codes_barres = [c for c in produit.codes_barres if c not in achat.nouveaux_codes_barres]
                produit.decrementer_quantite(achat.quantite)
                produit.save()
                achat.delete()

        # ✅ Totaux
        instance.total = somme_totale
        instance.somme_restante = somme_totale - instance.somme_payee
        instance.save()

        return instance

    # -----------------------
    # REPRESENTATION
    # -----------------------
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if hasattr(self, '_achats_with_extra'):
            data['achats'] = LigneAchatSerializer(self._achats_with_extra, many=True).data
        return data

