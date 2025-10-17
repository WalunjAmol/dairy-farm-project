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
            queryset = self.model.objects.filter(dairy_name__role=user_dairy_role).order_by('custom_id')

        queryset = queryset.annotate(total_bonus=Sum('bonuses__bonus_amount'))

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate total bonus for all end users
        bonus = Bonus.objects.filter(user__dairy_name=self.request.user.dairy)
        total_bonus = bonus.aggregate(Sum('bonus_amount'))['bonus_amount__sum']
        context['total_bonus'] = total_bonus if total_bonus else 0.0

        return context


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


from django.shortcuts import render, get_object_or_404
from .models import Bonus, EndUser
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import datetime
from django.db.models import F, ExpressionWrapper, FloatField

def user_bonuses(request, user_id):
    # Define the date range
    start_date = datetime(2024, 10, 1)
    end_date = datetime(2025, 9, 30)

    # Fetch the user and their bonuses
    user = get_object_or_404(EndUser, id=user_id)
    bonuses = (
        Bonus.objects
        .filter(user=user, bonus_date__range=(start_date, end_date))
        .annotate(month=TruncMonth('bonus_date'))
        .values('month')
        .annotate(total_bonus=Sum('bonus_amount'))
        .annotate(extra_bonus=ExpressionWrapper(F('total_bonus') * 0.50, output_field=FloatField()))
        .order_by('month')
    )
    
    # Calculate the total bonus amount for the user
    total_bonus_amount = bonuses.aggregate(Sum('total_bonus'))['total_bonus__sum'] or 0
    total_extra_bonus_amount = bonuses.aggregate(Sum('extra_bonus'))['extra_bonus__sum'] or 0

    return render(request, 'bonus_app/user_bonus.html', {
        'user': user,
        'bonuses': bonuses,
        'total_bonus_amount': total_bonus_amount,
        'total_extra_bonus_amount': total_extra_bonus_amount,
    })


from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

# Define the date range
START_DATE = datetime(2024, 10, 1)
END_DATE = datetime(2025, 9, 30)

@csrf_exempt
def update_bonus_status(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')

        # Fetch bonuses that have not been paid
        bonuses = Bonus.objects.filter(user_id=user_id, is_paid=False)

        if bonuses.exists():
            for bonus in bonuses:
                # Convert bonus_date to datetime
                bonus_date = datetime.combine(bonus.bonus_date, datetime.min.time())

                # Check if the bonus_date is within the allowed range
                if START_DATE <= bonus_date <= END_DATE:
                    bonus.is_paid = True
                    bonus.transaction_type = 'withdrawal'  # Set the transaction type as needed
                    bonus.save()
                
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'बोनस आधीच देण्यात आले आहे.'})

    return JsonResponse({'success': False})


from decimal import Decimal
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from datetime import datetime
from django.shortcuts import render

def all_user_bonuses(request):
    # Define the date range
    start_date = datetime(2024, 10, 1)
    end_date = datetime(2025, 9, 30)

    # Fetch all users and calculate their bonuses
    users = EndUser.objects.all().prefetch_related('bonuses')

    user_bonus_data = []
    grand_total_bonus_amount = Decimal('0.00')
    grand_total_extra_bonus_amount = Decimal('0.00')

    for user in users:
        bonuses = (
            Bonus.objects
            .filter(user=user, bonus_date__range=(start_date, end_date))
            .annotate(total_bonus=Sum('bonus_amount'))
            .annotate(extra_bonus=ExpressionWrapper(F('total_bonus') * Decimal('0.50'), output_field=DecimalField()))
        )

        total_bonus_amount = bonuses.aggregate(Sum('total_bonus'))['total_bonus__sum'] or Decimal('0.00')
        total_extra_bonus_amount = bonuses.aggregate(Sum('extra_bonus'))['extra_bonus__sum'] or Decimal('0.00')

        # Only include users with non-zero bonuses
        if total_bonus_amount > 0 or total_extra_bonus_amount > 0:
            combined_total = total_bonus_amount + total_extra_bonus_amount

            user_bonus_data.append({
                'user': user,
                'total_bonus_amount': total_bonus_amount,
                'total_extra_bonus_amount': total_extra_bonus_amount,
                'combined_total': combined_total,
            })

            # Update grand totals
            grand_total_bonus_amount += total_bonus_amount
            grand_total_extra_bonus_amount += total_extra_bonus_amount

    grand_combined_total = grand_total_bonus_amount + grand_total_extra_bonus_amount

    return render(request, 'bonus_app/all_user_bonuses.html', {
        'user_bonus_data': user_bonus_data,
        'grand_total_bonus_amount': grand_total_bonus_amount,
        'grand_total_extra_bonus_amount': grand_total_extra_bonus_amount,
        'grand_combined_total': grand_combined_total,
    })
