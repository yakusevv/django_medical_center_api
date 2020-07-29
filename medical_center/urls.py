from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('territories/', include('territories.urls')),
    path('admin_site/', admin.site.urls),
]
