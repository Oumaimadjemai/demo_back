from django.urls import path
from .views import *

urlpatterns = [
    path('depenses/', DepenseListCreateAPIView.as_view(), name='depense-list-create'),
    path('depenses/<int:pk>/', DepenseRetrieveUpdateDestroyAPIView.as_view(), name='depense-detail'),
]
