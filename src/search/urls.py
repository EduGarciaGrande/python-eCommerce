from django.conf.urls import url

from .views import (
    SearchProductView
    )

app_name = "eCommerce-project"

urlpatterns = [
    url(r'^$', SearchProductView.as_view(),name='query'),
]
