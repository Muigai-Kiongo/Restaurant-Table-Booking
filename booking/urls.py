from django.urls import path
from . import views



urlpatterns = [
    path('',views.index , name ='home' ),
    path('booking/', views.BookingListView, name='booking_list'),
    path('booking/<pk>/', views.BookingDetailView, name='booking_detail'),
    path('booking/<pk>/update/', views.BookingUpdateView, name='booking_update'),
    path('booking/<pk>/delete/', views.BookingDeleteView, name='booking_delete'),
    path('tables/', views.Tablesview, name='tables_list'),
    path('dishes/', views.Dishesview, name='dishes_list'),
     path('reports/', views.reports_view, name = 'reports-view'),
    path('reports/download/<str:report_type>/', views.download_report, name='download_report'),
 
]
