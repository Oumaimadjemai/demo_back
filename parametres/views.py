from rest_framework import generics
from .models import Magasin
from .serializers import MagasinSerializer

class MagasinListCreateAPIView(generics.ListCreateAPIView):
    """
    GET: List all Magasins
    POST: Create a new Magasin
    """
    queryset = Magasin.objects.all()
    serializer_class = MagasinSerializer

class MagasinRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a Magasin
    PUT: Update a Magasin
    PATCH: Partially update a Magasin
    DELETE: Destroy a Magasin
    """
    queryset = Magasin.objects.all()
    serializer_class = MagasinSerializer
    lookup_field = 'pk'  # default is 'pk' so this is optional