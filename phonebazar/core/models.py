from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings
import uuid

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_admin', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser must have is_admin=True.')

        return self.create_user(email, password, **extra_fields)

# Create your models here.
class User(AbstractBaseUser):

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin
    
    email = models.EmailField(unique=True)
    role_choices = (
        ('Buyer', 'Buyer'),
        ('Seller', 'Seller'),
        ('Retailer', 'Retailer'),
    )
    role = models.CharField(max_length=20, choices=role_choices,default='Buyer')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    firstname = models.CharField(max_length=30, blank=True,null=True)
    lastname = models.CharField(max_length=30, blank=True,null=True)
    age = models.PositiveIntegerField(null=True, blank=True)    
    
    GENDER_CHOICES = (
        ('', 'Select Gender'), 
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

    gender = models.CharField(max_length=10,choices=GENDER_CHOICES,default='', blank=True,null=True)
    mobile_number = models.CharField(max_length=10, blank=True,null=True)

    objects = UserManager()

      #override userName filed
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.email

class PhoneListing(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='listings')
    brand = models.CharField(max_length=50)
    model_name = models.CharField(max_length=100)
    imei_number = models.CharField(max_length=15, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='phone_images/')
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand} {self.model_name}"

class TestReport(models.Model):
    # Using 'PhoneListing' as a string prevents ImportErrors
    listing = models.OneToOneField(
        'PhoneListing', 
        on_delete=models.CASCADE, 
        related_name='test_report'
    )
    tester = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        limit_choices_to={'is_staff': True}, 
        on_delete=models.SET_NULL, 
        null=True
    )
    functional_status = models.TextField()
    valuation_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_passed = models.BooleanField(default=False)
    report_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # We use self.listing because Django resolves the string automatically
        if self.is_passed:
            self.listing.is_verified = True
            self.listing.save()
        super().save(*args, **kwargs)
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending_test', 'Pending Functional Test'),
        ('escrow', 'Payment Held in Escrow'),
        ('shipped', 'In Transit'),
        ('delivered', 'Delivered to Buyer'),
        ('completed', 'Transaction Finalized'),
        ('disputed', 'Under Dispute'),
    )
    
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='purchases'
    )
    # PROTECT ensures we don't accidentally delete a listing that has a paid order
    phone_listing = models.ForeignKey('PhoneListing', on_delete=models.PROTECT)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_test')
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.phone_listing.model_name} ({self.get_status_display()})"

    class Meta:
        ordering = ['-created_at']

class Transaction(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Test'),
        ('held', 'Funds in Escrow'),
        ('completed', 'Finalized'),
        ('refunded', 'Refunded'),
    )
    listing = models.ForeignKey('PhoneListing', on_delete=models.PROTECT)
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='transactions'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True,null=True)

    def __str__(self):
        return f"TXN-{self.transaction_id} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            # Generate a unique ID like PB-UUID
            self.transaction_id = f"PB-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

class Feedback(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='feedback')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_feedback')
    
    phone_condition_rating = models.IntegerField(choices=RATING_CHOICES)
    communication_rating = models.IntegerField(choices=RATING_CHOICES)
    shipping_rating = models.IntegerField(choices=RATING_CHOICES)
    
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Using get_username() is safer than .username
        seller_name = self.seller.get_username() if self.seller else "Unknown Seller"
        order_id = self.order.id if self.order else "N/A"
        
        return f"Feedback for {seller_name} - Order #{order_id}"

    @property
    def average_rating(self):
        # Calculates the overall score for this transaction
        return round((self.phone_condition_rating + self.communication_rating + self.shipping_rating) / 3, 1)




    
