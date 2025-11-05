

from rest_framework import serializers
from .models import Depense
from django.db.models import Sum, Count
from authentification.serializers import CustomUserSerializer

class DepenseSerializer(serializers.ModelSerializer):
    utilisateur = CustomUserSerializer(read_only=True)

    class Meta:
        model = Depense
        fields = '__all__'
        read_only_fields = ['utilisateur']
        # extra_fields = ['total_montant', 'total_depenses']

   