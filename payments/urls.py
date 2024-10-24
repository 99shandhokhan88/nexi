# nexipay/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('payment/', include('payments.urls')),  # Include the payments app URLs
]

# payments/urls.py (create this new file)
from django.urls import path
from . import views

urlpatterns = [
    path('initiate/', views.initiate_payment, name='initiate_payment'),
    path('result/', views.payment_result, name='payment_result'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
]

# payments/views.py (add the missing payment_cancel view)
# Add this to your existing views.py file
def payment_cancel(request):
    return render(request, 'payments/error.html', {
        'error_message': 'Payment was cancelled by the user.'
    })
