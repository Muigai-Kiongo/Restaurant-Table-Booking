from django.contrib import admin
from .models import Table, Booking, Meal


class MealAdmin(admin.ModelAdmin):
    list_display = ('name', 'price') 
    search_fields = ('name',)  

class TableAdmin(admin.ModelAdmin):
    list_display = ('number', 'capacity', 'is_available') 
    list_filter = ('is_available',)  
    search_fields = ('number',)  

class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'table', 'date', 'time', 'meal_option') 
    list_filter = ('date', 'table', 'user') 
    search_fields = ('user__username', 'table__number')  
    date_hierarchy = 'date'  



admin.site.register(Table, TableAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Meal, MealAdmin)

admin.site.site_header = "Restaurant Table Booking Management System"
admin.site.site_title = "Restaurant Table Booking Managements"
admin.site.index_title = "Welcome to Restaurant Table Booking Management System"