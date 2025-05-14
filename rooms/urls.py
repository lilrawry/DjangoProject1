from django.urls import path
from . import views, views_admin, views_user_admin, views_admin_dashboard

app_name = 'rooms'

urlpatterns = [
    path('', views.home, name='home'),
    path('rooms/', views.room_list, name='room_list'),
    path('room/<int:pk>/', views.room_detail, name='room_detail'),
    path('reserve/', views.create_reservation, name='create_reservation'),
    path('my-reservations/', views.my_reservations, name='my_reservations'),
    path('reservation/<int:pk>/cancel/', views.cancel_reservation, name='cancel_reservation'),
    path('reservation/<int:reservation_id>/pdf/', views.download_pdf, name='download_pdf'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('export-rooms-csv/', views.export_rooms_csv, name='export_rooms_csv'),
    path('export-reservations-csv/', views.export_reservations_csv, name='export_reservations_csv'),
    path('import-rooms-csv/', views.import_rooms_csv, name='import_rooms_csv'),
    path('preview-csv-import/', views.preview_csv_import, name='preview_csv_import'),
    path('reservation/<int:reservation_id>/payment/', views.process_payment, name='process_payment'),
    path('payment/<int:payment_id>/approve/', views.approve_payment, name='approve_payment'),
    path('payment/<int:payment_id>/reject/', views.reject_payment, name='reject_payment'),
    path('reservation/<int:reservation_id>/approve/', views.approve_reservation, name='approve_reservation'),
    path('reservation/<int:reservation_id>/reject/', views.reject_reservation, name='reject_reservation'),
    
    # Admin Dashboard Pages
    path('admin-dashboard/rooms/', views_admin_dashboard.admin_rooms, name='admin_dashboard_rooms'),
    path('admin-dashboard/reservations/', views_admin_dashboard.admin_reservations, name='admin_dashboard_reservations'),
    path('admin-dashboard/users/', views_admin_dashboard.admin_users, name='admin_dashboard_users'),
    path('admin-dashboard/groups/', views_admin_dashboard.admin_groups, name='admin_dashboard_groups'),
    path('admin-dashboard/pending-payments/', views_admin_dashboard.admin_pending_payments, name='admin_dashboard_pending_payments'),
    path('admin-dashboard/pending-reservations/', views_admin_dashboard.admin_pending_reservations, name='admin_dashboard_pending_reservations'),
    
    # Auth URLs
    path('login/', views.custom_login, name='custom_login'),
    path('register/', views.register, name='register'),
    path('logout/', views.custom_logout, name='custom_logout'),
    
    # Admin room management URLs
    path('admin/rooms/', views_admin.manage_rooms, name='manage_rooms'),
    path('admin/rooms/add/', views_admin.add_room, name='add_room'),
    path('admin/rooms/<int:pk>/edit/', views_admin.edit_room, name='edit_room'),
    path('admin/rooms/<int:pk>/delete/', views_admin.delete_room, name='delete_room'),
    
    # Admin user management URLs
    path('admin/users/', views_user_admin.manage_users, name='manage_users'),
    path('admin/users/add/', views_user_admin.add_user, name='add_user'),
    path('admin/users/<int:pk>/edit/', views_user_admin.edit_user, name='edit_user'),
    path('admin/users/<int:pk>/delete/', views_user_admin.delete_user, name='delete_user'),
]
