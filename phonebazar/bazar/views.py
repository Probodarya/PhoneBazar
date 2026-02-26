from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url="login") #check in core.urls.py login name should exist..
def BuyerDashboardView(request):
    return render(request,"bazar/buyer_dashboard.html")

@login_required(login_url="login")
def SellerDashboardView(request):
    return render(request,"bazar/seller_dashboard.html")

@login_required(login_url="login")
def RetailerDashboardView(request):
    return render(request,"bazar/retailer_dashboard.html")