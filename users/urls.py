from django.urls import include, path
from . import views


urlpatterns = [
    path('auth/', include('rest_auth.urls')),
    path('auth/register/', include('rest_auth.registration.urls')),
    path('auth/captchVerify/', views.recaptcha , name = 'CaptchaVerify')
]