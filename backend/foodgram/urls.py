import os

from dotenv import load_dotenv
from django.contrib import admin
from django.urls import include, path


load_dotenv()

DEBUG = os.getenv('DEBUG', 'True')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
]

if DEBUG:
    import debug_toolbar

    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
