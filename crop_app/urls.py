from django.urls import path
from .views import generate_report,get_wordpress_posts,capture_image
from crop_app import views

urlpatterns = [
    path('generate_pdf/', views.generate_pdf, name='generate_pdf'),
    path('generate_report/', generate_report, name='generate_report'),
    path('home/', views.home, name='home'),
    path('wordpress-posts/', get_wordpress_posts, name='wordpress-posts'),
    path('capture_image/', capture_image, name='capture_image'),
]
