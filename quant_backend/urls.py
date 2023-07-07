
from django.contrib import admin
from django.urls import path, include
from app import urls as passport_urls
urlpatterns = [
    path('admin/', admin.site.urls),
    path('app/', include(passport_urls, namespace='app'))
]
