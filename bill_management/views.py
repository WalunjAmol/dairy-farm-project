from datetime import datetime,timedelta
from django.views import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import GeneratedCycle  
from milk_transaction.models import MilkTransaction
from end_user_management.models import EndUser


class ProcessAndStoreObjectsView(View):

    # CYCLE_DAYS = [1, 16]

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


        cycles = GeneratedCycle.objects.all()

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
            queryset = self.model.objects.filter(dairy_name__role=user_dairy_role)
        
        return queryset