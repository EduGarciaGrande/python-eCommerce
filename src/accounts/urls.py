from django.conf.urls import url

from .views import (
    AccountHomeView,
    )

app_name = "eCommerce-project"

urlpatterns = [
    url(r'^$', AccountHomeView.as_view(), name='home'),
]
