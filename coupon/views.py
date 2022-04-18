from django.shortcuts import redirect, render

from orders.models import Order
from .models import Coupon
from .forms import CouponApplyForm
from datetime import timezone
from datetime import datetime

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from carts.models import CartItem
from django.http import JsonResponse



# Create your views here.
@require_POST
def coupon_apply(request):
    print("applied")
    now = timezone.now()
    
    form = CouponApplyForm(request.POST)
    if form.is_valid():
        code = form.cleaned_data['code']
        try:
            coupon = Coupon.objects.get(code__iexact = code, valid_from__lte=now, valid_to__gte=now, active = True)
            request.session['coupon_id'] = coupon.id
        except Coupon.DoesNotExist:
            request.session['coupon_id'] = None
    return redirect('place_order')

@csrf_exempt
def verify_coupon(request):
    print('coupon verify request received')
    now = datetime.now()
    if request.method == "POST":
        code = request.POST['code']
       
        print(code,'this is the offer code')
        try:
            print('checking coupon')
            coupon = Coupon.objects.get(code = code, valid_from__lte=now, valid_to__gte=now, active = True)
            print(coupon,'this is the coupon in ')
            if coupon:
                print(coupon,'coupon valid')
                try:
                    print("Checking whether already used")
                    coupon_already_used = Order.objects.get(user=request.user,coupon=coupon,coupon_use_status=True)
                    if coupon_already_used:
                        print("COUPON ALREADY USED")
                        print(coupon_already_used,"coupon not available")

                        # print("coupon used")
                        # print("coupon already used")
                        context = {
                        "success":"coupon already used",
                        }
                        return JsonResponse (context)
                    # else:
                    #     print('program runs this',coupon)
                    #     discount = coupon.discount
                    #     # print(discount)
                    #     order = Order.objects.get(user = request.user, is_ordered = False)
                    #     order_no = order.order_number
                    #     order.coupon = coupon
                    #     order.discount = round(discount,2)
                    #     order.save()
                    #     # print(order_no)
                    #     # print('got order')
                    #     current_user = request.user
                    #     cart_items = CartItem.objects.filter(user = current_user)
                    #     grand_total = 0
                    #     tax = 0
                    #     total = 0
                    #     quantity = 0
                    #     for cart_item in cart_items:
                    #         total   += (cart_item.product.price * cart_item.quantity)
                    #         quantity += cart_item.quantity
                    #     tax = round((5 * total)/100,2)
                    #     grand_total = round(total + tax,2)
                    
                    #     discount_amount = round(grand_total * discount/100,2)
                    #     # print(discount_amount,'discount amount')
                    #     total_after_coupon = round(float(grand_total - discount_amount),2)
                    #     # print(grand_total,'total')
                    #     # print(total_after_coupon,'amount after discount')

                    #     context = {
                    #         "success":"valid",
                    #         "discount_amount": discount_amount,
                    #         "total_after_coupon":total_after_coupon,
                    #     }
                    #     return JsonResponse(context)
                        
                except:
                    print('except'+"*" * 100)
                    discount = coupon.discount
                    print(discount,'discount amount +++++++++++')
                    order_number = request.session['order_number']
                    order = Order.objects.get(is_ordered = False,order_number=order_number)
                    print(order,"oder in ecxept ************************  ")
                    order_no = order.order_number
                    order.coupon = coupon
                    order.discount = round(discount,2)
                    
                    current_user = request.user
                    cart_items = CartItem.objects.filter(user = current_user)
                    grand_total = 0
                    tax = 0
                    total = 0
                    quantity = 0
                    for cart_item in cart_items:
                        total   += (cart_item.product.price * cart_item.quantity)
                        quantity += cart_item.quantity
                    tax = round((5 * total)/100,2)
                    grand_total = round(total + tax,2)
                    
                
                    discount_amount = round(grand_total * discount/100,2)
                    # print(discount_amount,'discount amount')
                    total_after_coupon = round(float(grand_total - discount_amount),2)
                    order.nett_paid = total_after_coupon
                    
                    order.save()
                    # print(grand_total,'total')
                    # print(total_after_coupon,'amount after discount')

                    context = {
                        "success":"valid",
                        "discount_amount": discount_amount,
                        "total_after_coupon":total_after_coupon,
                        # 'url':''
                    }   
                    return JsonResponse(context)                    
                    
        except Coupon.DoesNotExist:
            # print('no coupon available')
            context = {
                "success":"no_coupon",
            }
            return JsonResponse (context)





