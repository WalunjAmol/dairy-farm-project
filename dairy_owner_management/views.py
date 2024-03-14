from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import auth
from django.contrib.auth.mixins import LoginRequiredMixin
from milk_transaction.models import MilkTransaction


from .forms import CustomLoginForm


class CustomLoginView(FormView):
    template_name = 'dairy_owner_management/login.html'
    success_url = reverse_lazy('dairy_owner_management:dashboard') 
    form_class = CustomLoginForm

    def get_success_url(self):
        if "next" in self.request.GET and self.request.GET["next"] != "":
            return self.request.GET["next"]
        else:
            return self.success_url

    def get_form_class(self):
        return self.form_class

    def form_valid(self, form):
        auth.login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""
        print('test',form.errors)
        return self.render_to_response(self.get_context_data(form=form))


from decimal import Decimal
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.db.models import Sum, DecimalField
from bill_management.models import GeneratedCycle
from django.db.models import Sum, Avg, DecimalField


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dairy_owner_dashboard/content.html'
    login_url = '/dairy-management/login/'
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch all cycles for the dairy owner
        # all_cycles = GeneratedCycle.objects.filter(dairy_owner=self.request.user)
        all_cycles = GeneratedCycle.objects.all()


        # Initialize lists to store data for all cycles
        all_cycle_names = []
        all_total_liters = []
        all_avg_fat = []
        all_avg_snf = []
        all_avg_rate = []
        all_aggregated_data = []


        for current_cycle in all_cycles:
            # milk_production_data = MilkTransaction.objects \
            #     .filter(date__range=[current_cycle.from_date, current_cycle.to_date], dairy=current_cycle.dairy_name) \
            #     .aggregate(
            #         total_liters=Sum('transaction_liters', output_field=DecimalField()),
            #         avg_fat=Avg('transaction_fat'),
            #         avg_snf=Avg('transaction_snf'),
            #         avg_rate=Avg('transaction_rate')
            #     )
            
            milk_production_data = MilkTransaction.objects \
                .filter(date__range=[current_cycle.from_date, current_cycle.to_date]) \
                .aggregate(
                    total_liters=Sum('transaction_liters', output_field=DecimalField()),
                    avg_fat=Avg('transaction_fat'),
                    avg_snf=Avg('transaction_snf'),
                    avg_rate=Avg('transaction_rate')
                )


            total_liters = float(milk_production_data['total_liters']) if milk_production_data['total_liters'] else 0
            avg_fat = float(milk_production_data['avg_fat']) if milk_production_data['avg_fat'] is not None else 0
            avg_snf = float(milk_production_data['avg_snf']) if milk_production_data['avg_snf'] is not None else 0
            avg_rate =float(milk_production_data['avg_rate']) if milk_production_data['avg_rate'] is not None else 0

            aggregated_data = {
            'cycle_name': current_cycle.name,
            'total_liters': float(milk_production_data['total_liters']) if milk_production_data['total_liters'] else 0,
            'avg_fat': float(milk_production_data['avg_fat']) if milk_production_data['avg_fat'] is not None else 0,
            'avg_snf': float(milk_production_data['avg_snf']) if milk_production_data['avg_snf'] is not None else 0,
            'avg_rate': float(milk_production_data['avg_rate']) if milk_production_data['avg_rate'] is not None else 0,
        }

            all_cycle_names.append(current_cycle.name)
            all_total_liters.append(total_liters)
            all_avg_fat.append(avg_fat)
            all_avg_snf.append(avg_snf)
            all_avg_rate.append(avg_rate)
            all_aggregated_data.append(aggregated_data)

            

        context['cycle_names'] = all_cycle_names
        context['total_liters'] = all_total_liters
        context['avg_fat'] = all_avg_fat
        context['avg_snf'] = all_avg_snf
        context['avg_rate'] = all_avg_rate
        context['aggregated_data'] = all_aggregated_data

        return context
class HomeView(TemplateView):
    
        template_name='home/home.html'
    # login_url= '/dairy-management/login/'
    # redirect_field_name = 'redirect_to'