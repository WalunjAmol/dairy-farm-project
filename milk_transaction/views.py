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
from decimal import Decimal
import csv

#Local Import
from .models import EndUser, MilkTransaction, ImportTransaction,Dairy
from  bonus_app.models import Bonus
from .forms import MilkTransactionForm

@method_decorator(login_required, name='dispatch')
class MilkTransactionListView(ListView):
    model = MilkTransaction
    template_name = 'milk_transaction/transaction_list.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        user = self.request.user
        queryset = MilkTransaction.objects.filter(end_user__dairy_name__role=user.dairy.role)
        return queryset


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
            form.save()
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
        form = MilkTransactionForm(instance = self.model.objects.filter(id=kwargs['pk']).last(),user=request.user)
        return render(request, self.template_name, {'form':form})
    
    def post(self, request, *args, **kwargs):
        data = request.POST
        form = MilkTransactionForm(data=data,user=request.user)

        if not form.is_valid():
            return render(request, self.template_name, {'form':form})

        if form.is_valid():
            form.save()
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
                            transaction_source='import'
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
                            custom_id = line_data[7] if len(line_data) > 7 else 1
                            print('user id',custom_id)
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


