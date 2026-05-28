from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('movie/<str:imdb_code>/', views.movie_detail, name='movie_detail'),
    path('search/suggestions/', views.search_suggestions, name='search_suggestions'),
    path('test/', views.test_speed, name='test_speed'),
]