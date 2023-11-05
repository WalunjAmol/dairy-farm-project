from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Sum, F, Case, When, DecimalField,Value
from django.urls import reverse_lazy,reverse
from django.contrib import messages
from django.http import JsonResponse,HttpResponseRedirect


#Local Import
from .models import EndUser,AdvancePayment
from .forms import AdvancePaymentForm

@method_decorator(login_required, name='dispatch')
class AdvancePaymentEndUserListView(ListView):
    model = EndUser
    template_name = 'advance_payments/advance_payments_enduser_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        user_dairy_role = self.request.user.dairy.role
        if self.request.user.is_superuser:
            queryset = self.model.objects.filter(dairy_name__role=user_dairy_role)
        else:
            queryset = self.model.objects.filter(dairy_name__role=user_dairy_role).order_by('custom_id')

                # Calculate the total withdrawal amount for each end user
        queryset = queryset.annotate(
            total_advance=Sum(
                Case(
                    When(
                        advance_payments__transaction_type='withdrawal',
                        then=F('advance_payments__payment_amount')
                    ),
                    When(
                        advance_payments__transaction_type='deduct',
                        then=-F('advance_payments__payment_amount')
                    ),
                    default=Value(0),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                )
            )
        )

        return queryset

class AdvancePaymentCreateView(CreateView):
    model = AdvancePayment
    form_class = AdvancePaymentForm
    template_name = 'advance_payments/advance_payments_form.html'  # Change this to your template path
    success_url = reverse_lazy('advance_payments:advance-payment-user-list')  # URL to redirect after successful deletion


    def get(self, request, *args, **kwargs):
        form = AdvancePaymentForm(user = self.request.user)
        return render(request, self.template_name, {'form':form})
    
    def post(self, request, *args, **kwargs):
        data =  request.POST
        form = AdvancePaymentForm(data=data,user=request.user)

        if not form.is_valid():
            print('form errors',form.errors)
            return render(request, self.template_name, {'form':form})

        if form.is_valid():
            form.save()
            messages.success(self.request, 'Adavance Payments added Successfully.')
            
        return redirect(self.success_url)

class AdvancePaymentUpdateView(UpdateView):
    model = AdvancePayment
    form_class = AdvancePaymentForm
    template_name = 'advance_payments/advance_payments_form.html'
    success_url = reverse_lazy('advance_payments:advance-payment-user-list')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = AdvancePaymentForm(user=request.user, instance=self.object)
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = AdvancePaymentForm(request.user, data=request.POST, instance=self.object)

        if form.is_valid():
            form.save()
            messages.success(request, 'Advance Payment updated successfully.')
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


def get_total_withdrawal_amount(request):
    enduser_id = request.GET.get('enduser_id')
    
    # Calculate the total withdrawal amount for the selected enduser_id
    total_withdrawal_amount = EndUser.objects.filter(id=enduser_id).annotate(
        total_advance=Sum(
            Case(
                When(
                    advance_payments__transaction_type='withdrawal',
                    then=F('advance_payments__payment_amount')
                ),
                When(
                    advance_payments__transaction_type='deduct',
                    then=-F('advance_payments__payment_amount')
                ),
                default=Value(0),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        )
    ).values('total_advance').first()
    
    # Extract the total withdrawal amount from the queryset
    total_withdrawal_amount = total_withdrawal_amount['total_advance'] if total_withdrawal_amount else 0.00
    
    data = {'total_withdrawal_amount': total_withdrawal_amount}
    return JsonResponse(data)

@method_decorator(login_required, name='dispatch')
class AdvancePaymentDetailViewView(DetailView):
    model = EndUser
    template_name = 'advance_payments/advance_payments_detail.html'  # Change this to your template path
    context_object_name = 'user'

    def get_queryset(self):
        user_dairy_role = self.request.user.dairy.role
        if self.request.user.is_superuser:
            queryset = self.model.objects.filter(dairy_name__role=user_dairy_role)
        else:
            queryset = self.model.objects.filter(dairy_name__role=user_dairy_role)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        total_advance_payment = AdvancePayment.objects.filter(enduser=user, transaction_type='withdrawal').aggregate(total_bonus=Sum(F('payment_amount')))['total_bonus']
        total_recovered_payment = AdvancePayment.objects.filter(enduser=user, transaction_type='deduct').aggregate(total_bonus=Sum(F('payment_amount')))['total_bonus']
        total_remaining_amount = EndUser.objects.filter(id=user.id).annotate(
        total_advance=Sum(
                Case(
                    When(
                        advance_payments__transaction_type='withdrawal',
                        then=F('advance_payments__payment_amount')
                    ),
                    When(
                        advance_payments__transaction_type='deduct',
                        then=-F('advance_payments__payment_amount')
                    ),
                    default=Value(0),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                )
            )
        ).values('total_advance').first()
    
        # Extract the total withdrawal amount from the queryset
        total_remaining_amount = total_remaining_amount['total_advance'] if total_remaining_amount else 0.00
    
        context['total_advance_payment'] = total_advance_payment
        context['total_recovered_payment'] = total_recovered_payment
        context['total_remaining_amount'] = total_remaining_amount
        context['transactions'] = AdvancePayment.objects.filter(enduser=user).order_by('-payment_date')
        return context
