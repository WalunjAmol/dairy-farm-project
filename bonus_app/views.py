#django Imports
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy,reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Sum
from django.contrib import messages
from django.http import HttpResponseRedirect

#Local Import
from .models import EndUser
from .forms import BonusForm
from .models import Bonus

@method_decorator(login_required, name='dispatch')
class BonusEndUserListView(ListView):
    model = EndUser
    template_name = 'bonus_app/bonus_enduser_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        user_dairy_role = self.request.user.dairy.role
        if self.request.user.is_superuser:
            queryset = self.model.objects.filter(dairy_name__role=user_dairy_role)
        else:
            queryset = self.model.objects.filter(dairy_name__role=user_dairy_role)

        queryset = queryset.annotate(total_bonus=Sum('bonuses__bonus_amount'))

        return queryset


@method_decorator(login_required, name='dispatch')
class BonusDetailView(DetailView):
    model = EndUser
    template_name = 'bonus_app/bonus_details.html'
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
        total_bonus = Bonus.objects.filter(user=user).aggregate(total_bonus=Sum('bonus_amount'))['total_bonus']
        context['total_bonus'] = total_bonus
        context['transactions'] = Bonus.objects.filter(user=user).order_by('bonus_date')
        return context

class BonusCreateView(CreateView):
    model = Bonus
    form_class = BonusForm
    template_name = 'bonus_app/bonus_form.html'  # Change this to your template path

    def get(self, request, *args, **kwargs):
        form = BonusForm(user = self.request.user)
        return render(request, self.template_name, {'form':form})
    
    def post(self, request, *args, **kwargs):
        data =  request.POST
        print("assadsd",data)
        form = BonusForm(data=data,user=request.user)

        if not form.is_valid():
            return render(request, self.template_name, {'form':form})

        if form.is_valid():
            form.save()
            messages.success(self.request, 'Bonus Record Created Successfully.')
            
        return HttpResponseRedirect(reverse('bonus:bonus-detail', args=[ request.POST.get('user')]))

class BonusListView(ListView):
    model = Bonus
    template_name = 'bonus_app/bonus_list.html'  # Change this to your template path
    context_object_name = 'bonuses'

    def get_queryset(self):
        # Retrieve the original queryset using super()
        queryset = super().get_queryset()

        # Add ordering by the EndUser ID
        queryset = queryset.order_by('enduser__custom_id')

        return queryset

class BonusUpdateView(UpdateView):
    model = Bonus
    template_name = 'bonus/bonus_form.html'  # Change this to your template path
    fields = ['user', 'bonus_date', 'bonus_amount', 'description', 'is_approved', 'is_paid', 'payment_date', 'payment_method']

class BonusDeleteView(DeleteView):
    model = Bonus
    template_name = 'bonus/bonus_confirm_delete.html'  # Change this to your template path
    success_url = reverse_lazy('bonus-list')  # URL to redirect after successful deletion
