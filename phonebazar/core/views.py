import django
from django.shortcuts import render,redirect,HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from urllib3 import request
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
from .models import Feedback, PhoneListing, Order, Transaction, TestReport, User
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
import os

from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import os

def userSignupView(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST or None)
        if form.is_valid():
            # 1. Save user as Inactive
            user = form.save(commit=False)
            user.is_active = False 
            user.status = 'inactive'
            user.save()

            # 2. Generate the OTP
            otp_code = user.generate_otp() 
            email_address = form.cleaned_data['email']
            first_name = form.cleaned_data.get('firstname')
            
            # --- EMAIL 1: BRANDING & WELCOME (HTML with Attachment) ---
            welcome_context = {
                'email': email_address,
                'firstname': first_name,
                'login_url': 'http://127.0.0.1:8000/core/login/' 
            }
            welcome_html = render_to_string('welcome.html', welcome_context)
            
            welcome_email = EmailMultiAlternatives(
                subject="Welcome to PhoneBazar - Your Mobile Hub 📱",
                body=strip_tags(welcome_html),
                from_email=settings.EMAIL_HOST_USER,
                to=[email_address]
            )
            welcome_email.attach_alternative(welcome_html, "text/html")

            # Attach Logo
            file_path = os.path.join(settings.BASE_DIR, 'static/images/logo.png')
            if os.path.exists(file_path):
                welcome_email.attach_file(file_path)
            
            welcome_email.send() # Sends the branding email

            # --- EMAIL 2: SECURITY OTP (Simple & Fast) ---
            # --- EMAIL 2: SECURITY OTP (HTML version) ---
            otp_context = {
                'firstname': first_name,
                'otp': otp_code
            }
            otp_html = render_to_string('otp_mail.html', otp_context)

            otp_email = EmailMultiAlternatives(
                subject="Your PhoneBazar Verification Code",
                body=f"Your OTP is {otp_code}", # Fallback for plain text
                from_email=settings.EMAIL_HOST_USER,
                to=[email_address]
            )
            otp_email.attach_alternative(otp_html, "text/html")
            otp_email.send()
                        # 3. Redirect to verification page
            return render(request, 'core/verify_otp.html', {'email': email_address})

        else:
            return render(request, 'core/signup.html', {'form': form})  
    else:
        form = UserSignupForm()
        return render(request, 'core/signup.html', {'form': form})
    
def verifyOtpView(request):
    if request.method == "POST":
        email = request.POST.get('email')
        otp_entered = request.POST.get('otp')
        
        try:
            user = User.objects.get(email=email)
            if user.otp == otp_entered:
                # Activate user
                user.is_active = True
                user.status = 'active'
                user.otp = None  # Clear OTP after successful use
                user.save()
                return redirect('login')
            else:
                return render(request, 'core/verify_otp.html', {
                    'email': email, 
                    'error': 'Invalid OTP. Please try again.'
                })
        except User.DoesNotExist:
            
            return redirect('login')
    
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
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_redirect(request):
    """
    Central logic to route users based on their specific role.
    """
    role = getattr(request.user, 'role', None)
    
    if role == "Buyer":
        return redirect("Buyer_dashboard")
    elif role == "Seller":
        return redirect("Seller_dashboard")
    elif role == "Retailer":
        return redirect("Retailer_dashboard")
    
    # Fallback to home if no role is found
    return redirect("home")

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import PhoneListing, Feedback
from django.db.models import Avg
@login_required
def seller_dashboard(request):
    # 1. Fetch listings for the CURRENT user
    listings_list = PhoneListing.objects.filter(seller=request.user)
    
    # 2. Fetch feedback for the CURRENT user
    reviews_list = request.user.received_feedback.all()
    
    # 3. Calculate Average Rating
    avg_score = reviews_list.aggregate(Avg('phone_condition_rating'))['phone_condition_rating__avg'] or 0
    
    # Debugging: Check your VS Code terminal to see if these numbers are > 0
    print(f"--- DEBUG: User {request.user.email} ---")
    print(f"Listings: {listings_list.count()} | Reviews: {reviews_list.count()}")

    stats = {
        'total': listings_list.count(),
        'verified': listings_list.filter(is_verified=True).count(),
        'pending': listings_list.filter(is_verified=False).count(),
    }

    context = {
        'listings': listings_list,  # Use 'listings' to match your {% for listing in listings %}
        'reviews': reviews_list.order_by('-created_at'),
        'avg_score': round(float(avg_score), 1),
        'feedback_count': reviews_list.count(),
        'stats': stats,
    }
    
    return render(request, 'bazar/seller/seller_dashboard.html', context)
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


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import PhoneListing, Order
from django.db.models import Avg, Sum
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import PhoneListing, Feedback, Order
from django.db.models import Avg
from .models import PhoneListing, Feedback

@login_required
def retailer_dashboard(request):
    # TRICK: Let's check if there are ANY phones in the DB first
    all_phones_in_db = PhoneListing.objects.all().count()
    
    # Now get only the ones for this user
    # We use .filter(seller_id=request.user.id) to be 100% specific
    listings = PhoneListing.objects.filter(seller_id=request.user.id)
    
    # Get reviews specifically for this seller
    reviews = Feedback.objects.filter(seller_id=request.user.id)
    
    # Stats calculation
    avg_score = reviews.aggregate(Avg('phone_condition_rating'))['phone_condition_rating__avg'] or 0

    # PRINT TO YOUR TERMINAL (Check VS Code bottom window)
    print(f"--- DEBUG START ---")
    print(f"Logged in User ID: {request.user.id}")
    print(f"Logged in Email: {request.user.email}")
    print(f"Total Phones in System: {all_phones_in_db}")
    print(f"Phones for THIS User: {listings.count()}")
    print(f"--- DEBUG END ---")

    context = {
        'listings': listings,
        'reviews': reviews,
        'avg_score': round(float(avg_score), 1),
        'feedback_count': reviews.count(),
        'stats': {
            'total': listings.count(),
            'verified': listings.filter(is_verified=True).count(),
        }
    }
    return render(request, 'bazar/retailer/retailer_dashboard.html', context)

#buyer navbar
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def wishlist(request):
    # Logic to fetch user's wishlist items
    return render(request, 'bazar/wishlist.html')

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import PhoneListing 

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import PhoneListing, Wishlist

@login_required
def add_to_wishlist(request, phone_id):
    phone = get_object_or_404(PhoneListing, id=phone_id)
    
    # Check if already in wishlist to avoid Duplicate entry error
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user, 
        phone_listing=phone
    )
    
    if created:
        messages.success(request, f"{phone.model_name} added to your wishlist!")
    else:
        messages.info(request, "This item is already in your wishlist.")
        
    return redirect('phone_detail', phone_id=phone.id)
def phone_detail(request, pk): # Changed from phone_id to pk
    phone = get_object_or_404(PhoneListing, id=pk)
    return render(request, 'bazar/phone_detail.html', {'phone': phone})
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Wishlist

@login_required
def view_wishlist(request):
    # Fetch all items saved by the current user
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('phone_listing')
    
    return render(request, 'bazar/buyer/wishlist.html', {
        'wishlist_items': wishlist_items
    })
@login_required
def remove_from_wishlist(request, item_id):
    wishlist_item = get_object_or_404(Wishlist, id=item_id, user=request.user)
    wishlist_item.delete()
    messages.info(request, "Item removed from your wishlist.")
    return redirect('view_wishlist')

@login_required
def view_cart(request):
    # Retrieve cart items from session or database
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for phone_id, quantity in cart.items():
        phone = get_object_or_404(PhoneListing, id=phone_id)
        item_total = phone.price * quantity
        total_price += item_total
        cart_items.append({
            'phone': phone,
            'quantity': quantity,
            'item_total': item_total
        })

    return render(request, 'bazar/buyer/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import PhoneListing

def add_to_cart(request, phone_id):
    # 1. Get the phone or return 404 if not found
    phone = get_object_or_404(PhoneListing, id=phone_id)
    
    # 2. Get the current cart from session (or an empty dict if it doesn't exist)
    cart = request.session.get('cart', {})
    
    # 3. Add the phone ID to the cart
    # We use string keys because session JSON doesn't support integer keys well
    phone_id_str = str(phone_id)
    if phone_id_str in cart:
        cart[phone_id_str] += 1
    else:
        cart[phone_id_str] = 1
        
    # 4. Save the cart back to the session
    request.session['cart'] = cart
    messages.success(request, f"{phone.brand} {phone.model_name} added to cart!")
    
    # 5. Redirect back to the marketplace or the cart page
    return redirect('view_cart')
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import PhoneListing, Order, Address

@login_required
def place_order(request):
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.error(request, "Your cart is empty!")
        return redirect('buyer_dashboard')

    # Get the user's default address for the order
    address = Address.objects.filter(user=request.user, is_default=True).first()
    if not address:
        messages.warning(request, "Please set a default address before placing an order.")
        return redirect('saved_addresses')

    # Create Order records
    for phone_id, quantity in cart.items():
        phone = PhoneListing.objects.get(id=phone_id)
        
        Order.objects.create(
            buyer=request.user,
            phone_listing=phone,
            address=address,
            total_price=phone.price * quantity,
            status='pending' # Initial status for the seller to see
        )
        
    # Clear the cart after successful order placement
    request.session['cart'] = {}
    request.session.modified = True
    
    messages.success(request, "Order placed successfully! Sellers in Surat have been notified.")
    return redirect('buyer_dashboard')
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Address  # Assuming you have an Address model

@login_required
def saved_addresses(request):
    addresses = Address.objects.filter(user=request.user).order_by('-is_default')

    if request.method == 'POST':
        # Get form data
        is_default = request.POST.get('is_default') == 'on'
        
        # If this new address is set to default, reset others
        if is_default:
            Address.objects.filter(user=request.user).update(is_default=False)
        
        Address.objects.create(
            user=request.user,
            full_name=request.POST.get('full_name'),
            phone_number=request.POST.get('phone_number'),
            address_line=request.POST.get('address_line'),
            city=request.POST.get('city'),
            pincode=request.POST.get('pincode'),
            is_default=is_default
        )
        return redirect('saved_addresses')

    return render(request, 'bazar/buyer/saved_addresses.html', {'addresses': addresses})
from django.shortcuts import get_object_or_404, redirect
from .models import Address

@login_required
def set_default_address(request, address_id):
    if request.method == 'POST':
        # 1. Unset all current default addresses for this user
        Address.objects.filter(user=request.user).update(is_default=False)
        
        # 2. Set the selected address as the new default
        address = get_object_or_404(Address, id=address_id, user=request.user)
        address.is_default = True
        address.save()
        
    return redirect('saved_addresses')
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import SupportMessage # Assuming you have a message model

@login_required
def support_chat(request):
    # Fetch messages between the user and support
    messages = SupportMessage.objects.filter(user=request.user).order_by('timestamp')

    if request.method == 'POST':
        text = request.POST.get('message')
        if text:
            SupportMessage.objects.create(
                user=request.user,
                message=text,
                is_from_support=False
            )
            return redirect('support_chat')

    return render(request, 'bazar/buyer/support_chat.html', {
        'chat_messages': messages
    })

# sellernavbar
from django.db.models import Sum
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Order

@login_required
def my_earnings(request):
    # 1. Fetch all completed orders for this seller's phones
    # Assuming Order model has a foreign key to PhoneListing
    sales = Order.objects.filter(
        phone_listing__seller=request.user, 
        status='completed'
    ).order_by('-created_at')
    
    # 2. Calculate Total Revenue
    total_revenue = sales.aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # 3. Calculate Earnings for the current month
    from django.utils import timezone
    current_month = timezone.now().month
    monthly_revenue = sales.filter(
        created_at__month=current_month
    ).aggregate(Sum('total_price'))['total_price__sum'] or 0

    context = {
        'sales': sales,
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'sales_count': sales.count(),
    }
    
    return render(request, 'bazar/seller/my_earnings.html', context)

from django.db.models import Avg, Count

@login_required
def seller_rating_view(request):
    # Get all reviews using the related_name defined in your models
    reviews = request.user.received_feedback.all().order_by('-created_at')
    
    # Calculate Average
    stats = reviews.aggregate(
        avg=Avg('phone_condition_rating'),
        count=Count('id')
    )
    
    # Calculate star percentage breakdown for the progress bars
    star_counts = []
    for i in range(5, 0, -1):
        count = reviews.filter(phone_condition_rating=i).count()
        percentage = (count / stats['count'] * 100) if stats['count'] > 0 else 0
        star_counts.append({'stars': i, 'count': count, 'percent': percentage})

    return render(request, 'bazar/seller/seller_rating.html', {
        'reviews': reviews,
        'avg_score': round(stats['avg'] or 0, 1),
        'total_reviews': stats['count'],
        'star_counts': star_counts
    })
#retailer navbar
import csv
import io
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import PhoneListing

@login_required
def bulk_upload_inventory(request):
    if request.method == "POST":
        csv_file = request.FILES.get('file')
        
        # 1. Basic Validation
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file.')
            return redirect('bulk_upload')

        # 2. Process the File
        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        next(io_string) # Skip the header row
        
        count = 0
        for row in csv.reader(io_string, delimiter=',', quotechar="|"):
            _, created = PhoneListing.objects.update_or_create(
                seller=request.user,
                brand=row[0],
                model_name=row[1],
                price=row[2],
                imei_number=row[3],
                description=row[4]
            )
            count += 1
        
        messages.success(request, f"Successfully imported {count} phones to your inventory.")
        return redirect('retailer_dashboard')

    return render(request, 'bazar/retailer/bulk_upload.html')
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Wishlist, PhoneListing

@login_required
def customer_leads(request):
    # 1. Fetch all wishlist entries for phones owned by this retailer
    leads = Wishlist.objects.filter(
        phone_listing__seller=request.user
    ).select_related('user', 'phone_listing').order_by('-created_at')

    # 2. Group leads by phone model to see which devices are most popular
    hot_leads = PhoneListing.objects.filter(
        seller=request.user
    ).annotate(wishlist_count=Count('wishlisted_by')).order_by('-wishlist_count')[:5] # Fixed the typo here

    return render(request, 'bazar/retailer/customer_leads.html', {
        'leads': leads,
        'hot_leads': hot_leads
    })
from django.db.models import Sum, Avg, Count
from .models import Order

@login_required
def sales_report(request):
    # Fetch all completed orders for this retailer's listings
    completed_sales = Order.objects.filter(
        phone_listing__seller=request.user, 
        status='completed'
    ).order_by('-created_at')

    # Financial Aggregations
    total_revenue = completed_sales.aggregate(Sum('total_price'))['total_price__sum'] or 0
    avg_order_value = completed_sales.aggregate(Avg('total_price'))['total_price__avg'] or 0
    total_units_sold = completed_sales.count()

    context = {
        'sales': completed_sales,
        'total_revenue': total_revenue,
        'avg_order_value': round(avg_order_value, 2),
        'total_units_sold': total_units_sold,
    }
    return render(request, 'bazar/retailer/sales_report.html', context)
from .models import StoreProfile
@login_required
def manage_shop(request):
    # Get or create a blank profile for the retailer
    store, created = StoreProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        store.store_name = request.POST.get('store_name')
        store.gst_number = request.POST.get('gst_number')
        store.store_address = request.POST.get('store_address')
        store.contact_number = request.POST.get('contact_number')
        store.save()
        messages.success(request, "Shop details updated successfully!")
        return redirect('manage_shop')

    return render(request, 'bazar/retailer/manage_shop.html', {'store': store})

# views.py
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    template_path = 'invoice_template.html'
    context = {'order': order}
    logo_path = request.build_absolute_uri('/static/images/logo.png')
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="PhoneBazar_Invoice_{order.id}.pdf"'
    
    # Find the template and render it
    template = get_template(template_path)
    html = template.render(context)

    # Create PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
import csv
import io
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import PhoneListing

def bulk_upload(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('file')

        # 1. Basic Validation: Is it a CSV?
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'This is not a CSV file!')
            return redirect('bulk_upload')

        # 2. Read and Decode the file
        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        next(io_string) # Skip the header row (Brand, Model, etc.)

        # 3. Loop through rows and create objects
        count = 0
        for row in csv.reader(io_string, delimiter=',', quotechar='"'):
            # Map columns: 0=Brand, 1=Model, 2=Price, 3=IMEI, 4=Condition
            _, created = PhoneListing.objects.update_or_create(
                imei_number=row[3], # Use IMEI as the unique identifier
                defaults={
                    'retailer': request.user,
                    'brand': row[0],
                    'model_name': row[1],
                    'price': row[2],
                    'condition': row[4],
                }
            )
            count += 1

        messages.success(request, f'Successfully imported {count} devices to your Surat store!')
        return redirect('retailer/retailer_dashboard')

    return render(request, 'retailer/bulk_upload.html')


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib import messages
import os

def forgot_password_view(request):
    if request.method == "POST":
        email_address = request.POST.get('email')
        try:
            user = User.objects.get(email=email_address)
            
            # 1. Generate the OTP
            otp_code = user.generate_otp()
            
            # 2. Prepare the Email Content
            context = {
                'firstname': user.firstname if user.firstname else "User",
                'otp': otp_code,
            }
            
            # Using your existing OTP mail template for consistency
            html_content = render_to_string('core/forgetotp_mail', context)
            text_content = strip_tags(html_content)
            
            # 3. Create the Email object
            email = EmailMultiAlternatives(
                subject="Reset Your PhoneBazar Password 🔒",
                body=text_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[email_address]
            )
            email.attach_alternative(html_content, "text/html")
            
            
            # (Optional) Attach logo if you want the branding here too
            logo_path = os.path.join(settings.BASE_DIR, 'static/images/logo.png')
            if os.path.exists(logo_path):
                from email.mime.image import MIMEImage
                with open(logo_path, 'rb') as f:
                    logo_image = MIMEImage(f.read())
                    logo_image.add_header('Content-ID', '<logo>')
                    email.attach(logo_image)

            # 4. Send the Email
            email.send()
            
            messages.info(request, "A password reset code has been sent to your email.")
            return render(request, 'core/verify_forgot_otp.html', {'email': email_address})
            
        except User.DoesNotExist:
            messages.error(request, "No user found with this email address.")
        except Exception as e:
            messages.error(request, "Something went wrong while sending the email.")
            print(f"Error: {e}")
            
    return render(request, 'core/forgot_password.html')

def reset_password_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        otp_entered = request.POST.get('otp')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        user = User.objects.get(email=email)

        if user.otp == otp_entered:
            if new_password == confirm_password:
                user.set_password(new_password)
                user.otp = None  # Clear OTP
                user.status = 'active' # Ensure they are active
                user.is_active = True
                user.save()
                messages.success(request, "Password reset successful! Please login.")
                return redirect('login')
            else:
                messages.error(request, "Passwords do not match.")
        else:
            messages.error(request, "Invalid OTP.")
            
    return render(request, 'core/verify_forgot_otp.html', {'email': email})