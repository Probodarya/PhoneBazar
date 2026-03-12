
# Register your models here.
from django.contrib import admin
from .models import PhoneListing, TestReport, Order, Transaction, Feedback
from .models import User
admin.site.register(User)

class TestReportInline(admin.StackedInline):
    model = TestReport
    extra = 1  # Shows one empty report form by default
    can_delete = False
@admin.register(PhoneListing)
class PhoneListingAdmin(admin.ModelAdmin):
    # This controls which columns appear in the admin list view
    list_display = ('brand', 'model_name', 'seller', 'price', 'is_verified', 'created_at')
    
    # This adds a clickable link to filter by seller or verification status
    list_filter = ('is_verified', 'seller', 'brand')
    
    # This allows you to search for phones by IMEI or seller's username/email
    search_fields = ('imei_number', 'model_name', 'seller__username', 'seller__email')

    # Optional: Allow quick verification from the list view
    list_editable = ('is_verified',)
    inlines = [TestReportInline]
@admin.register(TestReport)
class TestReportAdmin(admin.ModelAdmin):
    # What columns you see in the history list
    list_display = ('listing', 'tester', 'valuation_price', 'is_passed', 'report_date')
    
    # Quick filters on the right side
    list_filter = ('is_passed', 'tester', 'report_date')
    
    # Search for specific phones or testers
    search_fields = ('listing__model_name', 'listing__imei_number', 'tester__username')
    
    # Make the date read-only so it can't be faked
    readonly_fields = ('report_date',)

    # Optional: Highlight failed tests in red (visual improvement)
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('listing', 'tester')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'phone_listing', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('buyer__username', 'phone_listing__model_name', 'tracking_number')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'phone_listing', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('buyer__username', 'phone_listing__model_name', 'tracking_number')
    readonly_fields = ('created_at',)
    
    # Allows you to change status directly in the list
    list_editable = ('status',)

# core/admin.py
# core/admin.py
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    # If the error persists after migrate, temporarily remove 'created_at' from here
    list_display = ('transaction_id', 'buyer', 'amount', 'status', 'created_at')

# core/admin.py
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    # 1. Fields to show in the list
    list_display = ('order', 'seller', 'buyer', 'phone_condition_rating', 'created_at')
    
    # 2. Add a Search Bar (Searches across related Usernames and Comments)
    search_fields = ('seller__username', 'buyer__username', 'comment')
    
    # 3. Add Sidebar Filters (Filter by Rating or Date)
    list_filter = ('phone_condition_rating', 'created_at')

    
    # 4. Add Date Hierarchy (The horizontal date bar at the top)
    date_hierarchy = 'created_at'

from django.contrib import admin
from .models import SupportMessage, Address

@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    # This shows these columns in the admin list view
    list_display = ('user', 'message', 'is_from_support', 'timestamp')
    # This adds a filter sidebar on the right
    list_filter = ('is_from_support', 'timestamp')
    # This adds a search bar to find messages by user email or text
    search_fields = ('user__email', 'message')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'city', 'pincode', 'is_default')
    list_filter = ('city', 'is_default')
    search_fields = ('full_name', 'user__email', 'pincode')
    
from django.contrib import admin
from .models import Wishlist

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_listing', 'created_at')
    list_filter = ('created_at',)

