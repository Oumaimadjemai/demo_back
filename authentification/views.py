from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics
from .models import *
from .serializers import *
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.parsers import MultiPartParser, FormParser,JSONParser
from rest_framework.permissions import IsAuthenticated 
from rest_framework import filters
from import_export.formats.base_formats import XLSX
from django.http import HttpResponse
from .resources import *

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache

class RegisterAPIView(APIView):
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = CustomUser.objects.create_user(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password'],
                role=serializer.validated_data['role']
            )
            return Response({'message': 'Utilisateur créé avec succès.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from .serializers import CustomUserSerializer

class CustomUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'  # or 'pk'


from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from .serializers import CustomUserSerializer

class CustomUserListView(generics.ListAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        role = self.request.query_params.get('role') or self.request.query_params.get('type')
        queryset = CustomUser.objects.all()
        if role:
            queryset = queryset.filter(role__iexact=role.strip())  # ignore case & spaces
        return queryset


# login
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user_data = CustomUserSerializer(self.user).data
        data.update({'user': user_data})
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# crud client
from rest_framework.response import Response
from datetime import timedelta, date
from django.utils.timezone import now

class ClientListCreateView(generics.ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'ccp', 'nom_famille_fr', 'prenom_fr',
        'nom_famille_ar', 'prenom_ar'
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        periode = self.request.query_params.get('periode')
        statut = self.request.query_params.get('statut')
        bloque = self.request.query_params.get('bloque')
        if statut:
          queryset = queryset.filter(statut=statut)
        if bloque is not None:
          queryset = queryset.filter(bloque=bloque.lower() in ['true', '1'])
        today = now().date()

        if periode:
            start_date, end_date = None, None

            if periode == "today":
                start_date = end_date = today

            elif periode == "yesterday":
                start_date = end_date = today - timedelta(days=1)

            elif periode == "this_week":
                start_date = today - timedelta(days=today.weekday())  # Monday
                end_date = today

            elif periode == "this_month":
                start_date = today.replace(day=1)
                end_date = today

            elif periode == "last_month":
                first_day_this_month = today.replace(day=1)
                last_day_last_month = first_day_this_month - timedelta(days=1)
                start_date = last_day_last_month.replace(day=1)
                end_date = last_day_last_month

            elif periode == "this_year":
                start_date = date(today.year, 1, 1)
                end_date = today

            elif periode == "last_year":
                start_date = date(today.year - 1, 1, 1)
                end_date = date(today.year - 1, 12, 31)

            elif periode == "3months":
                start_date = today - timedelta(days=90)
                end_date = today

            if start_date and end_date:
                queryset = queryset.filter(date_creation__date__range=[start_date, end_date])

        return queryset.order_by("-date_creation")
    
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page,many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)

        total_clients = queryset.count()

        return Response({
            "total_clients": total_clients,
            "results": serializer.data
        })

class FichierClientDeleteAPIView(generics.DestroyAPIView):
    """
    API to delete a client's file.
    """
    queryset = FichierClient.objects.all()
    serializer_class = FichierClientSerializer
    permission_classes = [IsAuthenticated]
   

class ClientRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]
   

from import_export import resources
from import_export.formats.base_formats import XLSX
from .models import Client
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

class ClientResource(resources.ModelResource):
    class Meta:
        model = Client
        # Liste de tous les champs que tu veux exporter
        fields = (
            'id',
            'assurance_militaire',
            'date_expedition',
            'nom_famille_ar',
            'prenom_ar',
            'nom_famille_fr',
            'prenom_fr',
            'nom_pere',
            'nom_mere',
            'numero_national',
            'date_naissance',
            'lieu_naissance',
            'adresse',
            'telephone',
            'profession',
            'revenu',
            'type_piece_identite',
            'numero_piece_identite',
            'date_emission_piece',
            'lieu_emission_piece',
            'ccp',
            'cle',
            'code',
            'dette_initiale',
            'note',
            'statut',
            'bloque',
            'date_creation',
            'date_modification',
            'jour',
        )
class ClientExportExcelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        client_resource = ClientResource()
        dataset = client_resource.export()
        export_data = XLSX().export_data(dataset)  # génère le fichier Excel

        response = HttpResponse(
            export_data,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="clients.xlsx"'
        return response

    
class ClientImportExcelView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({"detail": "Fichier manquant"}, status=status.HTTP_400_BAD_REQUEST)

        resource = ClientResource()
        dataset = resource.get_format('xlsx').create_dataset(file.read())
        result = resource.import_data(dataset, dry_run=True)  # test first

        if result.has_errors():
            return Response({"detail": "Erreur dans les données", "errors": result.row_errors()}, status=400)

        # Apply import
        resource.import_data(dataset, dry_run=False)
        return Response({"detail": "Importation réussie"}, status=200)

#crud fournisseur
# views.py


class FournisseurListCreateView(generics.ListCreateAPIView):
    queryset = Fournisseur.objects.all()
    serializer_class = FournisseurSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['nom', 'adresse', 'telephone']
    filterset_fields = ['wilaya']

    def perform_create(self, serializer):
        serializer.save()

class FournisseurRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Fournisseur.objects.all()
    serializer_class = FournisseurSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        serializer.save()  # Logique supplémentaire possible lors de la mise à jour

from import_export import resources
from .models import Fournisseur

class FournisseurResource(resources.ModelResource):
    class Meta:
        model = Fournisseur
        # Tous les champs que tu veux exporter
        fields = (
            'id',
            'nom',
            'adresse',
            'telephone',
            'wilaya',
            'dettes_initiales',
            'date_creation',
            'date_modification',
        )
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from import_export.formats.base_formats import XLSX
from django.http import HttpResponse

class FournisseurExportExcelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        fournisseur_resource = FournisseurResource()
        dataset = fournisseur_resource.export()       # récupère les données
        export_data = XLSX().export_data(dataset)    # convertit en XLSX

        response = HttpResponse(
            export_data,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="fournisseurs.xlsx"'
        return response



class FournisseurImportExcelView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({"detail": "Fichier manquant"}, status=status.HTTP_400_BAD_REQUEST)

        fournisseur_resource = FournisseurResource()
        dataset = fournisseur_resource.get_format('xlsx').create_dataset(file.read())
        result = fournisseur_resource.import_data(dataset, dry_run=True)

        if result.has_errors():
            return Response({"detail": "Erreur dans les données", "errors": result.row_errors()}, status=400)

        fournisseur_resource.import_data(dataset, dry_run=False)
        return Response({"detail": "Importation réussie"}, status=200)
    

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response({'detail': 'Champs manquants'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(old_password):
            return Response({'detail': 'Ancien mot de passe incorrect'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Mot de passe modifié avec succès'}, status=status.HTTP_200_OK)
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.views import APIView

class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            # Ignorer les erreurs pour rendre la déconnexion idempotente
            pass

        return Response({"detail": "Déconnexion réussie."}, status=status.HTTP_200_OK)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

User = get_user_model()

class AdminChangeUserPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not hasattr(request.user, 'role') or request.user.role != 'admin':
            return Response({'detail': "Accès refusé. Vous n'êtes pas administrateur."}, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get('user_id')
        new_password = request.data.get('new_password')

        if not user_id or not new_password:
            return Response({'detail': 'Champs manquants'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'Utilisateur introuvable'}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Mot de passe de l\'utilisateur modifié avec succès'}, status=status.HTTP_200_OK)
from cloudinary.utils import cloudinary_url

def get_signed_download_url(fichier):
    public_id = fichier.fichier.public_id
    format = fichier.fichier.format
    resource_type = fichier.fichier.resource_type or "raw"

    url, options = cloudinary_url(
        public_id,
        format=format,
        resource_type=resource_type,
        type="authenticated",  # ou "private" selon ton paramétrage
        sign_url=True,
        flags="attachment"     # ✅ Force le téléchargement
    )
    return url
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from .models import FichierClient

# def download_fichier_client(request, pk):
#     fichier = get_object_or_404(FichierClient, pk=pk)
#     if not fichier.fichier:
#         raise Http404("File not found")

#     signed_url = get_signed_download_url(fichier)
#     return JsonResponse({"url": signed_url})
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from .models import FichierClient

def download_fichier_client(request, pk):
    fichier = get_object_or_404(FichierClient, pk=pk)
    if not fichier.fichier:
        raise Http404("File not found")
    
    # ✅ Cloudinary gives a direct URL
    return HttpResponseRedirect(fichier.fichier.url)
# views.py
import os
from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class ChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_message = request.data.get("message")
        if not user_message:
            return Response({"error": "Message is required"}, status=400)

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",  # Accessible model
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_message}
                ]
            )
            answer = response.choices[0].message.content
            return Response({"reply": answer})

        except openai.OpenAIError as e:  # Correct exception
            return Response({"error": str(e)}, status=500)
