from django.urls import path
from . import views

app_name = 'board'
"""
Задаем пространство имен для приложения (URL-имена будут уникальными для разных приложений).
Здесь находится список шаблонов URL, которые сопоставлены URL с представлениями. 
"""
urlpatterns = [
    path('', views.advertisement_list, name='advertisement_list'),
    path('advertisement/<int:pk>/', views.advertisement_detail, name='advertisement_detail'),
    path('add/', views.add_advertisement, name='add_advertisement'),
    path('advertisement/<int:pk>/edit/', views.edit_advertisement, name='edit_advertisement'),
    path('advertisement/<int:pk>/delete/', views.delete_advertisement, name='delete_advertisement'),
]
