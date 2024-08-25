#Django Import
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

#Python Imports
from datetime import datetime
from datetime import date, timedelta
from decimal import Decimal
import csv

#Local Import
from .models import EndUser, MilkTransaction, ImportTransaction,Dairy
from  bonus_app.models import Bonus
from .forms import MilkTransactionForm
from django.db.models import Q

@method_decorator(login_required, name='dispatch')
class MilkTransactionListView(ListView):
    model = Dairy
    template_name = 'milk_transaction/transaction_list.html'
    context_object_name = 'transactions'

    # def get_queryset(self):
    #     user = self.request.user
    #     queryset = MilkTransaction.objects.filter(end_user__dairy_name__role=user.dairy.role)
    #     queryset = queryset.order_by('-date')  # Order by the 'date' field in descending order

    #     return queryset

from django.views import View
from django.core.paginator import Paginator
from django.urls import reverse

@csrf_exempt
def datatable_data(request):
    user = request.user
    queryset = MilkTransaction.objects.filter(end_user__dairy_name__role=user.dairy.role)
    queryset = queryset.order_by('-date')

    page_length = int(request.GET.get('length', 10))
    page_number = int(request.GET.get('start', 0)) // page_length + 1

    order_column_index = int(request.GET.get('order[0][column]', 0))
    order_direction = request.GET.get('order[0][dir]', 'asc')
    order_column = request.GET.get(f'columns[{order_column_index}][data]', '')
    if order_direction == 'asc':
        queryset = queryset.order_by(order_column)
    else:
        queryset = queryset.order_by(f'-{order_column}')

     # Apply search filter
    search_value = request.GET.get('search[value]', '')
    # print('*'*100,request.GET)
    if search_value:
        queryset = queryset.filter(
            Q(end_user__id__icontains=search_value) |
            Q(date__icontains=search_value) |
            Q(time__icontains=search_value) |
            Q(end_user__first_name__icontains=search_value) |
            Q(end_user__last_name__icontains=search_value) |
            Q(transaction_shift__icontains=search_value) |
            Q(transaction_liters__icontains=search_value) |
            Q(transaction_fat__icontains=search_value) |
            Q(transaction_snf__icontains=search_value) |
            Q(transaction_rate__icontains=search_value) |
            Q(transaction_amount__icontains=search_value) 
        )
    # Modify the search filter block
    for i in range(12):  # Assuming there are 12 columns in your DataTable
        column_search_value = request.GET.get(f'columns[{i}][search][value]', '')
        print('column_search_value',column_search_value)
        if column_search_value:
            column_data = request.GET.get(f'columns[{i}][name]', '')
            print('column_data',column_data)
            query_filter = f"{column_data}__contains"
            print('query_filter',query_filter)
            queryset = queryset.filter(Q(**{query_filter: column_search_value}))

    paginator = Paginator(queryset, page_length)
    page = paginator.page(page_number)

    data = [
        {   
            'date': item.date,
            'time': item.time,
            'end_user_id': item.end_user.custom_id,
            'end_user':f'{item.end_user.first_name} {item.end_user.last_name}',
            'transaction_shift': item.transaction_shift,
            'transaction_liters': item.transaction_liters,
            'transaction_fat': item.transaction_fat,
            'transaction_snf': item.transaction_snf,
            'transaction_rate': item.transaction_rate,
            'transaction_amount': item.transaction_amount,
            'update_url': reverse('milk_transaction:milk-transaction-update', args=[item.id])
        }
        for item in page.object_list
    ]

    return JsonResponse({
        'draw': int(request.GET.get('draw', 1)),
        'recordsTotal': queryset.count(),
        'recordsFiltered': paginator.count,
        'data': data,
    })
@method_decorator(login_required, name='dispatch')
class MilkTransactionCreateView(CreateView):
    model = MilkTransaction
    form_class = MilkTransactionForm
    template_name = 'milk_transaction/transaction_create.html'
    success_url = reverse_lazy('milk_transaction:milk-transaction-list')

    def get(self, request, *args, **kwargs):
        form = MilkTransactionForm(user=request.user)
        return render(request, self.template_name, {'form':form})
    
    def post(self, request, *args, **kwargs):
        data = request.POST
        form = MilkTransactionForm(data=data,user=request.user)

        if not form.is_valid():
            return render(request, self.template_name, {'form':form})

        if form.is_valid():
            milk_transaction_instance = form.save()  # Save the MilkTransaction and get the instance
            end_user = form.cleaned_data.get('end_user')
            date = form.cleaned_data.get('date')
            time = form.cleaned_data.get('time')
            transaction_liters = form.cleaned_data.get('transaction_liters')

            Bonus.objects.create(
                user=end_user,
                bonus_date=date,
                bonus_time=time,
                bonus_amount=Decimal(transaction_liters),
                description="Record added from the import transaction",
                transaction_type='bonus_added',
                transaction_source='manual',
                milk_transaction=milk_transaction_instance,  # Use the instance, not the ID
            )
            messages.success(self.request, 'Record Created Successfully.')

            return redirect('milk_transaction:milk-transaction-list')

    # def form_valid(self, form):
    #     form.instance.dairy = self.request.user.dairy
    #     messages.success(self.request, 'Record Created Successfully.')
    #     return super().form_valid(form)
    
    # def form_invalid(self,form):
    #     print('form',form.errors)
    

@method_decorator(login_required, name='dispatch')
class MilkTransactionUpdateView(UpdateView):
    model = MilkTransaction
    form_class = MilkTransactionForm
    template_name = 'milk_transaction/transaction_update.html'
    success_url = reverse_lazy('milk_transaction:milk-transaction-list')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = MilkTransactionForm(instance=self.object, user=request.user)
        return render(request, self.template_name, {'form': form, 'object': self.object})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = MilkTransactionForm(data=request.POST, instance=self.object, user=request.user)

        if not form.is_valid():
            return render(request, self.template_name, {'form': form, 'object': self.object})

        if form.is_valid():
            # Save the form to update the MilkTransaction object
            milk_transaction_instance = form.save()

            # Update the corresponding Bonus object
            bonus_obj = Bonus.objects.filter(milk_transaction=milk_transaction_instance).first()
            if bonus_obj:
                bonus_obj.bonus_amount = Decimal(milk_transaction_instance.transaction_liters)
                bonus_obj.save()

            messages.success(self.request, 'Record Updated Successfully.')
            return redirect('milk_transaction:milk-transaction-list')



    

@method_decorator(login_required, name='dispatch')
class MilkTransactionDeleteView(DeleteView):
    model = MilkTransaction
    template_name = 'milktransaction_confirm_delete.html'
    success_url = reverse_lazy('milk_transaction:milk-transaction-list')


# @csrf_exempt
# def import_transactions(request):
#     if request.method == 'GET':
#         transactions = ImportTransaction.objects.filter(dairy=request.user.dairy).order_by('-id').values()

#         context = {
#             'import_transactions': transactions
#         }
#         return render(request, 'milk_transaction/import_transactions_list.html', context)

        
#     if request.method == 'POST':
#         file = request.FILES.get('file')
#         if file:
#             # Process the uploaded file
#             lines_byte = file.readlines()
#             lines = lines_byte[0].decode('utf-8').split('\r')

#             success_records = []
#             failed_records = []

#             for line in lines:
#                 fields = line.strip().split(',')
#                 if len(fields) == 20:
#                     society_code, center_code, transaction_type, transaction_subtype, date_str, time_str, transaction_shift, transaction_producer, transaction_liters, transaction_fat, transaction_lacto, transaction_snf, transaction_water, transaction_protein, transaction_ph, transaction_rate, transaction_off_amount, transaction_amount, transaction_subtype_2, extra_data = fields

#                     transaction_liters = transaction_liters.replace('*', '0')
#                     transaction_fat = transaction_fat.replace('*', '')
#                     transaction_lacto = transaction_lacto.replace('*', '')
#                     transaction_snf = transaction_snf.replace('*', '')
#                     date = datetime.strptime(date_str, '%d/%m/%y').date()
#                     time = datetime.strptime(time_str, '%H:%M').time()
#                     print('transaction_liters',transaction_liters)
#                     try:
#                         end_user = EndUser.objects.get(dairy_name=request.user.dairy.id, custom_id=int(transaction_producer))
#                         dairy_id = request.user.dairy.id
#                         dairy = Dairy.objects.get(id=dairy_id)
#                     except EndUser.DoesNotExist:
#                         failed_records.append({
#                             'Reason': f"Customer with customer_id {transaction_producer} not found",
#                             'Customer_ID': transaction_producer,
#                             'Transaction_Shift': transaction_shift,
#                             'Transaction_Liters': transaction_liters,
#                             'Transaction_FAT': transaction_fat,
#                             'Transaction_SNF': transaction_snf,
#                             'Transaction_Amount': transaction_amount,
#                             'Date': date_str,
#                             'Time': time_str,
#                         })
#                         continue

#                     # Check if a similar transaction already exists
#                     existing_transaction = MilkTransaction.objects.filter(
#                         dairy=dairy,
#                         end_user=end_user,
#                         society_code=society_code,
#                         center_code=center_code,
#                         transaction_type=transaction_type,
#                         transaction_subtype=transaction_subtype,
#                         date=date,
#                         time=time,
#                         transaction_shift=transaction_shift,
#                         transaction_producer=transaction_producer,
#                         transaction_liters=Decimal(transaction_liters),
#                         transaction_fat=Decimal(transaction_fat),
#                         transaction_lacto=Decimal(transaction_lacto),
#                         transaction_snf=Decimal(transaction_snf),
#                         transaction_water=Decimal(transaction_water),
#                         transaction_protein=Decimal(transaction_protein),
#                         transaction_ph=Decimal(transaction_ph),
#                         transaction_rate=Decimal(transaction_rate),
#                         transaction_off_amount=Decimal(transaction_off_amount),
#                         transaction_amount=Decimal(transaction_amount),
#                         transaction_subtype_2=transaction_subtype_2,
#                     )

#                     if existing_transaction.exists():
#                         failed_records.append({
#                             'Reason': 'Similar transaction already exists',
#                             'Customer_ID': transaction_producer,
#                             'Transaction_Shift': transaction_shift,
#                             'Transaction_Liters': transaction_liters,
#                             'Transaction_FAT': transaction_fat,
#                             'Transaction_SNF': transaction_snf,
#                             'Transaction_Amount': transaction_amount,
#                             'Date': date_str,
#                             'Time': time_str,
#                         })
#                         continue

#                     try:
#                         with transaction.atomic():
#                             transaction_obj = MilkTransaction.objects.create(
#                                 dairy=dairy,
#                                 end_user=end_user,
#                                 society_code=society_code,
#                                 center_code=center_code,
#                                 transaction_type=transaction_type,
#                                 transaction_subtype=transaction_subtype,
#                                 date=date,
#                                 time=time,
#                                 transaction_shift=transaction_shift,
#                                 transaction_producer=transaction_producer,
#                                 transaction_liters=Decimal(transaction_liters),
#                                 transaction_fat=Decimal(transaction_fat),
#                                 transaction_lacto=Decimal(transaction_lacto),
#                                 transaction_snf=Decimal(transaction_snf),
#                                 transaction_water=Decimal(transaction_water),
#                                 transaction_protein=Decimal(transaction_protein),
#                                 transaction_ph=Decimal(transaction_ph),
#                                 transaction_rate=Decimal(transaction_rate),
#                                 transaction_off_amount=Decimal(transaction_off_amount),
#                                 transaction_amount=Decimal(transaction_amount),
#                                 transaction_subtype_2=transaction_subtype_2,
#                             )
#                             success_records.append({
#                                 'Reason': 'Record Successfully Created',
#                                 'Customer_ID': transaction_producer,
#                                 'Transaction_Shift': transaction_shift,
#                                 'Transaction_Liters': transaction_liters,
#                                 'Transaction_FAT': transaction_fat,
#                                 'Transaction_SNF': transaction_snf,
#                                 'Transaction_Amount': transaction_amount,
#                                 'Date': date_str,
#                                 'Time': time_str,
#                             })

#                             bonus_obj=Bonus.objects.create(
#                                 user=end_user,
#                                 bonus_date=date,
#                                 bonus_time=time,
#                                 bonus_amount=Decimal(transaction_liters),
#                                 description="Record added from the import transaction",
#                                 transaction_type='bonus_added',
#                                 transaction_source='import'
#                             )
#                     except Exception as e:
#                         failed_records.append({
#                             'Reason': str(e),
#                             'Customer_ID': transaction_producer,
#                             'Transaction_Shift': transaction_shift,
#                             'Transaction_Liters': transaction_liters,
#                             'Transaction_FAT': transaction_fat,
#                             'Transaction_SNF': transaction_snf,
#                             'Transaction_Amount': transaction_amount,
#                             'Date': date_str,
#                             'Time': time_str,
#                         })

#             # Write success and failed records to CSV files
#             success_csv_data = 'Customer_ID,Transaction_Shift,Transaction_Liters,Transaction_FAT,Transaction_SNF,Transaction_Amount,Date,Time,Reason\n' + '\n'.join([f'"{record["Customer_ID"]}","{record["Transaction_Shift"]}","{record["Transaction_Liters"]}","{record["Transaction_FAT"]}","{record["Transaction_SNF"]}","{record["Transaction_Amount"]}","{record["Date"]}","{record["Time"]}","{record["Reason"]}"' for record in success_records])
#             failed_csv_data = 'Customer_ID,Transaction_Shift,Transaction_Liters,Transaction_FAT,Transaction_SNF,Transaction_Amount,Date,Time,Reason\n' + '\n'.join([f'"{record["Customer_ID"]}","{record["Transaction_Shift"]}","{record["Transaction_Liters"]}","{record["Transaction_FAT"]}","{record["Transaction_SNF"]}","{record["Transaction_Amount"]}","{record["Date"]}","{record["Time"]}","{record["Reason"]}"' for record in failed_records])


#              # Generate unique filenames based on current date and time
#             timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
#             success_filename = f'media/records/success_records_{timestamp}.csv'
#             failed_filename = f'media/records/failed_records_{timestamp}.csv'
#             # Save the CSV files
#             with open(success_filename, 'w') as success_file:
#                 success_file.write(success_csv_data)

#             with open(failed_filename, 'w') as failed_file:
#                 failed_file.write(failed_csv_data)

#             # Create and save an ImportTransaction instance
#             import_transaction = ImportTransaction.objects.create(
#                 dairy=dairy,
#                 imported_transaction_name=f'Import_{timestamp}',
#                 success_records=len(success_records),
#                 success_csv=success_filename,
#                 failed_records=len(failed_records),
#                 failed_csv=failed_filename
#             )

#             success_message = f'Transactions imported successfully. {len(success_records)} records imported.'
#             failed_message = f'{len(failed_records)} records failed to import.'
            
#             # Fetch the updated list of transactions
#             updated_transactions = list(ImportTransaction.objects.filter(dairy=request.user.dairy).order_by('id').values())
#             response_data = {
#                 'message': success_message,
#                 'failed_message': failed_message,
#                 'transactions': updated_transactions[-1]
#             }

#             return JsonResponse(response_data)

#     return render(request, 'milk_transaction/import_transactions_list.html')



@csrf_exempt
def import_transactions(request):
    if request.method == 'GET':
        transactions = ImportTransaction.objects.filter(dairy=request.user.dairy).order_by('-id').values()
        context = {
            'import_transactions': transactions
        }
        return render(request, 'milk_transaction/import_transactions_list.html', context)

    if request.method == 'POST':
        file = request.FILES.get('file')
        if file:
            try:
                lines = file.read().decode('utf-8').splitlines()
            except UnicodeDecodeError:
                return JsonResponse({'error': 'Invalid file encoding.'}, status=400)

            success_records = []
            failed_records = []

            for line in lines:
                fields = line.strip().split(',')
                if len(fields) != 20:
                    failed_records.append({
                        'Reason': 'Invalid number of fields',
                        'Line': fields
                    })
                    continue

                try:
                    society_code, center_code, transaction_type, transaction_subtype, date_str, time_str, transaction_shift, transaction_producer, transaction_liters, transaction_fat, transaction_lacto, transaction_snf, transaction_water, transaction_protein, transaction_ph, transaction_rate, transaction_off_amount, transaction_amount, transaction_subtype_2, extra_data = fields

                    transaction_liters = transaction_liters.replace('*', '')
                    transaction_fat = transaction_fat.replace('*', '')
                    transaction_lacto = transaction_lacto.replace('*', '')
                    transaction_snf = transaction_snf.replace('*', '')

                    date = datetime.strptime(date_str, '%d/%m/%y').date()
                    time = datetime.strptime(time_str, '%H:%M').time()
                except ValueError as e:
                    failed_records.append({
                        'Reason': e.args,
                        'Line': fields
                    })
                    continue

                try:
                    end_user = EndUser.objects.get(dairy_name=request.user.dairy.id, custom_id=int(transaction_producer))
                    dairy = request.user.dairy
                except EndUser.DoesNotExist:
                    failed_records.append({
                        'Reason': f"Customer with customer_id {transaction_producer} not found",
                        'Line': fields
                    })
                    continue

                existing_transaction = MilkTransaction.objects.filter(
                    dairy=dairy,
                    end_user=end_user,
                    # society_code=society_code,
                    center_code=center_code,
                    transaction_type=transaction_type,
                    transaction_subtype=transaction_subtype,
                    date=date,
                    time=time,
                    transaction_shift=transaction_shift,
                    transaction_producer=transaction_producer,
                    transaction_liters=Decimal(transaction_liters),
                    transaction_fat=Decimal(transaction_fat),
                    transaction_lacto=Decimal(transaction_lacto),
                    transaction_snf=Decimal(transaction_snf),
                    transaction_water=Decimal(transaction_water),
                    transaction_protein=Decimal(transaction_protein),
                    transaction_ph=Decimal(transaction_ph),
                    transaction_rate=Decimal(transaction_rate),
                    transaction_off_amount=Decimal(transaction_off_amount),
                    transaction_amount=Decimal(transaction_amount),
                    transaction_subtype_2=transaction_subtype_2,
                )

                if existing_transaction.exists():
                    failed_records.append({
                        'Reason': 'Similar transaction already exists',
                        'Line': fields
                    })
                    continue

                try:
                    with transaction.atomic():
                        transaction_obj = MilkTransaction.objects.create(
                            dairy=dairy,
                            end_user=end_user,
                            society_code=society_code,
                            center_code=center_code,
                            transaction_type=transaction_type,
                            transaction_subtype=transaction_subtype,
                            date=date,
                            time=time,
                            transaction_shift=transaction_shift,
                            transaction_producer=transaction_producer,
                            transaction_liters=Decimal(transaction_liters),
                            transaction_fat=Decimal(transaction_fat),
                            transaction_lacto=Decimal(transaction_lacto),
                            transaction_snf=Decimal(transaction_snf),
                            transaction_water=Decimal(transaction_water),
                            transaction_protein=Decimal(transaction_protein),
                            transaction_ph=Decimal(transaction_ph),
                            transaction_rate=Decimal(transaction_rate),
                            transaction_off_amount=Decimal(transaction_off_amount),
                            transaction_amount=Decimal(transaction_amount),
                            transaction_subtype_2=transaction_subtype_2,
                        )
                        success_records.append({
                            'Reason': 'Record Successfully Created',
                            'Line': fields
                        })

                        bonus_obj = Bonus.objects.create(
                            user=end_user,
                            bonus_date=date,
                            bonus_time=time,
                            bonus_amount=Decimal(transaction_liters),
                            description="Record added from the import transaction",
                            transaction_type='bonus_added',
                            transaction_source='import',
                            milk_transaction=transaction_obj,
                        )
                except Exception as e:
                    failed_records.append({
                        'Reason': str(e),
                        'Line': fields
                    })

            # Generate unique filenames based on current date and time
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            success_filename = f'media/records/success_records_{timestamp}.csv'
            failed_filename = f'media/records/failed_records_{timestamp}.csv'

            # Write success and failed records to CSV files
            def write_csv(filename, records):
                fieldnames = ['Customer_ID', 'Customer_Name', 'Transaction_Shift', 'Transaction_Liters', 'Transaction_FAT',
                            'Transaction_SNF', 'Transaction_Rate', 'Transaction_Amount', 'Date', 'Time', 'Reason']
                
                with open(filename, 'w', newline='') as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    writer.writeheader()
                    for record in records:
                        
                        # Get the 'Line' list from the record, or use an empty list if it doesn't exist
                        line_data = record.get('Line', [])
                        try:
                            custom_id = line_data[7] if len(line_data) > 7 else '0'
                            # print('user id',custom_id)
                            end_user_obj = EndUser.objects.get(custom_id=custom_id)
                            customer_name = f"{end_user_obj.first_name} {end_user_obj.last_name}"
                        except EndUser.DoesNotExist:
                            customer_name = 'Customer Not exist'
                        
                        # Define a dictionary with default values as empty strings
                        data = {
                            'Customer_ID': line_data[7] if len(line_data) > 7 else '',
                            'Customer_Name':customer_name,
                            'Transaction_Shift': line_data[6] if len(line_data) > 6 else '',
                            'Transaction_Liters': line_data[8] if len(line_data) > 8 else '',
                            'Transaction_FAT': line_data[9] if len(line_data) > 9 else '',
                            'Transaction_SNF': line_data[11] if len(line_data) > 11 else '',
                            'Transaction_Rate': line_data[15] if len(line_data) > 15 else '',
                            'Transaction_Amount': line_data[17] if len(line_data) > 17 else '',
                            'Date': line_data[4] if len(line_data) > 4 else '',
                            'Time': line_data[5] if len(line_data) > 5 else '',
                            'Reason': record.get('Reason', ''),
                        }
                        
                        writer.writerow(data)


            write_csv(success_filename, success_records)
            write_csv(failed_filename, failed_records)

            # Create and save an ImportTransaction instance
            import_transaction = ImportTransaction.objects.create(
                dairy=request.user.dairy,
                imported_transaction_name=f'Import_{timestamp}',
                success_records=len(success_records),
                success_csv=success_filename,
                failed_records=len(failed_records),
                failed_csv=failed_filename
            )

            success_message = f'Transactions imported successfully. {len(success_records)} records imported.'
            failed_message = f'{len(failed_records)} records failed to import.'

            # Fetch the updated list of transactions
            updated_transactions = list(ImportTransaction.objects.filter(dairy=request.user.dairy).order_by('id').values())
            response_data = {
                'message': success_message,
                'failed_message': failed_message,
                'transactions': updated_transactions[-1]
            }

            return JsonResponse(response_data)

    return render(request, 'milk_transaction/import_transactions_list.html')


from django.views.generic import ListView
from django.db.models import Avg
from .models import MilkTransaction
from bill_management.models import GeneratedCycle

class WorstUsersPerCycleView(ListView):
    template_name = 'milk_transaction/worst_users.html'
    context_object_name = 'worst_users_data'

    def get_queryset(self):
        # Initialize an empty list to hold cycle data
        worst_users_data = []

        # Fetch all active cycles, ordered by created_at in descending order
        cycles = GeneratedCycle.objects.filter(is_deleted=False).order_by('-created_at')

        for cycle in cycles:
            # Filter transactions within the date range for each cycle
            transactions = MilkTransaction.objects.filter(
                date__gte=cycle.from_date,
                date__lte=cycle.to_date,
                dairy=cycle.dairy_name
            )

            # Calculate the average fat and SNF for each user in the cycle
            user_averages = transactions.values(
                'end_user__custom_id',
                'end_user__first_name',
                'end_user__last_name'
            ).annotate(
                avg_fat=Avg('transaction_fat'),
                avg_snf=Avg('transaction_snf')
            )

            # Get the worst three users by avg_fat and avg_snf
            worst_users = user_averages.order_by('avg_fat', 'avg_snf')[:3]

            # Append the cycle and its worst users to the data list
            worst_users_data.append({
                'cycle': cycle,
                'worst_users': worst_users
            })

        return worst_users_data
