# filters.py
import django_filters
from .models import Transfert

class TransfertFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(field_name="date", lookup_expr="date")
    date_gte = django_filters.DateFilter(field_name="date", lookup_expr="date__gte")
    date_lte = django_filters.DateFilter(field_name="date", lookup_expr="date__lte")

    class Meta:
        model = Transfert
        fields = {
            'magasin_source': ['exact'],
            'magasin_destination': ['exact'],

            # On ne met pas "date" ici, car on gère manuellement les variantes
        }
