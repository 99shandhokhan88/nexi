import hashlib
import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from .models import Transaction

# Alias and secret key from Nexi
ALIAS = "ALIAS_WEB_00073202"
SECRET_KEY = "XM3I2MOLZBHOYAJFV2U8QMPYVS3UPK1U"
REQUEST_URL = "https://int-ecommerce.nexi.it/ecomm/ecomm/DispatcherServlet"

def initiate_payment(request):
    # Transaction details
    transaction_code = f"TESTPS_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    currency = "EUR"
    amount = 5000  # Amount in cents (50.00 EUR)

    # MAC calculation (hashing for security)
    mac_string = f"codTrans={transaction_code}divisa={currency}importo={amount}{SECRET_KEY}"
    mac = hashlib.sha1(mac_string.encode('utf-8')).hexdigest()

    # Save the transaction to the database
    transaction = Transaction.objects.create(
        transaction_code=transaction_code,
        amount=amount,
        currency=currency
    )

    # Required parameters
    params = {
        'alias': ALIAS,
        'importo': amount,
        'divisa': currency,
        'codTrans': transaction_code,
        'url': request.build_absolute_uri('/payment/result/'),
        'url_back': request.build_absolute_uri('/payment/cancel/'),
        'mac': mac,
    }

    # Render the form with hidden fields to submit to Nexi
    return render(request, 'payments/checkout_form.html', {'params': params, 'request_url': REQUEST_URL})


def payment_result(request):
    SECRET_KEY = "XM3I2MOLZBHOYAJFV2U8QMPYVS3UPK1U"

    # Get necessary parameters from Nexi
    required_params = ['codTrans', 'esito', 'importo', 'divisa', 'data', 'orario', 'codAut', 'mac']
    missing_params = [param for param in required_params if param not in request.GET]

    if missing_params:
        return HttpResponse(f'Missing parameters: {", ".join(missing_params)}')

    # Recalculate MAC
    mac_calculated = hashlib.sha1(f"codTrans={request.GET['codTrans']}esito={request.GET['esito']}importo={request.GET['importo']}divisa={request.GET['divisa']}data={request.GET['data']}orario={request.GET['orario']}codAut={request.GET['codAut']}{SECRET_KEY}".encode('utf-8')).hexdigest()

    # Check MAC validity
    if mac_calculated != request.GET['mac']:
        return HttpResponse(f'MAC error: {mac_calculated} does not match {request.GET["mac"]}')

    # Check payment status
    if request.GET['esito'] == 'OK':
        message = f"The transaction {request.GET['codTrans']} was successful; authorization code: {request.GET['codAut']}"
        return render(request, 'payments/success.html', {'message': message})
    else:
        error_message = f"The transaction {request.GET['codTrans']} failed; error description: {request.GET.get('messaggio', 'Unknown error')}"
        return render(request, 'payments/error.html', {'error_message': error_message})



def payment_cancel(request):
    """
    Handle cancelled payments by redirecting to the error page
    with a cancellation message
    """
    # Get the transaction code if it was passed back from Nexi
    transaction_code = request.GET.get('codTrans', 'Unknown')

    # Update transaction status in database if it exists
    try:
        transaction = Transaction.objects.get(transaction_code=transaction_code)
        transaction.status = 'cancelled'
        transaction.save()
    except Transaction.DoesNotExist:
        pass  # If transaction doesn't exist in our database, just continue

    error_message = f"Transaction {transaction_code} was cancelled by the user."
    return render(request, 'payments/error.html', {
        'error_message': error_message
    })
