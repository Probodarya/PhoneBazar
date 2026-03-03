
# Register your models here.
from django.contrib import admin
from .models import PhoneListing, TestReport, Order, Transaction, Feedback
from .models import User
admin.site.register(User)

@admin.register(PhoneListing)
class PhoneListingAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model_name', 'seller', 'price', 'is_verified', 'created_at')
    list_filter = ('brand', 'is_verified', 'created_at')
    search_fields = ('brand', 'model_name', 'imei_number', 'seller__username')
    list_editable = ('is_verified',) # Quick toggle for verification

@admin.register(TestReport)
class TestReportAdmin(admin.ModelAdmin):
    list_display = ('listing', 'tester', 'is_passed', 'valuation_price', 'report_date')
    list_filter = ('is_passed',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'phone_listing', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('buyer__username', 'phone_listing__model_name', 'tracking_number')

admin.site.register(Order, OrderAdmin)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'listing', 'buyer', 'amount', 'status')
    readonly_fields = ('transaction_id',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('order', 'buyer', 'seller', 'phone_condition_rating', 'created_at')