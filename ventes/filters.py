import django_filters
from .models import VenteCache
from django.utils.timezone import now
from datetime import timedelta

class VenteCacheFilter(django_filters.FilterSet):
    # Dates
    date_from = django_filters.DateFilter(field_name='date_vente', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='date_vente', lookup_expr='lte')
    
    # Utilisateur
    users = django_filters.NumberFilter(field_name='utilisateur', lookup_expr='exact')
    client = django_filters.NumberFilter(field_name='client',lookup_expr='exact')

    
    # Period quick filter
    periode = django_filters.CharFilter(method='filter_periode')
    produit = django_filters.NumberFilter(method='filter_produit')


    class Meta:
        model = VenteCache
        fields = ['users', 'date_from', 'date_to', 'periode','produit','client']

    def filter_periode(self, queryset, name, value):
        """Filtrage rapide par période"""
        today = now().date()

        if value == "today":
            return queryset.filter(date_vente__date=today)
        elif value == "yesterday":
            return queryset.filter(date_vente__date=today - timedelta(days=1))
        elif value == "this_week":
            start_week = today - timedelta(days=today.weekday())
            return queryset.filter(date_vente__date__gte=start_week)
        elif value == "this_month":
            return queryset.filter(date_vente__year=today.year, date_vente__month=today.month)
        elif value == "last_month":
            month = today.month - 1 or 12
            year = today.year if today.month > 1 else today.year - 1
            return queryset.filter(date_vente__year=year, date_vente__month=month)
        elif value == "this_year":
            return queryset.filter(date_vente__year=today.year)

        return queryset
    def filter_produit(self, queryset, name, value):
        """
        Filtrer les ventes qui contiennent un produit spécifique dans leurs lignes
        """
        if value:
            return queryset.filter(lignes__produit=value).distinct()
        return queryset
    
# filters.py
import django_filters
from .models import VenteFacilite
from django.utils.timezone import now
from datetime import timedelta


class VenteFaciliteFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='date_creation', lookup_expr='gte')
    date_to = django_filters.DateFilter(method='filter_date_to')
    users = django_filters.NumberFilter(field_name='utilisateur', lookup_expr='exact')
    client = django_filters.NumberFilter(field_name='client',lookup_expr='exact')
    periode = django_filters.CharFilter(method='filter_periode')
    produit = django_filters.NumberFilter(method='filter_produit')

    class Meta:
        model = VenteFacilite
        fields = ['users', 'date_from', 'date_to', 'periode','produit','client']

    def filter_date_to(self, queryset, name, value):
        """Include the full day for date_to"""
        if value:
            return queryset.filter(date_creation__lt=value + timedelta(days=1))
        return queryset


    def filter_periode(self, queryset, name, value):
        """Quick period filtering"""
        today = now().date()

        if value == "today":
            return queryset.filter(date_creation__date=today)
        elif value == "yesterday":
            return queryset.filter(date_creation__date=today - timedelta(days=1))
        elif value == "this_week":
            start_week = today - timedelta(days=today.weekday())
            return queryset.filter(date_creation__date__gte=start_week)
        elif value == "this_month":
            return queryset.filter(date_creation__year=today.year, date_creation__month=today.month)
        elif value == "last_month":
            month = today.month - 1 or 12
            year = today.year if today.month > 1 else today.year - 1
            return queryset.filter(date_creation__year=year, date_creation__month=month)
        elif value == "this_year":
            return queryset.filter(date_creation__year=today.year)
        return queryset
    def filter_produit(self, queryset, name, value):
        """
        Filtrer les ventes qui contiennent un produit spécifique dans leurs lignes
        """
        if value:
            return queryset.filter(lignes__produit=value).distinct()
        return queryset
