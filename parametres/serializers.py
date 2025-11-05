from rest_framework import serializers
from .models import *

class MagasinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Magasin
        fields = '__all__'