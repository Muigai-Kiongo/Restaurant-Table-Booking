from django.urls import path
from .import views


urlpatterns = [
    path('register/',views.signUp , name ='register' ),
    path('login-success/', views.login_success_redirect, name='login_success'),
   
   
 
]