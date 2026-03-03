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