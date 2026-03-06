import django
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
from .forms import PhoneListingForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import PhoneListing, Order, Transaction, TestReport
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
# date 4/3/2026 working on post ad form
@login_required
def post_phone_ad(request):
    if request.method == 'POST':
        # request.FILES is required for the ImageField
        form = PhoneListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user # Link the listing to the logged-in seller
            listing.save()
            return redirect('post_ad_success')
    else:
        form = PhoneListingForm()
        return render(request, 'core/post_ad.html', {'form': form})
@login_required
def post_ad_success(request):
    """View to handle the success page after redirect."""
    return render(request, 'core/post_ad_success.html')
    
    return render(request, 'core/post_ad.html', {'form': form})
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import PhoneListing, Transaction

@login_required
def seller_dashboard(request):
    # TEMPORARY: Get ALL listings to see if anything shows up
    # If this works, the problem is with the 'seller' assignment
    my_listings = PhoneListing.objects.all()
    
    stats = {
        'total': my_listings.count(),
        'verified': my_listings.filter(is_verified=True).count(),
        'pending': my_listings.filter(is_verified=False).count(),
    }
    
    return render(request, 'bazar/seller/seller_dashboard.html', {
        'listings': my_listings,
        'stats': stats
    })

#5-2-2026 work
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from .models import PhoneListing, Order

@login_required
def create_order(request, listing_id):
    listing = get_object_or_404(PhoneListing, id=listing_id, is_verified=True)
    
    # Prevent buying your own phone
    if listing.seller == request.user:
        messages.error(request, "You cannot buy your own listing!")
        return redirect('seller_dashboard')

    # Create the order
    order = Order.objects.create(
        buyer=request.user,
        phone_listing=listing,
        total_price=listing.price,
        status='escrow' # Assuming payment is handled here
    )
    
    messages.success(request, f"Order for {listing.model_name} placed successfully!")
    return redirect('buyer_dashboard') # You'll need to create this view next

@login_required
def buyer_dashboard(request):
    # Fetch all orders placed by the current user
    my_purchases = Order.objects.filter(buyer=request.user).select_related('phone_listing').order_by('-created_at')
    
    # Calculate stats for the buyer's overview
    stats = {
        'active': my_purchases.exclude(status='completed').count(),
        'spent': sum(order.total_price for order in my_purchases.filter(status='completed')),
        'delivered': my_purchases.filter(status='delivered').count(),
    }
    
    return render(request, 'bazar/buyer/buyer_dashboard.html', {
        'orders': my_purchases,
        'stats': stats
    })
from django.shortcuts import render
from .models import PhoneListing

def marketplace_home(request):
    # CRITICAL: Only show phones that passed the test and haven't been bought
    # We exclude phones that are already linked to an Order
    verified_phones = PhoneListing.objects.filter(
        is_verified=True
    ).exclude(
        order__status__in=['escrow', 'shipped', 'delivered', 'completed']
    ).order_by('-created_at')

    return render(request, 'bazar/marketplace.html', {'phones': verified_phones})
from django.shortcuts import render, get_object_or_404
from .models import PhoneListing

def phone_detail(request, pk):
    # Fetch the phone or return a 404 error if it doesn't exist
    phone = get_object_or_404(PhoneListing, pk=pk)
    
    return render(request, 'bazar/phone_detail.html', {
        'phone': phone
    })
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import PhoneListing, Order


 # Import Django's DB transaction tool

from django.db import transaction as db_transaction

@login_required
def create_order(request, phone_id):
    listing = get_object_or_404(PhoneListing, id=phone_id)

    try:
        with db_transaction.atomic():
            # Create Order
            order = Order.objects.create(
                buyer=request.user,
                phone_listing=listing,
                total_price=listing.price,
                status='escrow'
            )

            # Create Transaction
            txn = Transaction.objects.create(
                listing=listing,
                buyer=request.user,
                amount=listing.price,
                status='held'
            )

        # Pass the Transaction ID in the success message
        messages.success(request, f"Order successful! Your Transaction ID is: {txn.transaction_id}")
        return redirect('buyer_dashboard')

    except Exception as e:
        messages.error(request, f"Error processing order: {str(e)}")
        return redirect('phone_detail', pk=phone_id)
    
def order_success(request, txn_id):
    transaction = get_object_or_404(Transaction, transaction_id=txn_id, buyer=request.user)
    return render(request, 'bazar/order_success.html', {'txn': transaction})

from django.db import transaction as db_transaction

@login_required
def confirm_delivery(request, order_id):
    # Fetch the order and ensure the current user is the buyer
    order = get_object_or_404(Order, id=order_id, buyer=request.user)

    if order.status != 'delivered':
        messages.error(request, "You can only confirm delivery for items already marked as delivered.")
        return redirect('buyer_dashboard')

    try:
        with db_transaction.atomic():
            # 1. Update Order Status
            order.status = 'completed'
            order.save()

            # 2. Update Transaction Status (Release Escrow)
            txn = Transaction.objects.get(listing=order.phone_listing, buyer=request.user)
            txn.status = 'completed'
            txn.save()

        messages.success(request, f"Transaction finalized for {order.phone_listing.model_name}! Funds released.")
    except Transaction.DoesNotExist:
        messages.error(request, "Transaction record not found.")
    
    return redirect('buyer_dashboard')
from .forms import FeedbackForm

@login_required
def leave_feedback(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user, status='completed')
    
    # Prevent double feedback
    if hasattr(order, 'feedback'):
        messages.warning(request, "You have already left feedback for this order.")
        return redirect('buyer_dashboard')

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.order = order
            feedback.buyer = request.user
            feedback.seller = order.phone_listing.seller
            feedback.save()
            messages.success(request, "Thank you for your feedback!")
            return redirect('buyer_dashboard')
    else:
        form = FeedbackForm()
    
    return render(request, 'bazar/leave_feedback.html', {'form': form, 'order': order})
from django.db.models import Avg

@login_required
def seller_dashboard(request):
    listings = PhoneListing.objects.filter(seller=request.user)
    
    # 1. Get all reviews for this seller
    all_reviews = Feedback.objects.filter(seller=request.user)
    
    # 2. Calculate the average score
    # We use .aggregate to get the mean of the condition rating
    rating_data = all_reviews.aggregate(Avg('phone_condition_rating'))
    avg_score = rating_data['phone_condition_rating__avg'] or 0
    
    # 3. Round to 1 decimal place (e.g., 4.5)
    avg_score = round(avg_score, 1)

    stats = {
        'total': listings.count(),
        'verified': listings.filter(is_verified=True).count(),
        'pending': listings.filter(is_verified=False).count(),
    }

    return render(request, 'bazar/seller_dashboard.html', {
        'listings': listings,
        'stats': stats,
        'avg_score': avg_score,      # <--- Make sure this is sent!
        'reviews': all_reviews[:5],  # <--- Send the last 5 reviews
        'feedback_count': all_reviews.count()
    })
#buyer navbar
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def wishlist(request):
    # Logic to fetch user's wishlist items
    return render(request, 'bazar/wishlist.html')

@login_required
def view_cart(request):
    # Logic to fetch items in the user's cart
    return render(request, 'bazar/cart.html')

@login_required
def saved_addresses(request):
    return render(request, 'bazar/addresses.html')

@login_required
def support_chat(request):
    return render(request, 'bazar/support.html')