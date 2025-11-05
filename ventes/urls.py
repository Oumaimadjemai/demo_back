from django.urls import path
from .views import *

urlpatterns = [
    path('ventes-facilite/', VenteFaciliteCreateAPIView.as_view()),
    path('ventes-facilite/<int:pk>/', VenteFaciliteRetrieveUpdateDestroyAPIView.as_view()),
    path("vente/payer/<int:pk>/", VentePaiementAPIView.as_view(), name="vente-payer"),
    path("vente/import-paiements-txt/", ImportPaiementsTxtAPIView.as_view(), name="import-paiements-txt"),
    path('ventes-facilite/<int:pk>/acte/word/', VenteFaciliteActeWordAPIView.as_view(), name='vente-facilite-acte-word'),
    path('ventes-facilite/<int:pk>/bon/word/', VenteFaciliteBonWordAPIView.as_view(), name='vente-facilite-bon-word'),
    path('ventes-cache/<int:pk>/bon/word/', VenteCashBonWordAPIView.as_view(), name='vente-cash-bon-word'),
     path('ventes-facilite/<int:pk>/depot/word/', VenteFaciliteDepotWordAPIView.as_view(), name='vente-facilite-depot-word'),
    path("ventes-facilite/<int:pk>/ccp/word/", VenteFaciliteCCPWordAPIView.as_view(), name="vente-facilite-ccp-word",),
     path('ventes-cache/', VenteCacheCreateAPIView.as_view(), name='ajouter-vente-cache'),
    path('liste/', VenteCacheListAPIView.as_view(), name='liste-vente-cache'),
    path('ventes-cache/<int:id>/', VenteCacheDetailAPIView.as_view(), name='vente-cache-detail'),
]
