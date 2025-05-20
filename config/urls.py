"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.contrib import admin
from django.urls import path
from coursework import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('admin/', admin.site.urls),
    path('login/', views.login_page, name='login'),
    path('registration/', views.registration_page, name='registration'),
    path('logout/', views.logout_page, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.profile_edit, name='profile_edit'),

    path('keys/', views.key_list, name='key_list'),
    path('keys/<int:key_id>/take/', views.take_key, name='take_key'),
    path('keys/<int:key_id>/put/', views.put_key, name='put_key'),
    path('keys/transfer/', views.transfer_key, name='transfer_key'),

    path('free-keys/', views.free_keys, name='free_keys'),
    path('free-keys/<int:key_id>/take/', views.take_key, name='take_key'),
    path('put/<int:key_id>', views.put_key, name='put_key'),
    path('transfer/<int:key_id>', views.transfer_key, name='transfer_key'),

    path('requests-take/', views.admin_key_request, name='admin_key_request'),
    path('requests-put/', views.admin_put_request, name='admin_put_request'),
    path('request-put-key/<int:key_id>', views.put_key_request, name='put_key_request'),
    path('request-key/<int:key_id>/', views.take_key_request, name='take_key_request'),
    path('key-requests/', views.admin_key_request, name='key_request'),
    path('key-requests/approve/<int:request_id>/', views.approve_key_request, name='approve_take_request'),
    path('key-requests/reject/<int:request_id>/', views.reject_key_request, name='reject_key_request'),
    path('return-requests/', views.admin_put_request, name='put_request'),
    path('return-request/approve/<int:request_id>/', views.approve_return_request, name='approve_put_request'),
    path('return-request/reject/<int:request_id>', views.reject_key_request, name='reject_put_request'),

]
