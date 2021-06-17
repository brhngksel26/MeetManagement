from . import views
from django.urls import path
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.index,name="index"),
    path('dashboard/', views.dashboard,name="dashboard"),
    path('login/',views.loginPage,name="login"),
    path('register/',views.registerPage,name="register"),
    path('logout/',views.logoutUser,name="logout"),
    path('calendar/',views.calendar,name="calendar"),
    path('meetDetails/<title>',views.meetDetails,name="meetDetails"),


]