from django.shortcuts import render,redirect,HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from .forms import UserSignupForm,UserLoginForm
from django.contrib.auth import authenticate,login
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import os
from django.contrib.auth import logout
from .forms import EditProfileForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def userSignupView(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST or None)
        if form.is_valid():
            user = form.save()  # Save the user to the database
            email_address = form.cleaned_data['email']
            first_name = form.cleaned_data.get('firstname')
            context = {
                        'email': email_address, # Passing the email address here
                        'firstname':  first_name,
                        'login_url': 'http://127.0.0.1:8000/core/login/' # Update with your actual domain
                      }
            html_content = render_to_string('welcome.html', context)
            
            email = EmailMultiAlternatives(
                subject="Welcome to PhoneBazar - Your Mobile Hub 📱",
                body=strip_tags(html_content),
                from_email=settings.EMAIL_HOST_USER,
                to=[email_address]
            )
            email.attach_alternative(html_content, "text/html")

            # Attachment: Maybe a "Mobile Price List" or "Warranty Guide"
            file_path = os.path.join(settings.BASE_DIR, 'static/images/PhoneBazar_Logo.PNG')  # Example attachment
            if os.path.exists(file_path):
                email.attach_file(file_path)

            email.send()
            return redirect('login')

           
        else:
            return render(request, 'core/signup.html', {'form': form})  
    else:
        form = UserSignupForm()
        return render(request, 'core/signup.html', {'form': form})
    
def userLoginView(request):
  if request.method =="POST":
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
      print(form.cleaned_data)
      email = form.cleaned_data['email']
      password = form.cleaned_data['password']
      user = authenticate(request,email=email,password=password) #it will check in database..
      if user:
        login(request,user)
        if user.role == "Buyer":
          return redirect("Buyer_dashboard") #bazar.urls.py name...
        elif user.role == "Seller":
          return redirect("Seller_dashboard") #bazar.urls.py name...
        elif user.role == "Retailer":
          return redirect("Retailer_dashboard") #bazar.urls.py name...
      else:
        return render(request,'core/login.html',{'form':form})  
    
  else:
    form = UserLoginForm()
    return render(request,'core/login.html',{'form':form})
  
def userLogoutView(request):
    logout(request)
    # You can either redirect to login immediately:
    # return redirect('login') 
    
    # OR show a "Logged Out" confirmation page:
    return render(request, 'core/logout.html')

def helpView(request):
    return render(request, 'core/help.html')

def privacyView(request):
    return render(request, 'core/privacy.html')

def termsView(request):
    return render(request, 'core/terms.html')

@login_required
def userProfileView(request):
    """
    Displays the personal details of the logged-in user.
    'request.user' is automatically available because of the decorator.
    """
    return render(request, 'core/profile.html', {
        'user': request.user
    })

@login_required
def editProfileView(request):
    if request.method == 'POST':
        # instance=request.user tells Django which user to update
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = EditProfileForm(instance=request.user)
    
    return render(request, 'core/edit_profile.html', {'form': form})