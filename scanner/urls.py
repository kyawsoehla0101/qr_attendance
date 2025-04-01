# scanner/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='scanner/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register_user, name='register'),
    path('', views.scan_page, name='scan_page'),
    path('scan/', views.receive_qr, name='receive_qr'),
    path('users/', views.users_list, name='users_list'),
    path('generate-qr/<int:user_id>/', views.generate_qr, name='generate_qr'),
    path('export-pdf/', views.export_logs_pdf, name='export_logs_pdf'),
    path('logs/', views.qr_logs_view, name='qr_logs'),

]
