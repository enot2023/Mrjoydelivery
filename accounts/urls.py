from . import views
from django.urls import include, path

urlpatterns=[
    path('',views.myaccount),
    path('registerUser/',views.registerUser, name='registerUser'),
    path('registerVendor/',views.registerVender, name='registerVendor'),
    path('login/',views.login, name='login'),
    path('logout/',views.logout, name='logout'),
    path('myaccount/',views.myaccount, name='myaccount'),
    path('custdashboard/',views.custdashboard, name='custdashboard'),
    path('vendashboard/',views.vendashboard, name='vendashboard'),
    path('vendor/', include('vendor.urls')),
    path('customer/', include('customers.urls')),
    

]