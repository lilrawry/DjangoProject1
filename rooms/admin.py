from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponse
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Room, Reservation
import csv
from datetime import datetime

class RoomResource(resources.ModelResource):
    class Meta:
        model = Room
        fields = ('id', 'name', 'capacity', 'price_per_hour', 'is_available', 'description')

@admin.register(Room)
class RoomAdmin(ImportExportModelAdmin):
    resource_class = RoomResource
    list_display = ('name', 'capacity', 'price_per_hour', 'is_available')
    list_filter = ('is_available',)
    search_fields = ('name', 'description')
    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=rooms-{datetime.now().strftime("%Y%m%d")}.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response
    export_as_csv.short_description = "Export Selected Rooms to CSV"

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('room', 'user', 'start_time', 'end_time', 'status', 'total_price')
    list_filter = ('status', 'user')
    search_fields = ('room__name', 'user__username')
    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=reservations-{datetime.now().strftime("%Y%m%d")}.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response
    export_as_csv.short_description = "Export Selected Reservations to CSV"

# Extend UserAdmin to add more functionality
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    actions = ['export_users_csv']

    def export_users_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=users-{datetime.now().strftime("%Y%m%d")}.csv'
        writer = csv.writer(response)

        writer.writerow(['Username', 'Email', 'First Name', 'Last Name', 'Is Staff', 'Is Active'])
        for user in queryset:
            writer.writerow([
                user.username, user.email, user.first_name,
                user.last_name, user.is_staff, user.is_active
            ])
        return response
    export_users_csv.short_description = "Export Selected Users to CSV"

# Unregister the default UserAdmin and register our CustomUserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)