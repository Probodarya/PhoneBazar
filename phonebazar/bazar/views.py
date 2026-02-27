from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .decorators import role_required

# Create your views here.
@role_required(allowed_roles=["Buyer"]) #check in core.urls.py login name should exist..
def BuyerDashboardView(request):
    return render(request,"bazar/buyer/buyer_dashboard.html")

@role_required(allowed_roles=["Seller"])
def SellerDashboardView(request):
    return render(request,"bazar/seller/seller_dashboard.html")

@role_required(allowed_roles=["Retailer"])
def RetailerDashboardView(request):
    return render(request,"bazar/retailer/retailer_dashboard.html")