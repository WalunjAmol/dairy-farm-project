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

class DashboardView(LoginRequiredMixin, TemplateView):
    model = MilkTransaction
    template_name = 'dairy_owner_dashboard/content.html'
    login_url = '/dairy-management/login/'
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetching milk production data month-wise
        milk_production_data = MilkTransaction.objects \
            .annotate(month=TruncMonth('date')) \
            .values('month') \
            .annotate(total_liters=Sum('transaction_liters')) \
            .order_by('month') \
            .values_list('month', 'total_liters')

        # Converting the fetched data into the required structure
        labels = [month.strftime('%B') for month in milk_production_data.values_list('month', flat=True)]

        # Convert Decimal values to floats
        total_liters_list = [float(total_liters) for total_liters in milk_production_data.values_list('total_liters', flat=True)]
        print('total_liters_list',total_liters_list)
        datasets = [{
            'label': 'Milk Production (in liters)',
            'data': total_liters_list,
            'backgroundColor': 'rgba(54, 162, 235, 0.6)',
            'borderColor': 'rgba(54, 162, 235, 1)',
            'borderWidth': 1
        }]
        print('dataset',datasets)

        milk_production_data_structure = {
            'labels': labels,
            'datasets': datasets
        }

        context['milk_production_data'] = milk_production_data_structure

        return context

class HomeView(TemplateView):
    template_name='home/home.html'
    # login_url= '/dairy-management/login/'
    # redirect_field_name = 'redirect_to'