
from rest_framework import serializers
from .models import Produit
from parametres.serializers import MagasinSerializer
import cloudinary.uploader

class ProduitSerializer(serializers.ModelSerializer):
    magasin_detail = MagasinSerializer(source='magasin', read_only=True)
    codebar_principal = serializers.SerializerMethodField()
    moyenne_pourcentage_facilite = serializers.SerializerMethodField()
    nouveaux_codes_barres = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False, allow_null=True)  # 👈 allow null

    class Meta:
        model = Produit
        fields = [
            'id','reference', 'codes_barres', 'codebar_principal', 'nom', 'famille',
            'magasin', 'magasin_detail', 'marque', 'image', 'prix_achat',
            'taux_benefice_cache', 'prix_vente_cache',
            'taux_benefice_3', 'taux_benefice_5',
            'taux_benefice_8', 'taux_benefice_10',
            'taux_benefice_6', 'taux_benefice_9',
            'taux_benefice_12', 'taux_benefice_15',
            'prix_vente_6', 'prix_vente_9',
            'prix_vente_12', 'prix_vente_15',
            'prix_vente_3', 'prix_vente_5',
            'prix_vente_8', 'prix_vente_10',
            'quantite', 'date_creation',
            'date_modification', 'moyenne_pourcentage_facilite',
            'nouveaux_codes_barres','est_supprime',
        ]
        extra_kwargs = {
            'magasin': {'write_only': True}
        }

    def get_codebar_principal(self, obj):
        return obj.codebar_principal

    def get_moyenne_pourcentage_facilite(self, obj):
        return obj.moyenne_pourcentage_facilite

    def get_nouveaux_codes_barres(self, obj):
        return getattr(obj, 'nouveaux_codes_barres', [])

    def validate_codes_barres(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Doit être une liste de codes-barres")
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Les codes-barres doivent être uniques")
        return value

    def update(self, instance, validated_data):
        # 👇 Handle clearing image
        if 'image' in validated_data:
            if validated_data['image'] in ["", None]:
                if instance.image:  
                    # Extract public_id from CloudinaryField
                    public_id = str(instance.image.public_id)
                    if public_id:
                        cloudinary.uploader.destroy(public_id)  # ✅ delete from Cloudinary
                validated_data['image'] = None

        return super().update(instance, validated_data)

class ProduitMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = ['id', 'reference', 'nom', 'codes_barres', 'quantite', 'est_supprime']
