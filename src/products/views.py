from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, View
from django.http import Http404, HttpResponse

from carts.models import Cart
from analytics.mixins import ObjectViewedMixin
from .models import Product, ProductFile
import os

from mimetypes import guess_type
from wsgiref.util import FileWrapper


class ProductFeaturedListView(ListView):
    queryset = Product.objects.all()
    template_name = 'products/list.html'

    def get_queryset(self, *args, **kwargs):
        return Product.objects.featured()


class ProductFeaturedDetailView(ObjectViewedMixin, DetailView):
    template_name = 'products/featured-detail.html'

    def get_queryset(self, *args, **kwargs):
        return Product.objects.featured()


class ProductDetailSlugView(ObjectViewedMixin, DetailView):
    queryset = Product.objects.all()
    template_name = 'products/detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailSlugView, self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        return context

    def get_object(self, *args, **kwargs):
        slug = self.kwargs.get('slug')

        # instance = get_object_or_404(Product, slug=slug, active=True)
        try:
            instance = Product.objects.get(slug=slug, active=True)
        except Product.DoesNotExist:
            raise Http404("Not found...")
        except Product.MultipleObjectsReturned:
            qs = Product.objects.filter(slug=slug, active=True)
            instance = qs.first()
        except:
            raise Http404("EEhhhhhhh...")

        # Trigger custom signal for analytics -> an object has been seen inside this view
        # object_viewed_signal.send(instance.__class__, instance=instance, request=request)
        return instance


class ProductDownloadView(View):
    def get(self, *args, **kwargs):
        slug = kwargs.get('slug')
        pk = kwargs.get('pk')

        downloads_qs = ProductFile.objects.filter(pk=pk, product__slug=slug)

        if downloads_qs.count() != 1:
            raise Http404("Download Not Found")

        download_obj = downloads_qs.first()
        file_root = settings.PROTECTED_ROOT
        filepath = download_obj.file.path
        final_filepath = os.path.join(file_root, filepath)

        with open(final_filepath, 'rb') as f:
            wrapper = FileWrapper(f)
            mime_type = 'application/force-download'
            guessed_mimetype = guess_type(filepath)[0]

            if guessed_mimetype:
                mime_type = guessed_mimetype

            response = HttpResponse(wrapper, content_type=mime_type)
            response['Content-Disposition'] = "attachment;filename=%s" % download_obj.name
            response['X-SendFile'] = str(download_obj.name)
            return response

       # return redirect(download_obj.get_default_url())


class UserProductHistoryView(LoginRequiredMixin, ListView):
    template_name = 'products/user-history.html'

    def get_context_data(self, *args, **kwargs):
        context = super(UserProductHistoryView, self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        views = request.user.objectviewed_set.by_model(Product, return_model=False)
        return views


class ProductListView(ListView):
    queryset = Product.objects.all()
    template_name = 'products/list.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductListView, self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.all()


class ProductDetailView(ObjectViewedMixin, DetailView):
    template_name = 'products/detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        print(context)
        return context

    def get_object(self, *args, **kwargs):
        request = self.request
        pk = self.kwargs.get('pk')
        instance = Product.objects.get_by_id(pk)

        if instance is None:
            raise Http404("Product doesn't exist")

        return instance
