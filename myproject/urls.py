from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Login, Signup, Logout
     path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot'),
    # Include Django built-in auth urls for password reset/change if needed
    path('accounts/', include('django.contrib.auth.urls')),

    # Your app urls
    path('', include('myapp.urls')),

    # API urls
    path('api/', include('myapp.api_urls')),
]
