# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('accounts/', include('django.contrib.auth.urls')),
#     path('', include('apps.transactions.urls')),  # home/dashboard at root
# ]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Your custom login view, pointing at your existing template:
    path(
        'accounts/login/',
        LoginView.as_view(template_name='accounts/login.html'),
        name='login'
    ),
    path(
        'accounts/logout/',
        LogoutView.as_view(next_page='login'),
        name='logout'
    ),

    # And your app’s URLs
    path('', include('apps.transactions.urls')),
]

