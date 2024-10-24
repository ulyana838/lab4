# urls.py
from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.xml_form, name='xml_form'),
    path('display/', views.display_xml_data, name='display_xml_data'),
    path('manage_xml/', views.manage_xml, name='manage_xml'),
]
