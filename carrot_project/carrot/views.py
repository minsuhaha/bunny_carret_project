from django.shortcuts import render
from .models import Product

# Create your views here.
def main(request):
  top_views_products = Product.objects.filter(product_sold='N').order_by('-view_cnt')[:4]
  return render(request, 'carret_app/main.html', {'products' : top_views_products})