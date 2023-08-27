from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.http import JsonResponse

from datetime import datetime
from decimal import Decimal

#Local Import
from .models import EndUser, MilkTransaction, ImportTransaction
from .forms import MilkTransactionForm


class MilkTransactionListView(ListView):
    model = MilkTransaction
    template_name = 'milk_transaction/transaction_list.html'
    context_object_name = 'transactions'

class MilkTransactionCreateView(CreateView):
    model = MilkTransaction
    form_class = MilkTransactionForm
    template_name = 'milk_transaction/transaction_create.html'
    success_url = reverse_lazy('milk_transaction:milk-transaction-list')

    def form_valid(self, form):
        messages.success(self.request, 'Record Created Successfully.')
        return super().form_valid(form)

class MilkTransactionUpdateView(UpdateView):
    model = MilkTransaction
    form_class = MilkTransactionForm
    template_name = 'milk_transaction/transaction_update.html'
    success_url = reverse_lazy('milk_transaction:milk-transaction-list')

    def form_valid(self, form):
        messages.success(self.request, 'Record Updated Successfully.')
        return super().form_valid(form)

class MilkTransactionDeleteView(DeleteView):
    model = MilkTransaction
    template_name = 'milktransaction_confirm_delete.html'
    success_url = reverse_lazy('milk_transaction:milk-transaction-list')


@csrf_exempt
def import_transactions(request):
    if request.method == 'GET':
        transactions = ImportTransaction.objects.all().order_by('-id').values()

        context = {
            'import_transactions': transactions
        }
        return render(request, 'milk_transaction/import_transactions_list.html', context)

        
    if request.method == 'POST':
        file = request.FILES.get('file')
        if file:
            # Process the uploaded file
            lines_byte = file.readlines()
            lines = lines_byte[0].decode('utf-8').split('\r')

            success_records = []
            failed_records = []

            for line in lines:
                fields = line.strip().split(',')
                if len(fields) == 20:
                    society_code, center_code, transaction_type, transaction_subtype, date_str, time_str, transaction_shift, transaction_producer, transaction_liters, transaction_fat, transaction_lacto, transaction_snf, transaction_water, transaction_protein, transaction_ph, transaction_rate, transaction_off_amount, transaction_amount, transaction_subtype_2, extra_data = fields

                    date = datetime.strptime(date_str, '%d/%m/%y').date()
                    time = datetime.strptime(time_str, '%H:%M').time()

                    try:
                        end_user = EndUser.objects.get(custom_id=int(transaction_producer))
                    except EndUser.DoesNotExist:
                        failed_records.append({
                            'Reason': f"Customer with customer_id {transaction_producer} not found",
                            'Customer_ID': transaction_producer,
                            'Transaction_Shift': transaction_shift,
                            'Transaction_Liters': transaction_liters,
                            'Transaction_FAT': transaction_fat,
                            'Transaction_SNF': transaction_snf,
                            'Transaction_Amount': transaction_amount,
                            'Date': date_str,
                            'Time': time_str,
                        })
                        continue

                    # Check if a similar transaction already exists
                    existing_transaction = MilkTransaction.objects.filter(
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
                            'Customer_ID': transaction_producer,
                            'Transaction_Shift': transaction_shift,
                            'Transaction_Liters': transaction_liters,
                            'Transaction_FAT': transaction_fat,
                            'Transaction_SNF': transaction_snf,
                            'Transaction_Amount': transaction_amount,
                            'Date': date_str,
                            'Time': time_str,
                        })
                        continue

                    try:
                        with transaction.atomic():
                            transaction_obj = MilkTransaction.objects.create(
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
                                'Customer_ID': transaction_producer,
                                'Transaction_Shift': transaction_shift,
                                'Transaction_Liters': transaction_liters,
                                'Transaction_FAT': transaction_fat,
                                'Transaction_SNF': transaction_snf,
                                'Transaction_Amount': transaction_amount,
                                'Date': date_str,
                                'Time': time_str,
                            })
                    except Exception as e:
                        failed_records.append({
                            'Reason': str(e),
                            'Customer_ID': transaction_producer,
                            'Transaction_Shift': transaction_shift,
                            'Transaction_Liters': transaction_liters,
                            'Transaction_FAT': transaction_fat,
                            'Transaction_SNF': transaction_snf,
                            'Transaction_Amount': transaction_amount,
                            'Date': date_str,
                            'Time': time_str,
                        })

            # Write success and failed records to CSV files
            success_csv_data = 'Customer_ID,Transaction_Shift,Transaction_Liters,Transaction_FAT,Transaction_SNF,Transaction_Amount,Date,Time,Reason\n' + '\n'.join([f'"{record["Customer_ID"]}","{record["Transaction_Shift"]}","{record["Transaction_Liters"]}","{record["Transaction_FAT"]}","{record["Transaction_SNF"]}","{record["Transaction_Amount"]}","{record["Date"]}","{record["Time"]}","{record["Reason"]}"' for record in success_records])
            failed_csv_data = 'Customer_ID,Transaction_Shift,Transaction_Liters,Transaction_FAT,Transaction_SNF,Transaction_Amount,Date,Time,Reason\n' + '\n'.join([f'"{record["Customer_ID"]}","{record["Transaction_Shift"]}","{record["Transaction_Liters"]}","{record["Transaction_FAT"]}","{record["Transaction_SNF"]}","{record["Transaction_Amount"]}","{record["Date"]}","{record["Time"]}","{record["Reason"]}"' for record in failed_records])


             # Generate unique filenames based on current date and time
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            success_filename = f'media/records/success_records_{timestamp}.csv'
            failed_filename = f'media/records/failed_records_{timestamp}.csv'
            # Save the CSV files
            with open(success_filename, 'w') as success_file:
                success_file.write(success_csv_data)

            with open(failed_filename, 'w') as failed_file:
                failed_file.write(failed_csv_data)

            # Create and save an ImportTransaction instance
            import_transaction = ImportTransaction.objects.create(
                imported_transaction_name=f'Import_{timestamp}',
                success_records=len(success_records),
                success_csv=success_filename,
                failed_records=len(failed_records),
                failed_csv=failed_filename
            )

            success_message = f'Transactions imported successfully. {len(success_records)} records imported.'
            failed_message = f'{len(failed_records)} records failed to import.'
            
            # Fetch the updated list of transactions
            updated_transactions = list(ImportTransaction.objects.all().order_by('id').values())
            response_data = {
                'message': success_message,
                'failed_message': failed_message,
                'transactions': updated_transactions[-1]
            }

            return JsonResponse(response_data)

    return render(request, 'milk_transaction/import_transactions_list.html')

