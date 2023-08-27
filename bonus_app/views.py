from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Bonus

class BonusListView(ListView):
    model = Bonus
    template_name = 'bonus/bonus_list.html'  # Change this to your template path
    context_object_name = 'bonuses'

class BonusDetailView(DetailView):
    model = Bonus
    template_name = 'bonus/bonus_detail.html'  # Change this to your template path
    context_object_name = 'bonus'

class BonusCreateView(CreateView):
    model = Bonus
    template_name = 'bonus/bonus_form.html'  # Change this to your template path
    fields = ['user', 'bonus_date', 'bonus_amount', 'description', 'is_approved', 'is_paid', 'payment_date', 'payment_method']

class BonusUpdateView(UpdateView):
    model = Bonus
    template_name = 'bonus/bonus_form.html'  # Change this to your template path
    fields = ['user', 'bonus_date', 'bonus_amount', 'description', 'is_approved', 'is_paid', 'payment_date', 'payment_method']

class BonusDeleteView(DeleteView):
    model = Bonus
    template_name = 'bonus/bonus_confirm_delete.html'  # Change this to your template path
    success_url = reverse_lazy('bonus-list')  # URL to redirect after successful deletion
