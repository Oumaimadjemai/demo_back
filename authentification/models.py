from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, role=None, **extra_fields):
        if not username:
            raise ValueError("Le nom d'utilisateur est requis.")
        user = self.model(username=username, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, role='super-admin', **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, role, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLES = [
        ('admin', 'Admin'),
        ('vendeur', 'Vendeur'),
        ('magasinier', 'Magasinier'),
    ]

    username = models.CharField(max_length=150, unique=True)
    role = models.CharField(max_length=20, choices=ROLES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    features = models.JSONField(default=list, blank=True) 
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['role']

    objects = UserManager()

    def __str__(self):
        return f"{self.username} ({self.role})"
    def has_feature(self, feature_name):
        return feature_name in self.features



TYPE_PIECE_IDENTITE = [
    ('بطاقة التعريف الوطنية ', 'بطاقة التعريف الوطنية / Carte d\'identité'),
    ('جواز السفر ', 'جواز السفر / Passeport'),
    ('رخصة السياقة ', 'رخصة السياقة / Permis de conduire'),
]

class Client(models.Model):
    # Informations personnelles (bilingues)
    assurance_militaire = models.CharField(max_length=50, verbose_name="assurance",null=True)
    date_expedition = models.DateField(verbose_name="date_expedition",null=True)
    nom_famille_ar = models.CharField(max_length=100, verbose_name="اللقب (عربي)",null=True)
    prenom_ar = models.CharField(max_length=100, verbose_name="الاسم (عربي)",null=True)
    nom_famille_fr = models.CharField(max_length=100, verbose_name="Nom de famille (français)",null=True)
    prenom_fr = models.CharField(max_length=100, verbose_name="Prénom (français)",null=True)
    
    # Parenté
    nom_pere = models.CharField(max_length=100, verbose_name="إسم الأب / Nom du père",null=True)
    nom_mere = models.CharField(max_length=100, verbose_name="إسم الأم / Nom de la mère",null=True)
    
    # Identification
    numero_national = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="الرقم الوطني / Numéro national",
        null=True
    )
    date_naissance = models.DateField(verbose_name="تاريخ الازدياد / Date de naissance",null=True)
    lieu_naissance = models.CharField(
        max_length=100, 
        verbose_name="مكان الازدياد / Lieu de naissance",
        null=True
    )
    
    # Coordonnées
    adresse = models.TextField(verbose_name="العنوان / Adresse")
    telephone = models.CharField(
        max_length=20,
        verbose_name="رقم الهاتف / Téléphone",
        validators=[RegexValidator(r'^[0-9+]+$', 'Numéro de téléphone invalide')],
        null=True
    )
    
    # Profession et revenu
    profession = models.CharField(max_length=100, verbose_name="المهنة / Profession")
    revenu = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="الدخل / Revenu"
    )
    
    # Pièce d'identité (détaillée)
    type_piece_identite = models.CharField(
        max_length=100,
        choices=TYPE_PIECE_IDENTITE,
        verbose_name="نوع وثيقة التعريف / Type de pièce",
    )
    numero_piece_identite = models.CharField(
        max_length=100, 
        verbose_name="رقم الوثيقة / Numéro de pièce",
        null=True
    )
    date_emission_piece = models.DateField(
        verbose_name="تاريخ الإصدار / Date d'émission",
        null=True
    )
    jour=models.CharField(max_length=2,null=True)
    lieu_emission_piece = models.CharField(
        max_length=100, 
        verbose_name="مكان الإصدار / Lieu d'émission",
        blank=True,
        null=True
    )
    
    # Informations bancaires
    ccp = models.CharField(
        max_length=50, 
        verbose_name="رقم الحساب البنكي / Numéro de compte", 
        blank=True, 
        null=True,
    )
    cle = models.CharField(
        max_length=2, 
        verbose_name="المفتاح / Clé", 
        blank=True, 
        null=True,
        validators=[MinLengthValidator(2)]
    )
    code = models.CharField(
        max_length=50, 
        verbose_name="الرمز السري / Code secret", 
        blank=True, 
        null=True
    )
    
    # Autres informations
    dette_initiale = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="ديون ابتدائية / Dette initiale", 
        default=0
    )
    note = models.TextField(
        verbose_name="ملاحظات / Notes", 
        blank=True, 
        null=True
    )
    statut = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="الحالة / Statut"
    )

    bloque = models.BooleanField(
        default=False,
        verbose_name="محظور / Bloqué"
    )
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True,null=True)
    date_modification = models.DateTimeField(auto_now=True,null=True)

    def __str__(self):
        return f"{self.nom_famille_fr} {self.prenom_fr} - {self.numero_national}"
    
    def clean(self):
        """Validation des données avant enregistrement"""
      
        
        # Vérification CCP + Clé
        if self.ccp and not self.cle:
            raise ValidationError("المفتاح مطلوب عند إدخال رقم الحساب / La clé est requise avec le numéro de compte")
            
        # Vérification date expiration > date émission
        if (self.date_expiration_piece and 
            self.date_expiration_piece <= self.date_emission_piece):
            raise ValidationError("تاريخ انتهاء الصلاحية يجب أن يكون بعد تاريخ الإصدار / La date d'expiration doit être après la date d'émission")
    
    class Meta:
        verbose_name = "عميل / Client"
        verbose_name_plural = "العملاء / Clients"
        ordering = ['nom_famille_fr', 'prenom_fr']

# class FichierClient(models.Model):
    
    
#     client = models.ForeignKey(
#         Client, 
#         related_name='fichiers', 
#         on_delete=models.CASCADE
#     )
#     fichier = models.FileField(
#         upload_to='client_files/%Y/%m/%d/', 
#         verbose_name="ملف مرفق / Fichier joint"
#     )

from cloudinary.models import CloudinaryField

class FichierClient(models.Model):
    client = models.ForeignKey(Client, related_name='fichiers', on_delete=models.CASCADE)
    fichier = CloudinaryField(
        resource_type='raw',    # ✅ handles pdf/images
        folder='client_files',  # ✅ store in folder
        type='upload',          # ✅ public (not private/authenticated)
        verbose_name="ملف مرفق / Fichier joint"
    )

    


   



class Fournisseur(models.Model):
    # Liste des 58 wilayas d'Algérie avec code et nom en français/arabe
    WILAYAS_CHOICES = [
        ('01', 'Adrar / أدرار'),
        ('02', 'Chlef / الشلف'),
        ('03', 'Laghouat / الأغواط'),
        ('04', 'Oum El Bouaghi / أم البواقي'),
        ('05', 'Batna / باتنة'),
        ('06', 'Béjaïa / بجاية'),
        ('07', 'Biskra / بسكرة'),
        ('08', 'Béchar / بشار'),
        ('09', 'Blida / البليدة'),
        ('10', 'Bouira / البويرة'),
        ('11', 'Tamanrasset / تمنراست'),
        ('12', 'Tébessa / تبسة'),
        ('13', 'Tlemcen / تلمسان'),
        ('14', 'Tiaret / تيارت'),
        ('15', 'Tizi Ouzou / تيزي وزو'),
        ('16', 'Alger / الجزائر'),
        ('17', 'Djelfa / الجلفة'),
        ('18', 'Jijel / جيجل'),
        ('19', 'Sétif / سطيف'),
        ('20', 'Saïda / سعيدة'),
        ('21', 'Skikda / سكيكدة'),
        ('22', 'Sidi Bel Abbès / سيدي بلعباس'),
        ('23', 'Annaba / عنابة'),
        ('24', 'Guelma / قالمة'),
        ('25', 'Constantine / قسنطينة'),
        ('26', 'Médéa / المدية'),
        ('27', 'Mostaganem / مستغانم'),
        ('28', 'M\'Sila / المسيلة'),
        ('29', 'Mascara / معسكر'),
        ('30', 'Ouargla / ورقلة'),
        ('31', 'Oran / وهران'),
        ('32', 'El Bayadh / البيض'),
        ('33', 'Illizi / إيليزي'),
        ('34', 'Bordj Bou Arréridj / برج بوعريريج'),
        ('35', 'Boumerdès / بومرداس'),
        ('36', 'El Tarf / الطارف'),
        ('37', 'Tindouf / تندوف'),
        ('38', 'Tissemsilt / تسمسيلت'),
        ('39', 'El Oued / الوادي'),
        ('40', 'Khenchela / خنشلة'),
        ('41', 'Souk Ahras / سوق أهراس'),
        ('42', 'Tipaza / تيبازة'),
        ('43', 'Mila / ميلة'),
        ('44', 'Aïn Defla / عين الدفلى'),
        ('45', 'Naâma / النعامة'),
        ('46', 'Aïn Témouchent / عين تيموشنت'),
        ('47', 'Ghardaïa / غرداية'),
        ('48', 'Relizane / غليزان'),
        ('49', 'Timimoun / تيميمون'),
        ('50', 'Bordj Badji Mokhtar / برج باجي مختار'),
        ('51', 'Ouled Djellal / أولاد جلال'),
        ('52', 'Béni Abbès / بني عباس'),
        ('53', 'In Salah / عين صالح'),
        ('54', 'In Guezzam / عين قزام'),
        ('55', 'Touggourt / تقرت'),
        ('56', 'Djanet / جانت'),
        ('57', 'El M\'Ghair / المغير'),
        ('58', 'El Menia / المنيعة'),
    ]

    # Informations de base
    nom = models.CharField(max_length=100, verbose_name="اسم الممون")
    adresse = models.TextField(verbose_name="عنوان الممون")
    telephone = models.CharField(
        max_length=20,
        verbose_name="رقم الهاتف",
        validators=[RegexValidator(r'^[0-9+]+$', 'رقم الهاتف غير صالح')]
    )
    wilaya = models.CharField(
        max_length=2,
        choices=WILAYAS_CHOICES,
        verbose_name="الولاية"
    )
    # Dettes et finances
    dettes_initiales = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="الديون الأولية",
        validators=[MinValueValidator(0)],
        help_text="المبلغ الابتدائي للديون عند إضافة الممون"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        wilaya_nom = dict(self.WILAYAS_CHOICES).get(self.wilaya, '')
        return f"{self.nom} - {wilaya_nom.split(' / ')[1] if wilaya_nom else ''}"

    class Meta:
        verbose_name = "ممون"
        verbose_name_plural = "الممونون"
        ordering = ['nom']