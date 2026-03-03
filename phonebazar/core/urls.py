from django.contrib import admin
from django.urls import path,include
from . import views
urlpatterns = [
  
  path('signup/',views.userSignupView,name='signup'),
  path('login/',views.userLoginView,name='login'),
  path('logout/',views.userLogoutView,name='logout'),
  path('help/',views.helpView,name='help'),
  path('privacy/',views.privacyView,name='privacy'),
  path('terms/',views.termsView,name='terms'),
  path('profile/',views.userProfileView,name='profile'),
  path('edit-profile/',views.editProfileView,name='edit_profile'),
]
