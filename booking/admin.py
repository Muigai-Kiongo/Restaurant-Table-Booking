from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import Table, Booking, Meal
from staff.forms import ReportForm 

class CustomAdminSite(admin.AdminSite):
    site_header = "Restaurant Table Booking Management System"
    site_title = "Restaurant Table Booking Management"
    index_title = "Welcome to Restaurant Table Booking Management System"

custom_admin_site = CustomAdminSite(name='custom_admin')

class MealAdmin(admin.ModelAdmin):
    list_display = ('name', 'price') 
    search_fields = ('name',)  

class TableAdmin(admin.ModelAdmin):
    list_display = ('number', 'capacity', 'is_available') 
    list_filter = ('is_available',)  
    search_fields = ('number',)  



    

class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'table', 'date', 'time', 'meal_option' ) 
    list_filter = ('date', 'table', 'user') 
    search_fields = ('user__username', 'table__number')  
    date_hierarchy = 'date'  
    change_list_template = 'admin/booking/booking_change_list.html' 


    def reports_view(self, request):
        report_html = None
        report_type = None

        if request.method == 'POST':
            form = ReportForm(request.POST)
            if form.is_valid():
                report_type = form.cleaned_data['report_type']
                bookings = self.get_bookings(report_type)
                report_html = render_to_string(f'reports/{report_type}_report.html', {'bookings': bookings})
        else:
            form = ReportForm()

        context = {
            'form': form,
            'report_html': report_html,
            'report_type': report_type,
            **self.admin_site.each_context(request),  # Include additional context
        }
        return render(request, 'admin/reports.html', context)

    def get_bookings(self, report_type):
        now = timezone.now()
        if report_type == 'weekly':
            week_start = now - timezone.timedelta(days=7)
            return Booking.objects.filter(date__gte=week_start)
        elif report_type == 'monthly':
            month_start = now.replace(day=1)
            return Booking.objects.filter(date__gte=month_start)
        elif report_type == 'yearly':
            year_start = now.replace(month=1, day=1)
            return Booking.objects.filter(date__gte=year_start)
        return Booking.objects.none()

    def generate_pdf_response(self, html_string, filename):
        html = HTML(string=html_string)
        pdf = html.write_pdf()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    def download_report(self, request, report_type):
        bookings = self.get_bookings(report_type)
        html_string = render_to_string(f'reports/{report_type}_report.html', {'bookings': bookings})
        return self.generate_pdf_response(html_string, f'{report_type}_report.pdf')



    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('reports/', self.admin_site.admin_view(self.reports_view), name='reports_view'),
            path('reports/download/<str:report_type>/', self.admin_site.admin_view(self.download_report), name='download_report'),
        ]
        return custom_urls + urls

    

# Register your models with the custom admin site
custom_admin_site.register(Table, TableAdmin)
custom_admin_site.register(Booking, BookingAdmin)
custom_admin_site.register(Meal, MealAdmin)
# custom_admin_site.register(Booking, ReportAdmin)