# urls.py
from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.xml_form, name='xml_form'),
    path('display/', views.display_xml_data, name='display_xml_data'),
    path('manage_xml/', views.manage_xml, name='manage_xml'),

    path('display_db/', views.display_db_data, name='display_db_data'),
    path('edit/<int:id>/', views.edit_entry, name='edit_entry'),
    path('delete_entry/<int:id>/', views.delete_entry, name='delete_entry'),
    path('search/', views.search_entries, name='search_entries'),
]
