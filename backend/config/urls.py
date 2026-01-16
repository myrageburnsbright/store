from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.main.views import health_check

urlpatterns = [
    path('admin/', admin.site.urls),

    # All API routes under /api/
    path('api/', include([
        path('health/', health_check, name='health-check'),
        path('v1/auth/', include('apps.accounts.urls')),
        path('', include('apps.main.urls')),
        path('cart/', include('apps.cart.urls')),
        path('payment/', include('apps.payment.urls')),
    ])),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)