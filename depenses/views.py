from rest_framework import generics
from .models import Depense
from .serializers import DepenseSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from rest_framework.response import Response
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from datetime import date, timedelta
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta


class DepenseListCreateAPIView(generics.ListCreateAPIView):
    queryset = Depense.objects.all()
    serializer_class = DepenseSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['libelle']  # champ utilisé pour ?search=
    filterset_fields = [ 'type_depense', 'mode_paiement', 'date']  # pour filtrer par query params

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['queryset'] = self.get_queryset()
        context['many'] = True
        return context

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())  # 🔴 IMPORTANT pour activer les filtres/recherche

        serializer = self.get_serializer(queryset, many=True)

        aggregates = queryset.aggregate(
            total_montant=Sum('montant'),
            total_depenses=Count('id')
        )

        return Response({
            "rows": serializer.data,
            "totaux_globaux": {
                "total_montant": aggregates['total_montant'] or 0,
                "total_depenses": aggregates['total_depenses'] or 0
            }
        })
    
    def get_queryset(self):
      queryset = Depense.objects.all()
      request = self.request
      periode = request.query_params.get('periode')
      date_from = request.query_params.get('date_from')  # format: YYYY-MM-DD
      date_to = request.query_params.get('date_to')      # format: YYYY-MM-DD

      today = date.today()

    # 📌 Intervalle personnalisé prioritaire
      if date_from and date_to:
        queryset = queryset.filter(date__range=(date_from, date_to))
      elif periode == "today":
        queryset = queryset.filter(date=today)
      elif periode == "yesterday":
        queryset = queryset.filter(date=today - timedelta(days=1))
      elif periode == "this_week":
        start = today - timedelta(days=today.weekday())
        queryset = queryset.filter(date__gte=start)
      elif periode == "this_month":
        start = today.replace(day=1)
        queryset = queryset.filter(date__gte=start)
      elif periode == "last_month":
        first_day_this_month = today.replace(day=1)
        last_month = first_day_this_month - timedelta(days=1)
        start = last_month.replace(day=1)
        end = last_month
        queryset = queryset.filter(date__range=(start, end))
      elif periode == "this_year":
        start = today.replace(month=1, day=1)
        queryset = queryset.filter(date__gte=start)

      return queryset


# Détail + Mise à jour + Suppression
class DepenseRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Depense.objects.all()
    serializer_class = DepenseSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['queryset'] = self.get_queryset()
        context['many'] = True
        return context
