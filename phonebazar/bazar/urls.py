from django.urls import path
from . import views

urlpatterns = [
    path('buyer/dashboard/', views.BuyerDashboardView, name='Buyer_dashboard'),
    path('seller/dashboard/', views.SellerDashboardView, name='Seller_dashboard'),
    path('retailer/dashboard/', views.RetailerDashboardView, name='Retailer_dashboard'),

   
]