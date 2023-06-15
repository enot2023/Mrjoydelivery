from datetime import date, datetime
from django.http import HttpResponse,JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from accounts.models import UserProfile

from orders.forms import OrderForm
from .context_processors import  get_cart_amounts, get_cart_counter
from marketplace.models import Cart
from menu.models import Categorys, FoodItem
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from vendor.models import OpeningHour, Vendor

# Create your views here.

def marketplace(request):
    vendors=Vendor.objects.filter(is_approved=True,user__is_active=True)
    vendor_count=vendors.count()
    context={
        'vendors':vendors,
        'vendor_count':vendor_count,
    }
    return render(request,'marketplace/listings.html',context)

def vendor_detail(request,vendor_slug):
    vendor=get_object_or_404(Vendor,vendor_slug=vendor_slug)

    categories=Categorys.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
    
        'fooditems',
        queryset=FoodItem.objects.filter(is_available=True)
        )
    )
    opening_hour=OpeningHour.objects.filter(vendor=vendor).order_by('day','-from_hour')
    
    # Check current days opening hour
    today_date=date.today()
    today=today_date.isoweekday()

    # current
    current_opening_hours = OpeningHour.objects.filter(vendor=vendor,day=today)
    


    if request.user.is_authenticated:
        cart_items=Cart.objects.filter(user=request.user)
    else:
        cart_items=None
    context={
        'vendor':vendor,
        'categories': categories,
        'cart_items':cart_items,
        'opening_hour':opening_hour,
        'current_opening_hours':current_opening_hours,
        
    }
    return render(request, 'marketplace/vendor_detail.html',context)

def add_to_cart(request,food_id):
    if request.user.is_authenticated:
        if request.is_ajax():
            # check if the food item is exits
            try:
                fooditem=FoodItem.objects.get(id=food_id)
                # check if the user has already added the food to the cart
                try:
                    chkcart=Cart.objects.get(user=request.user,fooditem=fooditem)
                    # increase cart quantity
                    chkcart.quantity+=1
                    chkcart.save()
                    return JsonResponse({'status':'Success','message': 'Increased the cart quantity', 'cart_counter':get_cart_counter(request), 'qty':chkcart.quantity, 'cart_amount':get_cart_amounts(request)})
                except:
                    chkcart=Cart.objects.create(user=request.user,fooditem=fooditem,quantity=1)
                    return JsonResponse({'status':'Success','message': 'Added the food to the cart', 'cart_counter':get_cart_counter(request),'qty':chkcart.quantity,  'cart_amount':get_cart_amounts(request) })

            except:
                return JsonResponse({'status':'Failed','message': 'This food does not exit'})
        else:
            return JsonResponse({'status':'Failed','message': 'Invalid request'})
        
    else:
        return JsonResponse({'status':'login_required','message': 'Please login in to continue '})
    
def decrease_cart(request,food_id):
    if request.user.is_authenticated:
        if request.is_ajax():
            # check if the food item is exits
            try:
                fooditem=FoodItem.objects.get(id=food_id)
                # check if the user has already added the food to the cart
                try:
                    chkcart=Cart.objects.get(user=request.user,fooditem=fooditem)
                    if chkcart.quantity>1:
                        # decrease cart quantity
                        chkcart.quantity-=1
                        chkcart.save()
                    else:
                        chkcart.delete()
                        chkcart.quantity=0
                    return JsonResponse({'status':'Success','message': 'cart quantity decrease successfully', 'cart_counter':get_cart_counter(request), 'qty':chkcart.quantity,'cart_amount':get_cart_amounts(request)})
                except:
                    return JsonResponse({'status':'Failed','message': 'You do not have this item in your cart!'})

            except:
                return JsonResponse({'status':'Failed','message': 'This food does not exit'})
        else:
            return JsonResponse({'status':'Failed','message': 'Invalid request'})
        
    else:
        return JsonResponse({'status':'login_required','message': 'Please login in to continue '})

@login_required(login_url='login')   
def cart(request):
    cart_items=Cart.objects.filter(user=request.user).order_by('created_at')
    context={
        'cart_items':cart_items
    }
    return render(request,'marketplace/cart.html',context)


def delete_cart(request,cart_id):
    if request.user.is_authenticated:
        if request.is_ajax():
            try:
                # check if the cart item exit
                cart_item=Cart.objects.get(user=request.user,id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status':'Success', 'message':'Cart item has been deleted!', 'cart_counter':get_cart_counter(request),'cart_amount':get_cart_amounts(request)})
            except:
                return JsonResponse({'status':'Failed','message': 'cART item does not exit!'})
        else:
            return JsonResponse({'static':'Failed', 'message':'Invalid request!'})
        
def search(request):
    keyword=request.GET['keyword']
    # get vendor ids that has the food item the user is looking for
    fetch_vendors_by_food_items=FoodItem.objects.filter(food_title__icontains=keyword, is_available=True).values_list('vendor', flat='True')
    vendors=Vendor.objects.filter(Q(id__in=fetch_vendors_by_food_items) | Q(vendor_name__icontains=keyword,is_approved=True, user__is_active=True))
    vendor_count=vendors.count()
    context={
        'vendors':vendors,
        'vendor_count':vendor_count
    }
    return render(request,'marketplace/listings.html',context)

@login_required(login_url='login')
def checkout(request):
    cart_items=Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count=cart_items.count()
    if cart_count<=0:
        return redirect('marketplace');
    user_profile=UserProfile.objects.get(user=request.user)
    default_values={
        'first_name':request.user.first_name,
        'last_name':request.user.last_name,
        'phone':request.user.phone_number,
        'email':request.user.email,
        'address':user_profile.address,
        'country':user_profile.country,
        'state':user_profile.state,
        'city':user_profile.city,
        'pin_code':user_profile.pincode,
    }
    form=OrderForm(initial=default_values)
    context={
        'form':form,
        'cart_items':cart_items,
    }
    return render(request,'marketplace/checkout.html',context)