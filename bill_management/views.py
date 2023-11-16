from datetime import datetime,timedelta
from typing import Any
from django.views import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404
from django.db.models import Sum, F, Case, When, DecimalField,Value
from django.utils import timezone




import calendar
from datetime import date

from .models import GeneratedCycle  
from milk_transaction.models import MilkTransaction
from end_user_management.models import EndUser
from advance_payments.models import AdvancePayment
from bonus_app.models import Bonus
from stock_food.models import FeedPurchase

class ProcessAndStoreObjectsView(View):

    def create_cycle(self, month, cycle_day):
        # Filter MilkTransaction objects based on the given month and day
        month_transactions = MilkTransaction.objects.filter(
            date__month=month,
            date__day=cycle_day
        )
        
        cycle_day_label = '1st' if cycle_day == 1 else '2nd' if cycle_day == 16 else str(cycle_day)
        
        if month_transactions.exists():
            current_year = datetime.now().year
            cycle_name = f"{cycle_day_label} Cycle {month_transactions[0].get_month_name()} {current_year}"
            # Calculate 'from_date' and 'to_date' based on cycle_day and month
            from_date = datetime(current_year, month, cycle_day)
            _, last_day_of_month = calendar.monthrange(current_year, month)
            if cycle_day == 16:
                to_date = datetime(current_year, month, last_day_of_month)
            elif cycle_day == 1:
                to_date = from_date + timedelta(days=14)  # Assuming each cycle is 15 days
            else:
                to_date = from_date + timedelta(days=14)  # Assuming each cycle is 15 days

            # Check if a cycle with the same name already exists
            if not GeneratedCycle.objects.filter(name=cycle_name).exists():
                print(f"Creating cycle: {cycle_name}")

                # Create and store the object in the GeneratedCycle model
                GeneratedCycle.objects.create(
                    name=cycle_name,
                    dairy_name=self.request.user.dairy,
                    dairy_owner=self.request.user,
                    from_date=from_date,
                    to_date=to_date
                )
            else:
                print(f"Cycle already exists for {cycle_name}. Skipping...")

    def get(self, request, *args, **kwargs):
        # Get the current date
        current_date = datetime.now().date()
        current_month = current_date.month

        # Create cycles for the specified cycle days
        # for cycle_day in self.CYCLE_DAYS:
        #     self.create_cycle(current_month, cycle_day)

        self.create_cycle(1, 1)
        self.create_cycle(1, 16)
        self.create_cycle(2, 1)
        self.create_cycle(2, 16)
        self.create_cycle(3, 1)
        self.create_cycle(3, 16)
        self.create_cycle(4, 1)
        self.create_cycle(4, 16)
        self.create_cycle(5, 1)
        self.create_cycle(5, 16)
        self.create_cycle(6, 1)
        self.create_cycle(6, 16)
        self.create_cycle(7, 1)
        self.create_cycle(7, 16)
        self.create_cycle(8, 1)
        self.create_cycle(8, 16)
        self.create_cycle(9, 1)
        self.create_cycle(9, 16)
        self.create_cycle(10, 1)
        self.create_cycle(10, 16)
        self.create_cycle(11, 1)
        self.create_cycle(11, 16)
        self.create_cycle(12, 1)
        self.create_cycle(12, 16)


        cycles = GeneratedCycle.objects.all().order_by('-from_date')

        context = {
            'cycles': cycles,
            'current_date': current_date,
            'current_month': current_month,
        }

        return render(request, 'bill_management/cycle_list.html', context)
        

@method_decorator(login_required, name='dispatch')
class BillMgtUserListView(ListView):
    model = EndUser
    template_name = 'bill_management/bill_mgt_enduser_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        user_dairy_role = self.request.user.dairy.role
        if self.request.user.is_superuser:
            queryset = self.model.objects.filter(dairy_name__role=user_dairy_role)
        else:
            queryset = self.model.objects.filter(dairy_name__role=user_dairy_role).order_by('custom_id')
        
        return queryset
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Retrieve the 'pk' from kwargs and get the cycle information
        pk = self.kwargs.get('pk')
        print('pk',pk)
        cycleinfo = get_object_or_404(GeneratedCycle, id=pk)
        print('cycle info',cycleinfo)
        
        # Add the cycleinfo to the context
        context['cycleinfo'] = cycleinfo
        
        return context


class GenerateBill(ListView):
    model = MilkTransaction
    template_name = 'bill_management/bill_details.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        # Fetch relevant parameters from URL
        cycle_id = self.kwargs.get('cycle_id')
        user_id = self.kwargs.get('user_id')
        
        # Fetch the cycle object
        cycle_object = GeneratedCycle.objects.get(id=cycle_id)
        
        # Filter MilkTransaction objects for the specified user and date range
        queryset = self.model.objects.filter(
            end_user=user_id,
            date__range=(cycle_object.from_date, cycle_object.to_date)
        ).order_by('date')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch relevant parameters from URL
        cycle_id = self.kwargs.get('cycle_id')
        user_id = self.kwargs.get('user_id')
        
        # Fetch the cycle object and user info
        cycle_object = GeneratedCycle.objects.get(id=cycle_id)
        user_info = EndUser.objects.get(id=user_id)

        # Fetch total advance payments
        total_advance_payment = AdvancePayment.objects.filter(
            enduser=user_info,
            transaction_type='withdrawal'
        ).aggregate(total_bonus=Sum(F('payment_amount')))['total_bonus']

        # Fetch last deduction amount
        last_deduction_amount = AdvancePayment.objects.filter(
            enduser=user_info,
            transaction_type='deduct',
            advance_taken_cycle=cycle_object,
        ).exclude(payment_date__gt=timezone.now().date(), payment_time__gt=timezone.now().time()
        ).order_by(F('payment_date').desc(), F('payment_time').desc()
        ).values('payment_amount').first()

        last_deduction_amount = last_deduction_amount['payment_amount'] if last_deduction_amount else 0

        # Calculate total remaining amount
        total_remaining_amount = EndUser.objects.filter(id=user_info.id).annotate(
            total_advance=Sum(
                Case(
                    When(advance_payments__transaction_type='withdrawal', then=F('advance_payments__payment_amount')),
                    When(advance_payments__transaction_type='deduct', then=-F('advance_payments__payment_amount')),
                    default=Value(0),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                )
            )
        ).values('total_advance').first()
        
        total_remaining_amount = total_remaining_amount['total_advance'] if total_remaining_amount else 0.00

        # Calculate bonus-related values
        from_date = cycle_object.from_date
        to_date = cycle_object.to_date
        bonus_sum = Bonus.objects.filter(
            user_id=user_id,
            transaction_type='bonus_added'
        ).aggregate(Sum('bonus_amount')).get('bonus_amount__sum') or 0
        last_cycle_bonus_deduct = Bonus.objects.filter(
            user_id=user_id,
            transaction_type='bonus_added',
            bonus_date__range=(from_date, to_date)
        ).aggregate(Sum('bonus_amount')).get('bonus_amount__sum') or 0

        # Calculate milk transaction amounts and liters
        milk_transation_amount_sum_morning = MilkTransaction.objects.filter(
            end_user=user_info,
            date__range=(from_date, to_date),
            transaction_shift='M'
        ).aggregate(Sum('transaction_amount')).get('transaction_amount__sum') or 0
        milk_transation_amount_sum_evening = MilkTransaction.objects.filter(
            end_user=user_info,
            date__range=(from_date, to_date),
            transaction_shift='E'
        ).aggregate(Sum('transaction_amount')).get('transaction_amount__sum') or 0

        milk_transation_liter_sum_morning = MilkTransaction.objects.filter(
            end_user=user_info,
            date__range=(from_date, to_date),
            transaction_shift='M'
        ).aggregate(Sum('transaction_liters')).get('transaction_liters__sum') or 0
        milk_transation_liter_sum_evening = MilkTransaction.objects.filter(
            end_user=user_info,
            date__range=(from_date, to_date),
            transaction_shift='E'
        ).aggregate(Sum('transaction_liters')).get('transaction_liters__sum') or 0

        milk_transation_amount_sum = milk_transation_amount_sum_morning + milk_transation_amount_sum_evening
        milk_transation_liter_sum = milk_transation_liter_sum_morning + milk_transation_liter_sum_evening

        # Fetch feed purchases
        # feed_purchase = FeedPurchase.objects.filter(
        #     taken_user=user_info,
        #     is_paid=False,
        #     date_created__range=(from_date, to_date),
        # )
        feed_purchase = FeedPurchase.objects.filter(
            taken_user=user_info,
            date_created__range=(from_date, to_date),
        )
        for feed in feed_purchase:
            feed.is_paid = True
            feed.save()

        total_feed_quantity = feed_purchase.aggregate(Sum('quantity_taken')).get('quantity_taken__sum') or 0
        total_purchase_amount = feed_purchase.aggregate(Sum('total_purchase_amount')).get('total_purchase_amount__sum') or 0

        bill_total_purchase_amount = total_purchase_amount
        if total_purchase_amount > (milk_transation_amount_sum-last_cycle_bonus_deduct):
            amt_forward_next_month = total_purchase_amount - (milk_transation_amount_sum-last_cycle_bonus_deduct)
           
            feed_purchase_instance, created = FeedPurchase.objects.get_or_create(
                taken_user=user_info,
                quantity_taken='0',
                purchase_amount=amt_forward_next_month,
                total_purchase_amount=amt_forward_next_month,
                created_by=self.request.user,
                dairy=self.request.user.dairy,
                extra_field="उर्वरित रक्कम"
            )
            total_purchase_amount=total_purchase_amount-amt_forward_next_month

        # Calculate the final amount
        finale_amount = (milk_transation_amount_sum - last_cycle_bonus_deduct - last_deduction_amount - total_purchase_amount)

        context.update({
            'milk_transation_amount_sum_morning': milk_transation_amount_sum_morning,
            'milk_transation_amount_sum_evening': milk_transation_amount_sum_evening,
            'milk_transation_liter_sum_morning': milk_transation_liter_sum_morning,
            'milk_transation_liter_sum_evening': milk_transation_liter_sum_evening,
            'finale_amount': finale_amount,
            'feed_purchase': feed_purchase,
            'total_feed_quantity': total_feed_quantity,
            'total_Purchase_amount': total_purchase_amount,
            'milk_transation_liter_sum': milk_transation_liter_sum,
            'milk_transation_sum': milk_transation_amount_sum,
            'last_cycle_bonus_deduct': last_cycle_bonus_deduct,
            'total_bonus': bonus_sum,
            'total_advanced_amount': total_advance_payment,
            'last_deduction_amount': last_deduction_amount,
            'remaining_amount': total_remaining_amount,
            'current_date': date.today(),
            'cycle_name': cycle_object,
            'user_info': user_info,
            'bill_total_purchase_amount':bill_total_purchase_amount,
        })

        return context
    
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def deduct_amount_view(request):
    if request.method == 'POST':
        try:
            deduction_amount = float(request.POST.get('deduction_amount', 0))
            user_id = request.POST.get('user_id')
            cycle_id = request.POST.get('cycle_id')
            user = EndUser.objects.get(id=user_id)

            cycle_object = GeneratedCycle.objects.get(id=cycle_id)
            from_date = cycle_object.from_date
            to_date = cycle_object.to_date
            # advance_payment_id = request.POST.get('advance_payment_id')

            # Assuming you have a specific AdvancePayment instance to deduct from
            total_advance_payment = AdvancePayment.objects.filter(enduser=user, transaction_type='withdrawal').aggregate(total_bonus=Sum(F('payment_amount')))['total_bonus'] or 0
            current_date = date.today()
            # print('deduction_amount',deduction_amount)
            # print('total_advance_payment',total_advance_payment)
            if total_advance_payment > deduction_amount:
                AdvancePayment.objects.create(enduser=user,dairy=request.user.dairy,advance_taken_cycle=cycle_object, payment_amount=deduction_amount,description=f'Amount is dedcuted from the bill and bill date {current_date}',transaction_type='deduct') or 0
                # return JsonResponse({'success': True, 'message': 'Deduction successful.'})
                total_advance_payment_taken= AdvancePayment.objects.filter(enduser=user, transaction_type='withdrawal').aggregate(total_bonus=Sum(F('payment_amount')))['total_bonus'] or 0
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
                                    ).values('total_advance').first() or 0
                
                last_deduction_amount = AdvancePayment.objects.filter(
                    enduser=user,
                    transaction_type='deduct'
                ).exclude(payment_date__gt=timezone.now().date(), payment_time__gt=timezone.now().time()).order_by(
                    F('payment_date').desc(), F('payment_time').desc()
                ).values('payment_amount').first() or 0

                if last_deduction_amount:
                    last_deduction_amount = last_deduction_amount['payment_amount']
                else:
                    last_deduction_amount = 0
                

                milk_transation_amount_sum = MilkTransaction.objects.filter(end_user=user,date__range=(from_date,to_date)).aggregate(Sum('transaction_amount')).get('transaction_amount__sum') or 0
                last_cycle_bonus_deduct = Bonus.objects.filter(user_id=user, transaction_type='bonus_added',bonus_date__range=(from_date,to_date)).aggregate(Sum('bonus_amount')).get('bonus_amount__sum') or 0
                total_Purchase_amount = FeedPurchase.objects.filter(taken_user=user,date_created__range=(from_date,to_date)).aggregate(Sum('total_purchase_amount')).get('total_purchase_amount__sum') or 0
                finale_amount = (milk_transation_amount_sum-last_cycle_bonus_deduct-last_deduction_amount-total_Purchase_amount) or 0
                
                print('milk_transation_amount_sum',milk_transation_amount_sum)
                print('last_cycle_bonus_deduct',last_cycle_bonus_deduct)
                print('last_deduction_amount',last_deduction_amount)
                print('total_Purchase_amount',total_Purchase_amount)
                # print('remaining_amount',total_remaining_amount.get('total_advance'))
                # print('deduction_amount',deduction_amount)
                # print('last_deduction_amount',last_deduction_amount)
                
                return JsonResponse({
                'success': True,
                'message': 'Deduction successful.',
                'total_advance_payment_taken':total_advance_payment_taken,
                'last_deduction_amount': last_deduction_amount,  # Add this line to include the updated total amount deduction
                'finale_adv_deduction_amount': last_deduction_amount,  # Add this line to include the updated total amount deduction
                'remaining_amount': total_remaining_amount.get('total_advance'),  # Add this line to include the updated remaining amount

                'milk_transation_amount_sum':milk_transation_amount_sum,
                'last_cycle_bonus_deduct':last_cycle_bonus_deduct,
                'total_Purchase_amount':total_Purchase_amount,
                'finale_amount':finale_amount,


            })
            else:
                return JsonResponse({'success': False, 'message': f'Total Advance Amount is {total_advance_payment} smaller than {deduction_amount}. Please enter the correct amount'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)



def save_data(request):
    if request.method == 'POST':
        feed_purchase_ids = request.POST.getlist('feed_purchase_ids[]')
        print("***************"*1000)
        print('feed_purchase_ids',feed_purchase_ids)

        # Implement your data-saving logic here, e.g., saving to the database

        # Return a JSON response to indicate success
        return JsonResponse({'success': True})

    # Handle other HTTP methods or errors if needed
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@method_decorator(login_required, name='dispatch')
class GeneratedCycleListView(ListView):
    model = GeneratedCycle
    template_name = 'bill_management/generated_cycles_list.html'
    context_object_name = 'generated_cycles'
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_date'] = datetime.now().date()  
        return context


@method_decorator(login_required, name='dispatch')
class BillingReports(ListView):
    pass
