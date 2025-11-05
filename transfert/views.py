from produits.models import Produit
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Transfert
from .serializers import TransfertSerializer
from rest_framework.filters import SearchFilter
from django.db.models import Q


from .filters import TransfertFilter


# class TransfertListView(generics.ListCreateAPIView):
#     queryset = Transfert.objects.select_related(
#         'produit', 'magasin_source', 'magasin_destination', 'utilisateur'
#     )
#     serializer_class = TransfertSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     filter_backends = [DjangoFilterBackend, SearchFilter]

#     filterset_class = TransfertFilter  # ⬅️ Ajout ici
#     search_fields = [
#         'produit__nom',
#         'codes_barres_transferes',
#     ]

#     def get_queryset(self):
#         queryset = super().get_queryset()
#         search_term = self.request.query_params.get('search', None)

#         if search_term:
#             queryset = queryset.filter(
#                 Q(produit__nom__icontains=search_term) |
#                 Q(codes_barres_transferes__icontains=search_term)
#             )
#         return queryset
from django.db.models import Q
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Transfert
from .serializers import TransfertSerializer
from .filters import TransfertFilter


class TransfertListView(generics.ListCreateAPIView):
    queryset = Transfert.objects.select_related(
        'produit', 'magasin_source', 'magasin_destination', 'utilisateur'
    ).all()
    serializer_class = TransfertSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Correct import for filters
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = TransfertFilter

    # Fields that can be searched with ?search=
    search_fields = ['produit__nom', 'codes_barres_transferes']

    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.query_params.get('search', None)

        # ✅ Only filter manually if no SearchFilter is handling it
        if search_term:
            queryset = queryset.filter(
                Q(produit__nom__icontains=search_term) |
                Q(codes_barres_transferes__icontains=search_term)
            )

        return queryset

# class TransfertDetailView(generics.RetrieveDestroyAPIView):
#     queryset = Transfert.objects.select_related(
#         'produit', 'magasin_source', 'magasin_destination', 'utilisateur'
#     )
#     serializer_class = TransfertSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def destroy(self, request, *args, **kwargs):
#      instance = self.get_object()

#      if instance.produit_supprime:
#         return Response(
#             {"detail": "Impossible d'annuler le transfert : le produit a été supprimé."},
#             status=status.HTTP_400_BAD_REQUEST
#         )

#      produit_source = instance.produit
#      produit_source.quantite += instance.quantite
#      if instance.codes_barres_transferes:
#         produit_source.codes_barres += instance.codes_barres_transferes
#      produit_source.est_supprime = False
#      produit_source.save()

#     # Gérer suppression du produit destination
#      try:
#         produit_dest = Produit.objects.get(
#             nom=produit_source.nom,
#             marque=produit_source.marque,
#             magasin=instance.magasin_destination
#         )
#         produit_dest.quantite -= instance.quantite
#         if instance.codes_barres_transferes:
#             produit_dest.codes_barres = [
#                 code for code in produit_dest.codes_barres
#                 if code not in instance.codes_barres_transferes
#             ]
#         if produit_dest.quantite <= 0:
#             produit_dest.est_supprime = True
#         produit_dest.save()
#      except Produit.DoesNotExist:
#         pass

#      return super().destroy(request, *args, **kwargs)
from django.db import transaction
from rest_framework import generics, permissions
from django.core.exceptions import ValidationError
from produits.models import Produit
from .models import Transfert
from .serializers import TransfertSerializer


class TransfertDetailView(generics.RetrieveDestroyAPIView):
    queryset = Transfert.objects.select_related(
        'produit', 'magasin_source', 'magasin_destination', 'utilisateur'
    )
    serializer_class = TransfertSerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        produit_source = instance.produit

        # ✅ Step 1 — Reactivate if deleted
        if produit_source.est_supprime:
            produit_source.est_supprime = False

        # ✅ Step 2 — Restore quantity
        produit_source.quantite += instance.quantite

        # ✅ Step 3 — Handle codebarre rollback
        if instance.codes_barres_transferes:
            for code in instance.codes_barres_transferes:
                try:
                    # Check if this code exists in another product
                    produit_avec_code = Produit.objects.get(codes_barres__contains=[code])
                    
                    # If it's not the same as produit_source → remove it
                    if produit_avec_code.id != produit_source.id:
                        # Remove this barcode from the other product
                        produit_avec_code.codes_barres.remove(code)
                        
                        # If no barcodes left, mark as deleted
                        if not produit_avec_code.codes_barres:
                            produit_avec_code.est_supprime = True
                        
                        produit_avec_code.save()
                        
                        # Add it to produit_source
                        if code not in produit_source.codes_barres:
                            produit_source.codes_barres.append(code)

                except Produit.DoesNotExist:
                    # If not found anywhere, just add it back normally
                    if code not in produit_source.codes_barres:
                        produit_source.codes_barres.append(code)

        produit_source.save()

        # ✅ Step 4 — Adjust destination product
        try:
            produit_dest = Produit.objects.get(
                nom=produit_source.nom,
                marque=produit_source.marque,
                magasin=instance.magasin_destination
            )

            produit_dest.quantite -= instance.quantite

            # Remove rollbacked barcodes from destination
            if instance.codes_barres_transferes:
                produit_dest.codes_barres = [
                    c for c in produit_dest.codes_barres
                    if c not in instance.codes_barres_transferes
                ]

            if produit_dest.quantite <= 0 or not produit_dest.codes_barres:
                produit_dest.est_supprime = True

            produit_dest.save()

        except Produit.DoesNotExist:
            pass

        # ✅ Step 5 — Delete the transfer record
        return super().destroy(request, *args, **kwargs)
