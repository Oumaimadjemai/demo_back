from django.urls import path
from .views import TransfertListView, TransfertDetailView

urlpatterns = [
    path('transferts/', TransfertListView.as_view(), name='transfert-list'),
    path('transferts/<int:pk>/', TransfertDetailView.as_view(), name='transfert-detail'),
]