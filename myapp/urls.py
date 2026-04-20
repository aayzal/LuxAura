from django.urls import path
from . import views

urlpatterns = [
    # MAIN PAGES
    path('', views.home, name='home'),
    path('perfume/', views.perfume, name='perfume'),
    path('perfume/<int:id>/', views.perfume_detail, name='perfume_detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # AUTH
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # CART
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:id>/', views.update_cart, name='update_cart'),

    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.orders, name='orders'),

]
