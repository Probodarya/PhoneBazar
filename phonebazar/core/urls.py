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
  # date 4/3/2026 working on post ad form
  path('post-ad/', views.post_phone_ad, name='post_phone_ad'),
  path('post-ad/success/', views.post_ad_success, name='post_ad_success'),
  #5-2-2026 work
  path('marketplace/', views.marketplace_home, name='marketplace_home'),
  path('phone/<int:pk>/', views.phone_detail, name='phone_detail'),
  path('buy/<int:phone_id>/', views.create_order, name='create_order'),
  path('dashboard/buyer/', views.buyer_dashboard, name='buyer_dashboard'),
  path('order/confirm/<int:order_id>/', views.confirm_delivery, name='confirm_delivery'),
  path('leave-feedback/<int:order_id>/', views.leave_feedback, name='leave_feedback'),
  path('dashboard/retailer/', views.retailer_dashboard, name='retailer_dashboard'),
#buyer navar
    #path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:phone_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('phone/<int:phone_id>/', views.phone_detail, name='phone_detail'),
    path('wishlist/', views.view_wishlist, name='view_wishlist'),
    path('wishlist/remove/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('cart/', views.view_cart, name='view_cart'),
    path('add-to-cart/<int:phone_id>/', views.add_to_cart, name='add_to_cart'),
    path('place-order/', views.place_order, name='place_order'),
    path('addresses/', views.saved_addresses, name='saved_addresses'),
    path('set-default-address/<int:address_id>/', views.set_default_address, name='set_default_address'),

    path('support/', views.support_chat, name='support_chat'),
#seller navbar
  path('dashboard/earnings/', views.my_earnings, name='my_earnings'),
  path('dashboard/rating/', views.seller_rating_view, name='seller_rating'),
#retailer navar
  path('retailer/bulk-upload/', views.bulk_upload_inventory, name='bulk_upload'),
  path('retailer/leads/', views.customer_leads, name='customer_leads'),
  path('retailer/reports/', views.sales_report, name='sales_reports'),
  path('retailer/manage-shop/', views.manage_shop, name='manage_shop'),
]

