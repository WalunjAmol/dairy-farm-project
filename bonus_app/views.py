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

def bonus_gaps_by_user(users, start_date, end_date, gap_days=15):
    """Gaps longer than gap_days whose empty stretch crosses the given date range.

    Each gap is the last bonus date before the break and the next bonus date after it,
    for example 14 Aug 2025 to 1 Jun 2026.
    """
    from collections import defaultdict
    from django.db.models import Max, Min

    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()

    dates_by_user = defaultdict(list)
    previous_bonus = (
        Bonus.objects.filter(user__in=users, bonus_date__lt=start_date)
        .values('user_id')
        .annotate(last_date=Max('bonus_date'))
    )
    for row in previous_bonus:
        dates_by_user[row['user_id']].append(row['last_date'])

    bonus_dates = (
        Bonus.objects.filter(user__in=users, bonus_date__range=(start_date, end_date))
        .order_by('user_id', 'bonus_date')
        .values_list('user_id', 'bonus_date')
        .distinct()
    )
    for user_id, bonus_date in bonus_dates:
        known_dates = dates_by_user[user_id]
        if not known_dates or known_dates[-1] != bonus_date:
            known_dates.append(bonus_date)

    next_bonus = {
        row['user_id']: row['first_date']
        for row in Bonus.objects.filter(user__in=users, bonus_date__gt=end_date)
        .values('user_id')
        .annotate(first_date=Min('bonus_date'))
    }
    for user_id, bonus_date in next_bonus.items():
        known_dates = dates_by_user[user_id]
        if not known_dates or known_dates[-1] != bonus_date:
            known_dates.append(bonus_date)

    gaps_by_user = defaultdict(list)
    for user_id, dates in dates_by_user.items():
        ordered_dates = sorted(set(dates))
        for previous_date, current_date in zip(ordered_dates, ordered_dates[1:]):
            crosses_range = previous_date < end_date and current_date > start_date
            if crosses_range and (current_date - previous_date).days > gap_days:
                gaps_by_user[user_id].append((previous_date, current_date))
    return gaps_by_user


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
        gaps_by_user = bonus_gaps_by_user(
            context['users'],
            datetime(2025, 10, 1).date(),
            datetime(2026, 9, 30).date(),
        )
        for customer in context['users']:
            customer.bonus_gaps = gaps_by_user.get(customer.id, [])

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
        transactions = list(Bonus.objects.filter(user=user).order_by('bonus_date', 'bonus_time', 'id'))
        context['transactions'] = transactions
        gaps = bonus_gaps_by_user(
            EndUser.objects.filter(pk=user.pk),
            datetime(2025, 10, 1).date(),
            datetime(2026, 9, 30).date(),
        ).get(user.pk, [])
        context['bonus_gaps'] = gaps
        gap_after = {start: end for start, end in gaps}
        gap_before = {end: start for start, end in gaps}
        display_rows = []
        for index, transaction in enumerate(transactions):
            previous_date = transactions[index - 1].bonus_date if index else None
            next_date = transactions[index + 1].bonus_date if index + 1 < len(transactions) else None
            is_gap_start = transaction.bonus_date in gap_after and next_date != transaction.bonus_date
            is_gap_end = transaction.bonus_date in gap_before and previous_date != transaction.bonus_date
            display_rows.append({
                'kind': 'transaction',
                'transaction': transaction,
                'highlight': is_gap_start or is_gap_end,
            })
            if is_gap_start:
                display_rows.append({
                    'kind': 'gap',
                    'start': transaction.bonus_date,
                    'end': gap_after[transaction.bonus_date],
                })
        context['display_rows'] = display_rows
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
    start_date = datetime(2025, 10, 1)
    end_date = datetime(2026, 9, 30)

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
START_DATE = datetime(2025, 10, 1)
END_DATE = datetime(2026, 9, 30)

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
    start_date = datetime(2025, 10, 1)
    end_date = datetime(2026, 9, 30)

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


def _cycle_customers(request):
    if not getattr(request.user, 'dairy_id', None):
        return EndUser.objects.none()
    return EndUser.objects.filter(dairy_name__role=request.user.dairy.role).order_by('custom_id')


def _customer_bonus_slips(customers, start_date, end_date):
    from collections import defaultdict

    month_rows = (
        Bonus.objects.filter(user__in=customers, bonus_date__range=(start_date, end_date))
        .annotate(month=TruncMonth('bonus_date'))
        .values('user_id', 'month')
        .annotate(total_bonus=Sum('bonus_amount'))
        .order_by('month')
    )
    months_by_user = defaultdict(list)
    for row in month_rows:
        total_bonus = row['total_bonus'] or Decimal('0.00')
        months_by_user[row['user_id']].append({
            'month': row['month'],
            'total_bonus': total_bonus,
            'extra_bonus': (total_bonus * Decimal('0.50')),
        })

    slips = []
    for customer in customers:
        months = months_by_user.get(customer.id)
        if not months:
            continue
        slips.append({
            'user': customer,
            'bonuses': months,
            'total_bonus_amount': sum(month['total_bonus'] for month in months),
            'total_extra_bonus_amount': sum(month['extra_bonus'] for month in months),
        })
    return slips


@login_required(login_url='/dairy-management/login/')
def print_all_user_bonuses(request):
    start_date = datetime(2025, 10, 1)
    end_date = datetime(2026, 9, 30)
    slips = _customer_bonus_slips(_cycle_customers(request), start_date, end_date)
    return render(request, 'bonus_app/print_all_bonuses.html', {
        'slips': slips,
        'start_date': start_date,
        'end_date': end_date,
    })


@login_required(login_url='/dairy-management/login/')
def update_all_bonus_status(request):
    if request.method != 'POST':
        return JsonResponse({'success': False}, status=405)

    updated = Bonus.objects.filter(
        user__in=_cycle_customers(request),
        is_paid=False,
        bonus_date__gte=START_DATE.date(),
        bonus_date__lte=END_DATE.date(),
    ).update(is_paid=True, transaction_type='withdrawal')
    return JsonResponse({'success': True, 'updated': updated})


def _bonus_delete_queryset(user, start_date, end_date, customer_id, search_text):
    bonuses = Bonus.objects.filter(
        user__dairy_name=user.dairy,
        bonus_date__gte=start_date,
        bonus_date__lte=end_date,
    ).select_related('user')

    if customer_id:
        customer = EndUser.objects.filter(pk=customer_id, dairy_name=user.dairy).first()
        if not customer:
            return None
        bonuses = bonuses.filter(user=customer)

    search_text = (search_text or '').strip()
    if search_text:
        from django.db.models import Q
        matched = (
            Q(user__marathi_name__icontains=search_text) |
            Q(user__first_name__icontains=search_text) |
            Q(user__last_name__icontains=search_text) |
            Q(description__icontains=search_text)
        )
        if search_text.isdigit():
            matched = matched | Q(user__custom_id=int(search_text))
        bonuses = bonuses.filter(matched)

    return bonuses


def _serialize_bonus_record(bonus):
    customer = bonus.user
    name = (customer.marathi_name or '').strip()
    if not name:
        name = ' '.join(part for part in (customer.first_name, customer.last_name) if part)
    type_labels = {
        'bonus_added': 'Bonus added',
        'withdrawal': 'Withdrawal',
    }
    return {
        'id': bonus.id,
        'customer_id': customer.custom_id,
        'name': name,
        'bonus_date': bonus.bonus_date.strftime('%d-%m-%Y'),
        'bonus_time': bonus.bonus_time.strftime('%H:%M') if bonus.bonus_time else '',
        'amount': f'{bonus.bonus_amount:.2f}',
        'description': bonus.description or '',
        'is_paid': bonus.is_paid,
        'transaction_type': type_labels.get(bonus.transaction_type, ''),
    }


@login_required(login_url='/dairy-management/login/')
def delete_bonus_by_date(request):
    """Show each bonus row and delete by selection without reloading the page."""
    import json
    from django.core.paginator import Paginator
    from django.db import transaction
    from django.db.models import Count, Sum
    from django.http import JsonResponse

    if request.method == 'GET':
        return render(request, 'bonus_app/delete_bonus_by_date.html', {
            'start_date': '2024-10-01',
            'end_date': '2025-11-30',
            'customers': EndUser.objects.filter(dairy_name=request.user.dairy).order_by('custom_id'),
        })

    try:
        payload = json.loads(request.body.decode() or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request.'}, status=400)

    if not request.user.dairy_id:
        return JsonResponse({'error': 'Your account is not linked to a dairy.'}, status=400)

    try:
        start_date = datetime.strptime(payload.get('start_date') or '', '%Y-%m-%d').date()
        end_date = datetime.strptime(payload.get('end_date') or '', '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Select both a start date and an end date.'}, status=400)

    if start_date > end_date:
        return JsonResponse({'error': 'The start date must be on or before the end date.'}, status=400)

    bonuses = _bonus_delete_queryset(
        request.user,
        start_date,
        end_date,
        payload.get('user_id') or '',
        payload.get('q') or '',
    )
    if bonuses is None:
        return JsonResponse({'error': 'Select a customer from your dairy.'}, status=400)

    action = payload.get('action')
    if action == 'list':
        try:
            page_number = int(payload.get('page') or 1)
        except (TypeError, ValueError):
            page_number = 1

        summary = bonuses.aggregate(record_count=Count('id'), total_amount=Sum('bonus_amount'))
        ordered = bonuses.order_by('bonus_date', 'bonus_time', 'id')
        page_size_raw = str(payload.get('page_size') or '25').lower()
        allowed_sizes = {'25', '50', '100', '250'}
        if page_size_raw == 'all':
            record_list = list(ordered)
            page_number = 1
            page_count = 1
            page_size_label = 'all'
        else:
            if page_size_raw not in allowed_sizes:
                page_size_raw = '25'
            paginator = Paginator(ordered, int(page_size_raw))
            page = paginator.get_page(page_number)
            record_list = list(page.object_list)
            page_number = page.number
            page_count = paginator.num_pages
            page_size_label = int(page_size_raw)
        return JsonResponse({
            'count': summary['record_count'] or 0,
            'total_amount': f"{summary['total_amount'] or 0:.2f}",
            'page': page_number,
            'pages': page_count,
            'page_size': page_size_label,
            'records': [_serialize_bonus_record(bonus) for bonus in record_list],
        })

    if action == 'delete':
        if (payload.get('confirm_text') or '').strip() != 'DELETE':
            return JsonResponse({'error': 'Type DELETE to confirm.'}, status=400)
        mode = payload.get('mode')
        if mode == 'ids':
            raw_ids = payload.get('ids') or []
            if not isinstance(raw_ids, list) or not raw_ids:
                return JsonResponse({'error': 'Select at least one record.'}, status=400)
            try:
                record_ids = [int(record_id) for record_id in raw_ids]
            except (TypeError, ValueError):
                return JsonResponse({'error': 'Select at least one record.'}, status=400)
            bonuses = bonuses.filter(id__in=record_ids)
        elif mode != 'all':
            return JsonResponse({'error': 'Choose which records to delete.'}, status=400)

        record_count = bonuses.count()
        if not record_count:
            return JsonResponse({'error': 'No matching bonus records.'}, status=400)

        with transaction.atomic():
            bonuses.delete()
        return JsonResponse({'deleted': record_count})

    return JsonResponse({'error': 'Unknown action.'}, status=400)
