
import csv
from multiprocessing import context
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages,auth
from accounts.models import Account, UserProfile
from category.forms import CategoryForm
from category.models import Category
from django.contrib.auth.decorators import login_required
from coupon.forms import CategoryOfferForm, CouponApplyForm, ProductOfferForm
from coupon.models import CategoryOffer, Coupon, ProductOffer
from orders.forms import OrderStatusForm
from orders.models import Order, OrderProduct
from store.forms import ProductForm, ProductGalleryForm
from django.utils.text import slugify
from store.models import Product, ProductGallery 
from django.db.models import Count
import xlwt
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login
from django.views.decorators.cache import never_cache   


# <================= Home =================>
@never_cache
@login_required(login_url='admin-login')
def admin_home(request):
    orders = Order.objects.filter(is_ordered=True).order_by('-created_at')
    categories = Category.objects.all().annotate(item_count=Count('product'))
    order_status = Order.objects.all().annotate(item_status=Count('status'))
    print(order_status)
    order_count = Order.objects.all().count()
    users_count = UserProfile.objects.all().count()
    total_products = Product.objects.all().count()
    total_sales_amount=0
    for total in orders:
        total_sales_amount += total.order_total     
        

    
    print(order_status)
    print(categories)   

  
    
    context = {
        'orders':orders,
        'order_status':order_status,
        'categories':categories,
        'order_count':order_count,
        'users_count':users_count,
        'total_products':total_products,
        'total_sales_amount':total_sales_amount

        
    }
    return render(request, 'admin/admin-home.html',context)


#Admin Login/logout
@never_cache
# @login_required(login_url='admin-login')
def admin_login(request):
  if  request.session.get('admin_login'):
    return render(request, 'admin/admin-home.html')

  else:   
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        superadmin = authenticate(email=email, password=password)

        if superadmin is not None:
            if superadmin.is_admin:
                login(request, superadmin) 
                request.session['admin_login'] = 'admin_signin' 
                return redirect('admin_home')  
                 
            else:
                messages.error(request, 'Invalid login credentials')
                return redirect('admin-login')
        else:
                messages.error(request, 'Invalid login credentials')
                return redirect('admin-login')
    return render(request, 'admin/admin-login.html')


@never_cache
@login_required(login_url='admin-login')
def admin_logout(request):
   
    auth.logout(request)
    try:
        del request.session['admin_login']
    except:
        pass
   
    messages.success(request, 'You are logged out')
    return redirect('admin-login')


#User Managememt

@login_required(login_url='admin-login')
def user_list(request):
    users = Account.objects.all()
    context = {'users':users}
    return render(request, 'admin/user_table.html',context)


@login_required(login_url='admin-login')
def user_deactivate(request, user_id):
    user = Account.objects.get(pk=user_id)
    user.is_active = False
    user.save()
    messages.success(request, "User account has been succesfully deactivated!")    
    return redirect('user-table')


@login_required(login_url='admin-login')
def user_activate(request, user_id):
    user = Account.objects.get(pk=user_id)
    user.is_active = True
    user.save()
    messages.success(request, "User account has been succesfully activated")
    return redirect('user-table')


# Category list
@login_required(login_url='admin-login')
def category(request):
    category_items =  Category.objects.all()
    context ={'category_items':category_items}
    return render(request, 'admin/category/category-list.html',context)


# Category Add
@login_required(login_url='admin-login')
def add_category(request):
    
    if request.method == 'POST':
        print(50*'*'+"enter to add product")
        form = CategoryForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            form.save()
            messages.success(request,'Successfully new category added')
            context = {
            'form':form
          }
            return render(request, 'admin/category/add-category.html', context)
        else:
            messages.error(request,'Please fill all the fields')
            form = CategoryForm(request.POST or None, request.FILES or None)
        
            context = {
            'form':form
                    }
            return render(request, 'admin/category/add-category.html', context)
    else:
           
            form = CategoryForm(request.POST or None, request.FILES or None)
        
            context = {
            'form':form
                    }
            return render(request, 'admin/category/add-category.html', context)


# Category edit
@login_required(login_url='admin-login')
def edit_category(request ,id):
    if request.user.is_authenticated:
        if request.user.is_superadmin:
            instance = get_object_or_404(Category, id=id)
            form = CategoryForm(request.POST or None, request.FILES or None, instance=instance)
            if request.method == "POST":
                if form.is_valid():
                    form.save()
                    messages.success(request,'Product has been updated')
                    return redirect('category')
                else:
                    instance = get_object_or_404(Category, id=id)
                    form = CategoryForm(request.POST or None, request.FILES or None, instance=instance)  
                    context = {
                        'form'     : form,
                        'category':instance,
                        }
                    return render(request, 'admin/category/edit-category.html',context)
            else:
                instance = get_object_or_404(Category, id=id)
                form = CategoryForm(request.POST or None, request.FILES or None, instance=instance)  
                context = {
                    'form'     : form,
                    'category':instance,
                    }
                return render(request, 'admin/category/edit-category.html',context)

# Category delete
@login_required(login_url='admin-login')
def delete_category(request):
    
    cat_id = request.GET['catId']
    category = Category.objects.get(id = cat_id)
    category.delete()
    return redirect('category')
 


#products list
@login_required(login_url='admin-login')
def products_list(request):
  
    products = Product.objects.all()
    context = {
        'product':products,
    }
    return render(request, 'admin/products/products_list.html', context)

#add product
@login_required(login_url='admin-login')
def add_product(request):
                print('Entered to add product')
                if request.method == 'POST':
                    print('Entered to request ot method')
                    form = ProductForm(request.POST or None, request.FILES or None)
                    
                    if form.is_valid():
                        print('form is valid')
                        product = Product()
                        product.product_name = form.cleaned_data['product_name']
                        product.slug = slugify(product.product_name)
                        product.description = form.cleaned_data['description']
                        product.price = form.cleaned_data['price']
                        product.images = form.cleaned_data['images']
                        product.stock = form.cleaned_data['stock']
                        product.category = form.cleaned_data['category']
                        product = Product.objects.create(product_name=product.product_name, slug=product.slug,mrp_price=product.price, description=product.description, price=product.price, images= product.images, stock=product.stock,category=product.category)
                        product.save()
                        print('products saved')
                        return redirect(products_list)
                    products = Product.objects.all()
                    category = Category.objects.only('category_name')
                    context = {
                                'products':products,
                                'category':category,
                                'form':form,

                            }
                    return render(request, 'admin/products/add_product.html', context)
                
                else:
                    form = ProductForm(request.POST or None, request.FILES or None)
                    
                    context = {
                                'form':form
                            }
                    return render(request, 'admin/products/add_product.html', context)  
                


#producgt gallery
@login_required(login_url='admin-login')
def add_product_gallery_image(request):
    print('Entered to add product gallery5555555555555555555555555555555555555555555555555555555')
    form = ProductGalleryForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
    
    context = {                           
                'form':form,
            }
    return render(request, 'admin/products/add_product_gallery.html', context)

                
                
               

            

# Product edit
@login_required(login_url='admin-login')
def edit_product(request ,id):
    
     if request.user.is_authenticated:
        if request.user.is_superadmin:
            instance = get_object_or_404(Product, id=id)
            form = ProductForm(request.FILES or None, instance=instance)
            if request.method == "POST":
                if form.is_valid():
                    form.save()
                    messages.success(request,'Product has been updated')
                    return redirect('products_list')
                else:
                    instance = get_object_or_404(Product, id=id)
                    form = ProductForm(request.FILES or None, instance=instance)  
                    context = {
                        'form'     : form,
                        'product':instance,
                        }
                    return render(request, 'admin/products/edit_product.html',context)
            else:
                instance = get_object_or_404(Product, id=id)
                form = ProductForm(request.FILES or None, instance=instance)  
                context = {
                    'form'     : form,
                    'product':instance,
                    }
                return render(request, 'admin/products/edit_product.html',context)

# product delete
@login_required(login_url='admin-login')
def product_delete(request):
    pro_id = request.GET['proId']
    product = Product.objects.get(id = pro_id)
    product.delete()
    return redirect('products_list')

#Order Management
@login_required(login_url='admin-login')
def orders_list(request):
    orders = Order.objects.filter(is_ordered=True).order_by('-created_at')
    context = {
        'orders':orders
    }
    return render(request, 'admin/orders/orders_list.html', context)

@login_required(login_url='admin-login')
def cancel_order_admin(request, id):
    
    print('entered to cancel function')
    order = Order.objects.get(user = request.user, order_number = id)
    
    if request.method == "POST":
        # status = request.POST['cancel_order']
        order.status = "Cancelled"
        order.save()   
        print('order cancelled')
    
    return redirect('orders_list')


@login_required(login_url='admin-login')
def add_product_gallery(request):
    if request.method == 'POST':
        form = ProductGalleryForm()
        if form.is_valid():
            product = ProductGallery()
            product.image = form.cleaned_data['image']
            form.save()
    return render(request, 'admin/products/add_product_gallery.html')




@login_required(login_url='admin-login')
def update_order_status(request, order_number):

    instance = get_object_or_404(Order, order_number = order_number)
    
    form = OrderStatusForm(request.POST or None, instance=instance)
    print(form) 
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request,'Order Status has been updated')
            return redirect('orders_list')
    else:  
        context = {
            'form': form,
            'order': instance,
            }
        return render(request, 'admin/orders/update_order_status.html',context)
    context = {
                'form': form,
                'order': instance,
                }
    return render(request, 'admin/orders/update_order_status.html',context)





# @never_cache
# @login_required(login_url='admin-login')
# def export_csv(request):
#     order_data = Order.objects.all()
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename=GreatKart_Sales_Report'+'.csv'
#     writer = csv.writer(response)   
#     writer.writerow(['Customer Name', 'Order No', 'Order Date', 'City','State','Order Amount','Status'])
#     for data in order_data:
#         writer.writerow([data.full_name, data.order_number, data.created_at,data.city, data.state,data.order_total,data.status])
#     return response



@login_required(login_url='admin-login')
def adminsale(request):
    page = 'salesreport'
    global order_data
    order_data = Order.objects.filter(is_ordered=True)
    print('this is order data',order_data)
    yr = []
    ag = 2000
    months = ['January', 'February', 'March','April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    for i in range(0,51):
        yr.append(ag + i)
    if request.method == 'POST':
        datestr = request.POST.get('dates')
            #start date
        mo = datestr[:2]
        print('this is month',mo)
        da = datestr[3:5]
        print('this is day',da)
        ye = datestr[6:10]
        print('this is year',ye)
        #enddate
        mo1 = datestr[13:15]
        print('this is end day',mo1)
        da1 = datestr[16:18]
        print('this is end day',da1)
        ye1 = datestr[19:]
        print('this is end year',ye1)
        from_date = ye+'-'+mo+'-'+da
        to_date = ye1+'-'+mo1+'-'+da1
        
        year = request.POST.get('year')
        month = request.POST.get('month')
     
        print(from_date)
        if  month != '' :
            # order_data = OrderProduct.objects.filter(order__date_order__month=m).filter(order__payments__status='Completed').order_by('order__date_order')
            order_data = Order.objects.filter(created_at__month=month).filter(is_ordered=True).order_by('created_at')
        elif  year != '' :
            order_data = Order.objects.filter(created_at__year=year).filter(is_ordered=True).order_by('created_at')
        elif from_date != '' and to_date != '' :
            # order_data = OrderProduct.objects.filter(order__date_order__range=[from_date,to_date]).filter(order__payments__status='Completed').order_by('order__date_order')
            order_data = Order.objects.filter(created_at__range=(from_date,to_date)).filter(is_ordered=True).order_by('created_at')
    print('this is order data',order_data)
    
        


    
    #Total sales
    total_sales_amount=0
    sales = Order.objects.filter(is_ordered = True)
    for total in sales:
        total_sales_amount += total.nett_paid
    sales_amount = round(total_sales_amount,2)
    print(sales_amount)
    
    context = {'order_data': order_data, 'years': yr,'page': page,'months':months, 'sales_amount':sales_amount}
    return render(request,'admin/orders/sales_report2.html', context)




@login_required(login_url='admin-login')
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=SalesReport'+str(datetime.datetime.now())+'.csv'
    writer = csv.writer(response)   
    writer.writerow(['Customer Id','Name','Email','Payment Type','City','Ordered Date','Amount'])
    print('here is the error')
    order_data = Order.objects.filter(is_ordered=True)
    for data in order_data:
        writer.writerow([data.id, data.first_name, data.email, data.payment.payment_method,data.city,data.created_at,data.nett_paid])
    return response


@login_required(login_url='admin-login')
def admin_offers(request):
    coupon_offers = Coupon.objects.all().order_by('-valid_to')
    prod_offers = ProductOffer.objects.all().order_by('-valid_to')
    cat_offers = CategoryOffer.objects.all().order_by('-valid_to')


    # paginator = Paginator(coupon_offers, 5) # Show 25 contacts per page.
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)


    context = {
        'coupon_offers': coupon_offers,
        'prod_offers': prod_offers,
        'cat_offers': cat_offers,

    }

    return render(request,'admin/offer/offers.html',context)    


# Category offers


@login_required(login_url='admin-login')
def add_cat_offer(request):

    form = CategoryOfferForm(request.POST or None, request.FILES or None)  
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect('admin_offers')
        else:
            messages.error(request,'form not valid')            
            context = {
            'form':form
            }
            return render(request,'admin/offer/add_cat_offer.html',context)
    else:
        context = {
            'form':form
        }
        return render(request,'admin/offer/add_cat_offer.html',context)
    


@login_required(login_url='admin-login')
def edit_cat_offer(request,cat_id):
    instance = get_object_or_404(CategoryOffer, id=cat_id)
    form = CategoryOfferForm(request.POST or None, instance=instance)
  

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request,'Offer has been updated')
            return redirect('admin_offers')
        else:
             context = {
            'form'     : form,
            'coupon':instance,
            }
        return render(request, 'admin/offer/edit_cat_offer.html',context)
    else:  
        context = {
            'form'     : form,
            'coupon':instance,
            }
        return render(request, 'admin/offer/edit_cat_offer.html',context)


@login_required(login_url='admin-login')
def activate_cat_offer(request):
    offer_id = request.GET['catOffId']
    
    offer = CategoryOffer.objects.get(id = offer_id)
 
    offer.is_active = True
    offer.save()

    return redirect('admin_offers')



@login_required(login_url='admin-login')
def block_cat_offer(request):
    offer_id = request.GET['catOffId']
    offer = CategoryOffer.objects.get(id = offer_id)
    offer.is_active = False
    offer.save()

    return redirect('admin_offers')


@login_required(login_url='admin-login')
def delete_cat_offer(request):
    offer_id = request.GET['catOffId']
    offer = CategoryOffer.objects.get(id = offer_id)
    
    offer.delete()

    return redirect('admin_offers')

#coupon
@login_required(login_url='admin-login')
def add_coupon(request):
    form = CouponApplyForm(request.POST or None, request.FILES or None)  
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect('admin_offers')
        else:
            messages.error(request,'form not valid')            
            context = {
            'form':form
            }
            return render(request,'admin/offer/add_coupon.html',context)
    else:
        context = {
            'form':form
        }
        return render(request,'admin/offer/add_coupon.html',context)

@login_required(login_url='admin-login')
def edit_coupon(request,c_id):
    instance = get_object_or_404(Coupon, id=c_id)
    form = CouponApplyForm(request.POST or None, instance=instance)


    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request,'Product has been updated')
            return redirect('admin_offers')
        else:
             context = {
            'form'     : form,
            'coupon':instance,
            }
        return render(request, 'admin/offer/edit_coupon_offer.html',context)
    else:  
        context = {
            'form'     : form,
            'coupon':instance,
            }
        return render(request, 'admin/offer/edit_coupon_offer.html',context)


@login_required(login_url='admin-login')
def activate_coupon(request):
    coupon_id = request.GET['couponId']
    coupon = Coupon.objects.get(id = coupon_id)
    coupon.active = True
    coupon.save()

    return redirect('admin_offers')


@login_required(login_url='admin-login')
def block_coupon(request):
  
    coupon_id = request.GET['couponId']
    coupon = Coupon.objects.get(id = coupon_id)
    coupon.active = False
    coupon.save()

    return redirect('admin_offers')


@login_required(login_url='admin-login')
def delete_coupon(request):
    coupon_id = request.GET['couponId']
    coupon = Coupon.objects.get(id = coupon_id)
    
    coupon.delete()

    return redirect('admin_offers')


# Product offers
@login_required(login_url='admin-login')
def add_product_offer(request):

    form = ProductOfferForm(request.POST or None, request.FILES or None)  
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect('admin_offers')
        else:
            messages.error(request,'form not valid')            
            context = {
            'form':form
            }
            return render(request,'admin/offer/add_product_offer.html',context)
    else:
        context = {
            'form':form
        }
        return render(request,'admin/offer/add_product_offer.html',context)



@login_required(login_url='admin-login')
def edit_product_offer(request,prod_id):
    instance = get_object_or_404(ProductOffer, id=prod_id)
    form = ProductOfferForm(request.POST or None, instance=instance)


    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request,'Offer has been updated')
            return redirect('admin_offers')
        else:
             context = {
            'form'     : form,
            'coupon':instance,
            }
        return render(request, 'admin/offer/edit_product_offer.html',context)
    else:  
        context = {
            'form'     : form,
            'coupon':instance,
            }
        return render(request, 'admin/offer/edit_product_offer.html',context)


@login_required(login_url='admin-login')
def activate_product_offer(request):
    offer_id = request.GET['proOffId']
   
    offer = ProductOffer.objects.get(id = offer_id)

    offer.is_active = True
    offer.save()

    return redirect('admin_offers')


@login_required(login_url='admin-login')
def block_product_offer(request):
    offer_id = request.GET['proOffId']
    offer = ProductOffer.objects.get(id = offer_id)
    offer.is_active = False
    offer.save()

    return redirect('admin_offers')


@login_required(login_url='admin-login')
def delete_product_offer(request):
    offer_id = request.GET['proOffId']
    offer = ProductOffer.objects.get(id = offer_id)
    
    offer.delete()

    return redirect('admin_offers')
