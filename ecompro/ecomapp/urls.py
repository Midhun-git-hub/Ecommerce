from django.urls import path
from . import views 
urlpatterns = [
    path('',views.home,name='home'),
    path('products/',views.products,name='products'),
    path('category/<slug:slug>/',views.category_products,name='category_products'),
    path('register/',views.register,name='register'),
    path('login/',views.user_login,name='login'),
    path('logout/',views.user_logout,name='logout'),
    path('about/',views.about,name='about'),
    path('contact/',views.contact,name='contact'),
    # card
    path('cart/', views.cart_view, name='cart'),
    path('cart/increase/<int:item_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:item_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('add_address/', views.add_address, name='add_address'),
    path('order_success/', views.order_success, name='order_success'),
    path('verify_payment/', views.verify_payment, name='verify_payment'),
       
]
