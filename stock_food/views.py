from django.shortcuts import render
from django.views.generic import ListView,CreateView,UpdateView
from django.urls import reverse_lazy

from .models import Stock
from .forms import StockForm, StockUpdateForm

import random
import string



# Create your views here.
class StockListView(ListView):
    model = Stock  # Specify the model for this view
    template_name = 'stock_list.html'  # Specify the template to be used

    def get_queryset(self):
        # Customize the queryset if needed
        return Stock.objects.filter(is_deleted=False)
    
class StockCreateView(CreateView):
    model = Stock
    form_class = StockForm
    template_name = 'stock_food/stock_create.html'
    success_url = reverse_lazy('stock_food_management:stock-list')

    def generate_random_symbol(self):
        # Generate a random symbol using a combination of characters and a random number
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f'SYM-{random_chars}'

    def form_valid(self, form):
        # Custom logic when the form is valid
        # For example, you can perform additional actions before saving the form
        instance = form.save(commit=False)
        # Set additional properties based on the form data or any other logic
        # For instance, setting the created_by field to the currently logged-in user
        instance.created_by = self.request.user  # Assuming you have authentication in place
        instance.dairy= self.request.user.dairy
        # Generate a unique symbol
        form.instance.symbol = self.generate_random_symbol()
        instance.save()

        return super().form_valid(form)


    def form_invalid(self, form):
        # Custom logic when the form is invalid
        # For example, you can log errors or perform other actions
        # In this case, we'll just print a message to the console
        print("Form is invalid",form.errors)
        return super().form_invalid(form)

class StockUpdateView(UpdateView):
    model = Stock
    form_class = StockUpdateForm
    template_name = 'stock_food/stock_update.html'
    success_url = reverse_lazy('stock_food_management:stock-list')


