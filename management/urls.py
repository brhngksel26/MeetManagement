from . import views
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', views.index,name="index"),
    path('dashboard/', views.dashboard,name="dashboard"),
    path('login/',views.loginPage,name="login"),
    path('register/',views.registerPage,name="register"),
    path('logout/',views.logoutUser,name="logout"),
    path('meetDetails/<title>',views.meetDetails,name="meetDetails"),
    

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)