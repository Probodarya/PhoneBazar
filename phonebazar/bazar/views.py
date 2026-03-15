from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .decorators import role_required

# Create your views here.
from django.shortcuts import render
from django.db.models import Sum
from core.models import Order, Wishlist


@role_required(allowed_roles=["Buyer"])
def BuyerDashboardView(request):

    # Orders of current buyer
    orders = Order.objects.filter(buyer=request.user).order_by("-created_at")

    # Total spent
    total_spent = orders.aggregate(
        Sum("total_price")
    )["total_price__sum"] or 0

    # Wishlist items
    wishlist_count = Wishlist.objects.filter(user=request.user).count()

    stats = {
        "total_orders": orders.count(),
        "active": orders.exclude(status="completed").count(),
        "wishlist": wishlist_count,
        "spent": total_spent,
    }

    context = {
        "orders": orders,
        "stats": stats
    }

    return render(request, "bazar/buyer/buyer_dashboard.html", context)

from django.shortcuts import render
from django.db.models import Avg, Sum
from core.models import PhoneListing, Order, Feedback



@role_required(allowed_roles=["Seller"])
def SellerDashboardView(request):

    # Seller listings
    listings = PhoneListing.objects.filter(seller=request.user)

    # Orders for seller phones
    orders = Order.objects.filter(phone_listing__seller=request.user)

    # Feedback received by seller
    reviews = Feedback.objects.filter(seller=request.user)

    # Calculate revenue
    total_revenue = orders.aggregate(
        Sum("total_price")
    )["total_price__sum"] or 0

    # Calculate average rating
    avg_rating = reviews.aggregate(
        Avg("phone_condition_rating")
    )["phone_condition_rating__avg"] or 0

    stats = {
        "total": listings.count(),
        "verified": listings.filter(is_verified=True).count(),
        "pending": listings.filter(is_verified=False).count(),
        "revenue": total_revenue,
        "rating": round(avg_rating, 1)
    }

    context = {
        "listings": listings,
        "orders": orders,
        "reviews": reviews,
        "stats": stats
    }

    return render(request, "bazar/seller/seller_dashboard.html", context)

from django.shortcuts import render
from django.db.models import Sum
from core.models import PhoneListing, Order


@role_required(allowed_roles=["Retailer"])
def RetailerDashboardView(request):

    # Phones listed by retailer
    listings = PhoneListing.objects.filter(seller=request.user)

    # Orders for retailer phones
    orders = Order.objects.filter(phone_listing__seller=request.user)

    # Total revenue
    revenue = orders.aggregate(
        Sum("total_price")
    )["total_price__sum"] or 0

    stats = {
        "total_listings": listings.count(),
        "verified": listings.filter(is_verified=True).count(),
        "pending": listings.filter(is_verified=False).count(),
        "total_orders": orders.count(),
        "revenue": revenue,
    }

    context = {
        "listings": listings,
        "orders": orders,
        "stats": stats
    }

    return render(request, "bazar/retailer/retailer_dashboard.html", context)
