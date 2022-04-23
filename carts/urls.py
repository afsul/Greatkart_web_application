from django.urls import path
from . import views

urlpatterns = [ 
    path('', views.cart, name='cart'),
    path('add_cart_id/<int:product_id>/',views.add_cart_id,name='add_cart_id'),
    path('add_cart/',views.add_cart,name='add_cart'),
    path('remove_cart/',views.remove_cart,name='remove_cart'),
    path('remove_cart_item/',views.remove_cart_item,name='remove_cart_item'),
    path('checkout/',views.checkout,name='checkout'),
]

