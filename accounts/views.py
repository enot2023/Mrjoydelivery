from django.http import HttpResponse
from django.shortcuts import redirect, render

from orders.models import Order
from .utils import detectUser
import datetime
from vendor.forms import VendorForm

from .models import User, UserProfile
from django.contrib import messages, auth
from .forms import UserForm
from django.contrib.auth.decorators import login_required,user_passes_test
from django.core.exceptions import PermissionDenied
from django.template.defaultfilters import slugify

from vendor.models import Vendor
# restric the vendor form accessing the customer page
def check_role_vendor(user):
    if user.role==1:
        return True
    else:
        raise PermissionDenied
        

# restric the vendor form accessing the customer page
def check_role_customer(user):
    if user.role==2:
        return True
    else:
        raise PermissionDenied
        

# Create your views here.

def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request,'You are already login.')
        return redirect('myaccount')
    elif request.method=='POST':
        
        # print(request.POST)
        form=UserForm(request.POST)
        if form.is_valid():
            # create the user using the form
            # password = form.cleaned_data['password']
            # user=form.save(commit=False)
            # user.set_password(password)
            # user.role=User.CUSTOMER
            # user.save()

            # create the user using create_user_method
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            username=form.cleaned_data['username']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            user=User.objects.create_user(first_name=first_name,last_name=last_name,username=username,email=email,password=password)
            user.role=User.CUSTOMER
            user.save()
            # print('user is created')
            messages.success(request,'Your account has been register successfully.')
            return redirect('registerUser')
        else:
            print('invalid')
            print(form.errors)
    else:
         form = UserForm()
    context={
        'form':form,
    }
        
    return render(request,'accounts/registerUser.html',context)

def registerVender(request):
    if request.user.is_authenticated:
        messages.warning(request,'You are already login.')
        return redirect('myaccount')
    elif request.method=='POST':
        #store hte date and create the user
        form=UserForm(request.POST)
        v_form=VendorForm(request.POST,request.FILES)
        if form.is_valid() and v_form.is_valid():
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            username=form.cleaned_data['username']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            user=User.objects.create_user(first_name=first_name,last_name=last_name,username=username,email=email,password=password)
            user.role=User.RESTAURANT
            user.save()
            vendor=v_form.save(commit=False)
            vendor.user=user
            vendor_name=v_form.cleaned_data['vendor_name']
            vendor.vendor_slug=slugify(vendor_name)+'-'+str(user.id)
            user_profile=UserProfile.objects.get(user=user)
            vendor.user_profile=user_profile
            vendor.save()
            messages.success(request,'Your account is register successfully! Please wait for the approval.')
            return redirect('registerVendor')

        else:
            print('invalid form')
            print(form.errors)
    else:
        form=UserForm()
        v_form=VendorForm()

    context={
        'form':form,
        'v_form':v_form,
    }
    return render(request,'accounts/registerVendor.html',context)

def login(request):
    if request.user.is_authenticated:
        messages.warning(request,'You are already login.')
        return redirect('myaccount')

    elif request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']

        user=auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request,user)
            messages.success(request,'You are now logged in.')
            return redirect('myaccount')
        else:
            messages.error(request,'Invalid login credentials')
            return redirect('login')

    return render(request,'accounts/login.html',)
def logout(request):
    auth.logout(request)
    messages.info(request,'You have successfully logged out.')
    return redirect('login')



@login_required(login_url='login')
def myaccount(request):
    user=request.user
    redirectUrl = detectUser(user)
    print(user.role)
    return redirect(redirectUrl)

@login_required(login_url='login') 
@user_passes_test(check_role_customer)  
def custdashboard(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    recent_order = orders[:5]
    context={
        'orders':orders,
        'orders_count':orders.count(),
        'recent_order': recent_order,
    }
    return render(request,'accounts/custdashboard.html',context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendashboard(request):
    vendor=Vendor.objects.get(user=request.user)
    orders=Order.objects.filter(vendors__in=[vendor.id],is_ordered=True).order_by('-created_at')
    recent_orders=orders[:5]

    # currentmonth revenue
    current_month=datetime.datetime.now().month
    current_month_order=orders.filter(vendors__in=[vendor.id],created_at__month=current_month)
    current_month_revenue=0
    for i in current_month_order:
        current_month_revenue+=i.get_total_by_vendor()['grand_total']
    # total rev
    total_revenue=0
    for i in orders:
        total_revenue+=i.get_total_by_vendor()['grand_total']
    context={
        'orders':orders,
        'orders_count':orders.count(),
        'recent_orders':recent_orders,
        'total_revenue':total_revenue,
        'current_month_revenue':current_month_revenue,
    }
    return render(request,'accounts/vendashboard.html',context)

