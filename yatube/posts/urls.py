from django.urls import path

from . import views


app_name = 'posts'
urlpatterns = [
    path('', views.index, name=''),
    path('index/', views.index, name='index'),
    path('groups/', views.groups, name='groups'),
    path('group/<slug:slug>/', views.group_list, name='group_list'),
]
