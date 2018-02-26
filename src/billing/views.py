from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.utils.http import is_safe_url
import stripe


# Stripe integration -> the  API keys were generated using a fake email
stripe.api_key = "sk_test_BKDQSDGB04CKeHQg8FF7Qe4u"

STRIPE_PUB_KEY = 'pk_test_Ieryuhr7WQ5oPxm9hr0ECJpb'


def payment_method_view(request):
    next_ = request.GET.get('next')
    next_url = None

    if is_safe_url(next_, request.get_host()):
        next_url = next_

    return render(request, 'billing/payment-method.html', {"publish_key": STRIPE_PUB_KEY, 'next_url': next_url})


def payment_method_createview(request):
    if request.method == 'POST' and request.is_ajax():
        print(request.POST)
        return JsonResponse({'message': 'Done'})

    return HttpResponse('error', status_code=401)
