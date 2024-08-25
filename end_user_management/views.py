# Django Imports
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, Case, When, Value, DecimalField
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

# Internal Imports
from .models import EndUser
from .forms import EndUserForm

# External App Imports
from stock_food.models import FeedPurchase
from bonus_app.models import Bonus
from advance_payments.models import AdvancePayment

@method_decorator(login_required, name='dispatch')
class EndUserListView(ListView):
    model = EndUser
    template_name = 'end_user_management/enduser_list.html'
    context_object_name = 'users'
    ordering = ['custom_id']

    def get_queryset(self):
        user_dairy_role = self.request.user.dairy.role
        if self.request.user.is_superuser:
            queryset = self.model.objects.filter(dairy_name__role=user_dairy_role)
        else:
            queryset = self.model.objects.filter(dairy_name__role=user_dairy_role)

        queryset = queryset.order_by(*self.ordering)

        # Annotate each EndUser with total and remaining advance amount
        queryset = queryset.annotate(
            total_advance=Sum(
                Case(
                    When(
                        advance_payments__transaction_type='withdrawal',
                        then=F('advance_payments__payment_amount')
                    ),
                    default=Value(0),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                )
            ),
            total_deductions=Sum(
                Case(
                    When(
                        advance_payments__transaction_type__in=['deduct', 'online_received'],
                        then=F('advance_payments__payment_amount')
                    ),
                    default=Value(0),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                )
            )
        ).annotate(
            remaining_advance=F('total_advance') - F('total_deductions')
        )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calculate bonus amount for each user
        bonuses = Bonus.objects.filter(
            user__in=context['users']
        ).values('user').annotate(total_bonus_amount=Sum('bonus_amount'))

        bonuses_dict = {entry['user']: entry['total_bonus_amount'] for entry in bonuses}

        # Calculate feed_purchase amount and remaining amount for each user
        feed_purchases = FeedPurchase.objects.filter(
            taken_user__in=context['users']
        ).values('taken_user').annotate(
            total_feed_purchase_amount=Sum('total_purchase_amount'),
            paid_feed_purchase_amount=Sum(
                Case(
                    When(is_paid=True, then=F('total_purchase_amount')),
                    default=Value(0),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                )
            )
        ).annotate(
            remaining_feed_purchase=F('total_feed_purchase_amount') - F('paid_feed_purchase_amount')
        )

        feed_purchases_dict = {
            entry['taken_user']: {
                'total': entry['total_feed_purchase_amount'] or 0,
                'remaining': entry['remaining_feed_purchase'] or 0
            }
            for entry in feed_purchases
        }

        # Initialize totals
        total_remaining_advance = 0
        total_remaining_feed_purchase = 0
        total_bonus_amount = 0

        # Add amounts to context for template rendering and calculate overall totals
        for user in context['users']:
            user.advance_payment_amount = user.total_advance or 0
            user.advance_payment_remaining = user.remaining_advance or 0
            user.bonus_amount = bonuses_dict.get(user.pk, 0)
            user.feed_purchase_amount = feed_purchases_dict.get(user.pk, {}).get('total', 0)
            user.feed_purchase_remaining = feed_purchases_dict.get(user.pk, {}).get('remaining', 0)

            # Accumulate the totals
            total_remaining_advance += user.advance_payment_remaining
            total_remaining_feed_purchase += user.feed_purchase_remaining
            total_bonus_amount += user.bonus_amount

        # Add overall totals to the context
        context['total_remaining_advance'] = total_remaining_advance
        context['total_remaining_feed_purchase'] = total_remaining_feed_purchase
        context['total_bonus_amount'] = total_bonus_amount

        return context
@method_decorator(login_required, name='dispatch')
class EndUserCreateView(CreateView):
    model = EndUser
    form_class = EndUserForm
    template_name = 'end_user_management/enduser_create.html'
    success_url = reverse_lazy('end_user_management:user-list')

    def form_valid(self, form):
        custom_id = form.cleaned_data['custom_id']
        existing_users_with_same_id = EndUser.objects.filter(dairy_name=self.request.user.dairy, custom_id=custom_id)
        if existing_users_with_same_id:
            form.add_error('custom_id', "A user with this custom ID already exists within this dairy.")
            return self.form_invalid(form) 

        form.instance.dairy_owner = self.request.user
        form.instance.dairy_name = self.request.user.dairy
        messages.success(self.request, 'User created successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

@method_decorator(login_required, name='dispatch')
class EndUserUpdateView(UpdateView):
    model = EndUser
    form_class = EndUserForm
    template_name = 'end_user_management/enduser_update.html'
    success_url = reverse_lazy('end_user_management:user-list')

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            return queryset.filter(dairy_owner=self.request.user)
        else:
            return queryset.filter(dairy_owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'User updated successfully.')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class EndUserDeleteView(DeleteView):
    model = EndUser
    template_name = 'enduser_confirm_delete.html'
    success_url = reverse_lazy('end_user_management:enduser-list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'User deleted successfully.')
        return super().delete(request, *args, **kwargs)
