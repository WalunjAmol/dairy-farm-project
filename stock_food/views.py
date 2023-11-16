from typing import Any
from django.shortcuts import render
from django.views.generic import ListView,CreateView,UpdateView,DeleteView,DetailView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from end_user_management.models import EndUser
from django.db.models import Sum
from django.urls import reverse


from .models import Stock
from .forms import StockForm, StockUpdateForm
from .models import FeedPurchase
from .forms import FeedPurchaseCreateForm,FeedPurchaseUpdateForm

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



class FeedPurchaseCreateView(CreateView):
    model = FeedPurchase
    form_class = FeedPurchaseCreateForm
    template_name = 'stock_food/feedpurchase_create_form.html'
    success_url = reverse_lazy('stock_food_management:feedpurchase-list')
    success_message = "Feed Purchased Successfully"


    def form_valid(self, form):
        print("**********",form.data.get('stock'))
        stock_obj = Stock.objects.get(id=form.data.get('stock'))
        stock_qty = stock_obj.quantity-int(form.data.get('quantity_taken'))
        stock_obj.quantity = stock_qty
        stock_obj.save()
        form.instance.dairy = self.request.user.dairy 
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class FeedPurchaseListView(ListView):
    model = FeedPurchase
    template_name = 'stock_food/feedpurchase_list.html'
    context_object_name = 'feed_purchases'
    ordering = ['-date_created']  # This orders records by the 'date_created' field in descending order

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_feed_reamining_amount = self.model.objects.filter(
            created_by=self.request.user,
            is_paid=False,
            ).aggregate(total_purchase_amount=Sum('total_purchase_amount')).get('total_purchase_amount')
        context['total_feed_reamining_amount'] = total_feed_reamining_amount
        return context
    
class FeedPurchaseUpdateView(UpdateView):
    model = FeedPurchase
    form_class = FeedPurchaseUpdateForm
    template_name = 'stock_food/feedpurchase_update_form.html'
    success_url = reverse_lazy('stock_food_management:feedpurchase-list')
    success_message = "Feed Updated Successfully"

    def form_valid(self, form):
        # Retrieve the original feed purchase object
        original_feed_purchase = self.get_object()
        
        # Calculate the difference in quantity taken
        quantity_difference = form.cleaned_data['quantity_taken'] - original_feed_purchase.quantity_taken
        print('quantity_taken',form.cleaned_data['quantity_taken'])
        print('original_feed_purchase.quantity_taken',original_feed_purchase.quantity_taken)
        print('quantity_difference',quantity_difference)

        # Update the stock quantity
        stock_obj = original_feed_purchase.stock
        stock_obj.quantity -= quantity_difference
        stock_obj.save()

        return super().form_valid(form)


class FeedPurchaseDeleteView(DeleteView):
    model = FeedPurchase
    template_name = 'stock_food/feedpurchase_confirm_delete.html'
    success_url = reverse_lazy('stock_food_management:feedpurchase-list')
    success_message = "Feed Deleted Successfully"


@method_decorator(login_required, name='dispatch')
class UserWiseFeedPurchaseList(ListView):
    model = EndUser
    template_name = 'stock_food/feed_sale_enduser_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        user_dairy_role = self.request.user.dairy.role
        if self.request.user.is_superuser:
            queryset = self.model.objects.filter(dairy_name__role=user_dairy_role)
        else:
            queryset = self.model.objects.filter(dairy_name__role=user_dairy_role).order_by('custom_id')
        
        return queryset
    from django.db.models import Sum

@method_decorator(login_required, name='dispatch')
class UserWiseFeedDetails(ListView):
    model = FeedPurchase
    template_name = 'stock_food/feedpurchase_details.html'
    context_object_name = 'feed_purchases'

    def get_queryset(self, **kwargs):
        feed_user = self.kwargs.get('pk')
        queryset = self.model.objects.filter(
            taken_user=feed_user,
            created_by=self.request.user,
            dairy=self.request.user.dairy
        )
        return queryset.order_by('-date_created')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        feed_user = self.kwargs.get('pk')
        user_detail = EndUser.objects.get(id=feed_user)
        feed_amount_remaining = FeedPurchase.objects.filter(
            taken_user=feed_user,
            created_by=self.request.user,
            dairy=self.request.user.dairy,
            is_paid=False
        ).aggregate(total_purchase_amount=Sum('total_purchase_amount')).get('total_purchase_amount')
        context['feed_amount_remaining'] = feed_amount_remaining
        context['user_detail'] = user_detail
        return context

class UserFeedPurchaseCreateView(CreateView):
    model = FeedPurchase
    form_class = FeedPurchaseCreateForm
    template_name = 'stock_food/user_stock_create.html'
    success_message = "Feed Purchased Successfully"

    def get(self, request, *args, **kwargs):
        # Print the 'id' from kwargs
        feed_purchase_id = kwargs.get('pk')
        print("ID from kwargs:", feed_purchase_id)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        stock_obj = Stock.objects.get(id=form.data.get('stock'))
        stock_qty = stock_obj.quantity-int(form.data.get('quantity_taken'))
        stock_obj.quantity = stock_qty
        stock_obj.save()
        form.instance.dairy = self.request.user.dairy 
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        feed_user = self.kwargs.get('pk')
        user_detail = EndUser.objects.get(id=feed_user)
        context['user_detail'] = user_detail
        return context
    
    def get_success_url(self):
        # You can construct the success URL here, passing the 'id' parameter
        feed_purchase_id = self.kwargs.get('pk')

        return reverse('stock_food_management:user-wise-feed-purchase-details', kwargs={'pk': feed_purchase_id})
    
class UserFeedPurchaseUpdateView(UpdateView):
    model = FeedPurchase
    form_class = FeedPurchaseUpdateForm
    template_name = 'stock_food/user_stock_update.html'
    success_message = "Feed Updated Successfully"

    def form_valid(self, form):
        # Retrieve the original feed purchase object
        original_feed_purchase = self.get_object()
        
        # Calculate the difference in quantity taken
        quantity_difference = form.cleaned_data['quantity_taken'] - original_feed_purchase.quantity_taken
        print('quantity_taken',form.cleaned_data['quantity_taken'])
        print('original_feed_purchase.quantity_taken',original_feed_purchase.quantity_taken)
        print('quantity_difference',quantity_difference)

        # Update the stock quantity
        stock_obj = original_feed_purchase.stock
        stock_obj.quantity -= quantity_difference
        stock_obj.save()

        return super().form_valid(form)
    
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     feed_user = self.kwargs.get('pk')
    #     user_detail = EndUser.objects.get(id=feed_user)
    #     context['user_detail'] = user_detail
    #     return context
    
    def get_success_url(self):
        taken_user_value = self.request.POST.get('taken_user')
        return reverse('stock_food_management:user-wise-feed-purchase-details', kwargs={'pk': taken_user_value})