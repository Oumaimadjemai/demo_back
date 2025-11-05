from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/', CustomUserListView.as_view(), name='user-list-create'),
    path('users/<int:id>/', CustomUserDetailView.as_view(), name='user-detail'),
    path('clients/', ClientListCreateView.as_view(), name='client-list-create'),
    path('clients/<int:pk>/', ClientRetrieveUpdateDestroyView.as_view(), name='client-retrieve-update-destroy'),
    path('clients/export-excel/', ClientExportExcelView.as_view(), name='export-clients-excel'),
    path('clients/import-excel/', ClientImportExcelView.as_view(), name='import-clients-excel'),
    path('clients/files/<int:pk>/', FichierClientDeleteAPIView.as_view(), name='client-file-delete'),
    path('fournisseurs/', FournisseurListCreateView.as_view(), name='fournisseur-list-create'),
    path('fournisseurs/<int:pk>/', FournisseurRetrieveUpdateDestroyView.as_view(), name='fournisseur-retrieve-update-destroy'),
    path('fournisseurs/export/', FournisseurExportExcelView.as_view(), name='fournisseur-export'),
    path('fournisseurs/import/', FournisseurImportExcelView.as_view(), name='fournisseur-import'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('admin/change-password/', AdminChangeUserPasswordView.as_view(), name='admin-change-password'),
    path('clients/files/<int:pk>/download/', download_fichier_client, name='download_fichier_client'),
     path('chat/', ChatAPIView.as_view(), name='chat'),
]
