from django.urls import path
from .views import*

urlpatterns = [
    path('produits/', ProduitListCreateAPIView.as_view(), name='produit-list-create'),
    path('produits/<int:pk>/', ProduitRetrieveUpdateDestroyAPIView.as_view(), name='produit-detail'),
    path("produits/export-excel/", ExportProduitExcelView.as_view(), name="produits-export"),
    path("produits/import-excel/", ImportProduitExcelView.as_view(), name="produits-import"),
    path('comparaison/', ProduitComparaisonView.as_view(), name='produits-comparaison'),
     path('produits/familles/', FamillesProduitView.as_view(), name='produits-familles'), 
     path("import-prix/", importer_prix_produits, name="import-prix"),
]
