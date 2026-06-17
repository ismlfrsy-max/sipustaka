from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # <-- Pastikan di sini tulisannya admin.site.urls
    path('', include('perpustakaan.urls')),
]