from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib import messages
from .views import CustomPasswordChangeView
urlpatterns = [
    path('', views.index, name='index'),

    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path("profile/", views.profile, name="profile"),
    path('about/', views.about, name='about'),
    path('prediction/', views.prediction, name='prediction'),
    path("api/predict/", views.predict_disease, name="predict_disease"),

    path('history/', views.history, name='history'),
    path('export-history-csv/', views.export_history_csv, name='export_history_csv'),
    path('export-history-pdf/', views.export_history_pdf, name='export_history_pdf'),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    #profile update password
    path(
    "change-password/",
    CustomPasswordChangeView.as_view(),
    name="password_change",
),
]

