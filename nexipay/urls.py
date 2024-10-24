# nexipay/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('payment/', include('payments.urls')),  # Include the payments app URLs
    path('', lambda request: redirect('initiate_payment')),  # Redirect root URL to payment initiation
]
