from django.urls import path
from . import views



urlpatterns = [
    path('', views.staff_view, name = 'staff_home'),
    path('tables/', views.StaffTablesview, name='tables'),
    path('dishes/', views.StaffDishesview, name='dishes'),
    path('book/<int:pk>/', views.StaffBookview, name='book_detail'),
    path('book/update/<int:pk>/', views.Staffupdate_book, name='staffupdate_book'),
    path('book/cancel/<int:pk>/', views.Staffcancel_book, name='staffcancel_book'),
    path('booking-statistics/', views.booking_statistics, name='booking_statistics'),
]
