from django.urls import path
from .views import *
urlpatterns = [
    path('par-group/', AchatGroupeListCreateAPIView.as_view(), name='achat-groupe-list-create'),
    path('par-group/<int:pk>/', AchatGroupeRetrieveUpdateDestroyAPIView.as_view(), name='achat-groupe-detail'),
    path('achats/', AchatListCreateAPIView.as_view(), name='achat-list-create'),
    path('achats/<int:pk>/', AchatRetrieveUpdateDestroyAPIView.as_view(), name='achat-detail'),

]
