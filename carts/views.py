from datetime import datetime
import datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from accounts.models import Account, UserProfile
from carts.models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from orders.models import Address, Order
from store.models import Product
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control

# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

# Add to cart

def add_cart_id(request, product_id): 
    product =  Product.objects.get(id=product_id) #get the product
    
    try:
        cart = Cart.objects.get(cart_id = _cart_id(request)) #get the cart using the cart id present in the session
        print(cart)
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id = _cart_id(request))
        cart.save()
    if request.user.is_authenticated:

        try:
            #For increasing cart product quanity... if not same product present create a new product item in cart
            cart_item = CartItem.objects.get(product=product, cart=cart, user = request.user)
            print(cart_item, "check cart_id present or not")
            cart_item.quantity += 1 
            print(cart_item.quantity, "quantity added")
            cart_item.save()
            
        except CartItem.DoesNotExist:
        
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
                user = request.user
            )
            cart_item.save()
            print(cart_item, " created new one")

    else:
        try:
            #For increasing cart product quanity... if not same product present create a new product item in cart
            cart_item = CartItem.objects.get(product=product, cart=cart)
            print(cart_item, "check cart_id present or not")
            cart_item.quantity += 1 
            print(cart_item.quantity, "quantity added")
            cart_item.save()
            
        except CartItem.DoesNotExist:
        
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
                
            )
            cart_item.save()
            print(cart_item, " created new one")
    return redirect('cart')


def add_cart(request): 
    product_id = request.GET['plusId']
    product =  Product.objects.get(id=product_id) #get the product
    
    try:
        cart = Cart.objects.get(cart_id = _cart_id(request)) #get the cart using the cart id present in the session
        print(cart)
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id = _cart_id(request))
        cart.save()
    if request.user.is_authenticated:

        try:
            #For increasing cart product quanity... if not same product present create a new product item in cart
            cart_item = CartItem.objects.get(product=product, cart=cart, user = request.user)
            print(cart_item, "check cart_id present or not")
            cart_item.quantity += 1 
            print(cart_item.quantity, "quantity added")
            cart_item.save()
            
        except CartItem.DoesNotExist:
        
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
                user = request.user
            )
            cart_item.save()
            print(cart_item, " created new one")

    else:
        try:
            #For increasing cart product quanity... if not same product present create a new product item in cart
            cart_item = CartItem.objects.get(product=product, cart=cart)
            print(cart_item, "check cart_id present or not")
            cart_item.quantity += 1 
            print(cart_item.quantity, "quantity added")
            cart_item.save()
            
        except CartItem.DoesNotExist:
        
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
                
            )
            cart_item.save()
            print(cart_item, " created new one")
            print(cart_item.name)
            
    return JsonResponse({
        "status":True,
        "qty":cart_item.quantity
    })

def remove_cart(request):
    product_id = request.GET['minusId']
    cart = Cart.objects.get(cart_id = _cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return JsonResponse({
        "status":True,
        "qty":cart_item.quantity
        
    })

def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id =_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax =0
        grand_total=0
        if request.user.is_authenticated:
            print("user authenticated")
            cart_items = CartItem.objects.filter(user=request.user, is_active = True)
     
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request)) #if not authenticated, a cart id created
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)  #cart item taken on the basis of cart id
            
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (5 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass #just ignore

    context = {
        'total': total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax'      : tax,
        'grand_total' : grand_total,
    }

    return render(request, 'store/cart.html', context)


@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    
    # tax =0
    # grand_total=0
    try:
        
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:

            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        current_user = request.user
        cart_items = CartItem.objects.filter(user=current_user)
        cart_count = cart_items.count()
        if cart_count <=0:
            return redirect('store')


        grand_total = 0
        tax         = 0
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (5 * total)/100
        grand_total = total + tax 
        current_user = request.user
        order = Order()
          #Generate the order number
        order.user               = current_user
        order.tax               = tax
        yr                      = int(datetime.date.today().strftime('%Y'))
        dt                      = int(datetime.date.today().strftime('%d'))
        mt                      = int(datetime.date.today().strftime('%m'))
        d                       = datetime.date(yr,mt,dt)
        current_date            = d.strftime("%Y%m%d")
        order.order_total       = grand_total
        order.nett_paid         = grand_total
        order.save()
        order_number            = current_date + str(order.id)
        order.order_number      = order_number

        
        order.save()
        request.session['order_number'] =  order.order_number
    except ObjectDoesNotExist:
        pass #just ignore
    address = Address.objects.filter(user=request.user)
    
    context = { 
        'total': total,                 
        'quantity':quantity,
        'cart_items':cart_items,
        'tax': tax,
        'grand_total' : grand_total,
        'address':address,
    }
    return render(request, 'store/checkout.html', context)
    