from django.urls import path

from app.views import Login, Register, Forget, CheckToken, Calculate

app_name = 'app'

urlpatterns = [
    path('login/', Login.as_view()),
    path('register/', Register.as_view()),
    path('forget/', Forget.as_view()),
    path('checkToken/', CheckToken.as_view()),
    path('calculate/', Calculate.as_view())
]
