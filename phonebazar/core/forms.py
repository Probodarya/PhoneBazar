from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.contrib.auth import get_user_model
from .models import PhoneListing
class UserSignupForm(UserCreationForm):
    
    class Meta:
        model = User
        # Removed password1 and password2 from fields as UserCreationForm handles them
        fields = ['email', 'role', 'firstname', 'lastname', 'age', 'gender', 'mobile_number']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control custom-input',
                'placeholder': 'Enter your Email'
            }),
            'role': forms.Select(attrs={
                'class': 'form-control custom-input'
            }),
            
        }

        widgets = {
                'firstname': forms.TextInput(attrs={
                    'class': 'form-control custom-input',
                    'placeholder': 'Enter your First Name'
                }),
                'lastname': forms.TextInput(attrs={
                    'class': 'form-control custom-input',
                    'placeholder': 'Enter your Last Name'
                }),
                'age': forms.NumberInput(attrs={
                    'class': 'form-control custom-input',
                    'placeholder': 'Enter your Age'
                }),
                'gender': forms.Select(attrs={
                    'class': 'form-control custom-input'
                }),
                'mobile_number': forms.TextInput(attrs={
                    'class': 'form-control custom-input',
                    'placeholder': 'Enter your Mobile Number'
                })
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Cashify styling to the automatically generated password fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control custom-input',
                'placeholder': f'Enter {field.replace("_", " ").title()}'
            })

class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

User = get_user_model()

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('firstname', 'lastname', 'email', 'mobile_number') # Add 'phone' if you have it
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'mobile_number'}),

        }

# date 4/3/2026 working on post ad form
from django import forms
from .models import PhoneListing

BRAND_CHOICES = [
    ('', 'Select Brand'),
    ('Apple', 'Apple'),
    ('Samsung', 'Samsung'),
    ('Google', 'Google'),
    ('OnePlus', 'OnePlus'),
    ('Xiaomi', 'Xiaomi'),
    ('Vivo', 'Vivo'),
    ('Oppo', 'Oppo'),
]
class PhoneListingForm(forms.ModelForm):
    class Meta:
        model = PhoneListing
        # We include all fields the seller needs to fill out
        fields = ['brand', 'model_name', 'imei_number', 'price', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the phone condition...'}),
            'brand': forms.Select(choices=BRAND_CHOICES, attrs={'class': 'form-select', 'id': 'brand-select'}),
            'model_name': forms.Select(choices=[('', 'Select Model')], attrs={'class': 'form-select', 'id': 'model-select'}),
            'imei_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '15-digit IMEI number'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Set your price'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'},),
        }
from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['phone_condition_rating', 'communication_rating', 'shipping_rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'How was your experience?'}),
        }