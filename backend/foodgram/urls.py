import os

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv('DEBUG', 'True')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/', include('users.urls')),
]

if DEBUG:
    import debug_toolbar

    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
