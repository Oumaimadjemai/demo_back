from rest_framework import serializers
from .models import *
from produits.models import Produit
from produits.serializers import ProduitSerializer
from authentification.serializers import ClientSerializer
from parametres.serializers import MagasinSerializer
from datetime import timedelta
from rest_framework.exceptions import ValidationError
from django.utils.timezone import localtime
from authentification.serializers import CustomUserSerializer
class LigneVenteFaciliteSerializer(serializers.ModelSerializer):
    produit = serializers.PrimaryKeyRelatedField(queryset=Produit.objects.all())  # <--
    produit_detail = ProduitSerializer(source='produit', read_only=True)

    class Meta:
        model = LigneVenteFacilite
        fields = [
            'id', 'produit', 'produit_detail', 'quantite',
            'prix_unitaire', 'sous_total', 'codes_barres_utilises'
        ]
        read_only_fields = ['prix_unitaire', 'sous_total', 'codes_barres_utilises']


class VenteFaciliteSerializer(serializers.ModelSerializer):
    lignes = LigneVenteFaciliteSerializer(many=True, write_only=True)
    lignes_detail = LigneVenteFaciliteSerializer(many=True, read_only=True, source='lignes')
    client_detail = ClientSerializer(source='client', read_only=True)
    utilisateur_detail = serializers.SerializerMethodField()
    date_formatee = serializers.SerializerMethodField()

    # # ✅ New fields without source
    dette_totale_client = serializers.SerializerMethodField()
    dette_actuelle_client = serializers.SerializerMethodField()

    class Meta:
        model = VenteFacilite
        fields = [
            'id', 'client', 'client_detail', 'utilisateur', 'utilisateur_detail',
            'nombre_mois', 'date_debut', 'date_fin',
            'montant_total', 'montant_verse', 'montant_restant',
            'montant_mensuel', 'montants_par_mois', 'montant_paye_effectif', 'date_creation', 'last_payment_date',
            'lignes', 'lignes_detail', 'date_formatee',
            'dette_totale_client', 'dette_actuelle_client','solde_regle'
        ]
        read_only_fields = [
            'date_creation', 'lignes_detail', 'utilisateur',
            'last_payment_date', 'dette_totale_client', 'dette_actuelle_client', 'montant_paye_effectif',
        ]

    def get_utilisateur_detail(self, obj):
        if obj.utilisateur:
            return {
                "id": obj.utilisateur.id,
                "username": obj.utilisateur.username,
            }
        return None

    def get_date_formatee(self, obj):
        return localtime(obj.date_creation).strftime('%d/%m/%Y')

    def get_dette_totale_client(self, obj):
        return obj.dette_totale_client

    def get_dette_actuelle_client(self, obj):
        return obj.dette_actuelle_client

    def create(self, validated_data):
        lignes_data = validated_data.pop('lignes', [])
        
        # ✅ Assign the logged-in user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['utilisateur'] = request.user

        vente = VenteFacilite.objects.create(**validated_data)
        nombre_mois = vente.nombre_mois

        prix_mapping_field = {
            3: 'prix_vente_3',
            5: 'prix_vente_5',
            6:'prix_vente_6',
            8: 'prix_vente_8',
            9:'prix_vente_9',
            10: 'prix_vente_10',
            12:'prix_vente_12',
            15:'prix_vente_15',

        }

        for ligne in lignes_data:
            produit = ligne['produit']
            quantite = ligne['quantite']

            if produit.quantite < quantite:
                raise serializers.ValidationError(f"Stock insuffisant pour {produit.nom}")

            if len(produit.codes_barres) < quantite:
                raise serializers.ValidationError(
                    f"Pas assez de codes-barres pour {produit.nom}. "
                    f"Demandé : {quantite}, disponibles : {len(produit.codes_barres)}"
                )

            prix_field = prix_mapping_field.get(nombre_mois)
            if not prix_field:
                raise serializers.ValidationError(f"Aucun prix défini pour {nombre_mois} mois pour {produit.nom}.")

            prix_unitaire = getattr(produit, prix_field)
            sous_total = prix_unitaire * quantite

            # Mise à jour du stock
            codes_utilises = produit.codes_barres[:quantite]
            produit.codes_barres = produit.codes_barres[quantite:]
            produit.quantite -= quantite
            produit.save()

            LigneVenteFacilite.objects.create(
                vente=vente,
                produit=produit,
                quantite=quantite,
                prix_unitaire=prix_unitaire,
                sous_total=sous_total,
                codes_barres_utilises=codes_utilises
            )

        return vente



class PaiementVenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaiementVente
        fields = ["id", "montant", "date_paiement", "month_index", "status"]


# ventes/serializers.py
from produits.serializers import MagasinSerializer  # adapte l'import

class LigneVenteCacheReadSerializer(serializers.ModelSerializer):
    produit_nom = serializers.CharField(source='produit.nom', read_only=True)
    produit_reference=serializers.CharField(source='produit.reference',read_only=True)
    magasin_detail = MagasinSerializer(source='produit.magasin', read_only=True)
    codes_barres_utilises = serializers.ListField(read_only=True)

    class Meta:
        model = LigneVenteCache
        fields = ['id', 'produit', 'produit_nom', 'produit_reference','quantite', 'prix_unitaire', 'sous_total', 'magasin_detail','codes_barres_utilises']


class LigneVenteCacheCreateSerializer(serializers.Serializer):
    produit = serializers.IntegerField()
    quantite = serializers.IntegerField(min_value=1)



class VenteCacheSerializer(serializers.ModelSerializer):
    lignes = LigneVenteCacheCreateSerializer(many=True, write_only=True)
    lignes_detail = LigneVenteCacheReadSerializer(many=True, read_only=True, source='lignes')
    client_detail = ClientSerializer(source='client', read_only=True)
    utilisateur_detail = serializers.SerializerMethodField()
    date_formatee = serializers.SerializerMethodField()

    class Meta:
        model = VenteCache
        fields = [
            'id', 'client', 'client_detail', 'utilisateur', 'utilisateur_detail',
            'lignes', 'lignes_detail', 'montant_total', 'date_vente', 'date_formatee'
        ]
        read_only_fields = [
            'montant_total', 'date_vente', 'lignes_detail',
            'client_detail', 'utilisateur', 'utilisateur_detail', 'date_formatee'
        ]

    def get_utilisateur_detail(self, obj):
        if obj.utilisateur:
            return {
                "id": obj.utilisateur.id,
                "username": obj.utilisateur.username,
            }
        return None

    def get_date_formatee(self, obj):
        return localtime(obj.date_vente).strftime('%d/%m/%Y')

    def create(self, validated_data):
        lignes_data = validated_data.pop('lignes')
        request = self.context.get('request')
        utilisateur = request.user if request and request.user.is_authenticated else None

        vente = VenteCache.objects.create(utilisateur=utilisateur, **validated_data)
        montant_total = 0

        for ligne in lignes_data:
            produit_id = ligne['produit']
            quantite = ligne['quantite']

            try:
                produit = Produit.objects.get(id=produit_id)
            except Produit.DoesNotExist:
                raise ValidationError(f"Produit avec ID {produit_id} introuvable.")

            if produit.quantite < quantite:
                raise ValidationError(
                    f"Quantité insuffisante pour le produit '{produit.nom}'. "
                    f"Disponible : {produit.quantite}, demandé : {quantite}."
                )

            if len(produit.codes_barres) < quantite:
                raise ValidationError(
                    f"Pas assez de codes-barres disponibles pour le produit '{produit.nom}'. "
                    f"Disponibles : {len(produit.codes_barres)}, demandés : {quantite}."
                )

            codes_utilises = produit.codes_barres[:quantite]
            produit.codes_barres = produit.codes_barres[quantite:]

            prix_unitaire = float(produit.prix_vente_cache)
            sous_total = prix_unitaire * quantite

            LigneVenteCache.objects.create(
                vente=vente,
                produit=produit,
                quantite=quantite,
                prix_unitaire=prix_unitaire,
                sous_total=sous_total,
                codes_barres_utilises=codes_utilises
            )

            produit.quantite -= quantite
            produit.save()

            montant_total += sous_total

        vente.montant_total = montant_total
        vente.save()
        return vente
