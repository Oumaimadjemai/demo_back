from django.urls import path
from .views import *
urlpatterns = [
    path('magasins/', MagasinListCreateAPIView.as_view(), name='magasin-list-create'),
    path('magasins/<int:pk>/', MagasinRetrieveUpdateDestroyAPIView.as_view(), name='magasin-retrieve-update-destroy'),
]