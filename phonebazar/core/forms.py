from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserSignupForm(UserCreationForm):
    class Meta:
        model = User
        # Removed password1 and password2 from fields as UserCreationForm handles them
        fields = ['email', 'role']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control custom-input',
                'placeholder': 'Enter your Email'
            }),
            'role': forms.Select(attrs={
                'class': 'form-control custom-input'
            }),
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