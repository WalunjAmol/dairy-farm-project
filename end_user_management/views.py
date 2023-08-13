from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import EndUser
from .forms import EndUserForm

class EndUserListView(ListView):
    model = EndUser
    template_name = 'enduser_list.html'
    context_object_name = 'users'

class EndUserCreateView(CreateView):
    model = EndUser
    form_class = EndUserForm
    template_name = 'end_user_management/enduser_create.html'
    success_url = reverse_lazy('end_user_management:user-list')


    def form_valid(self, form):
        form.instance.dairy_owner = self.request.user
        form.instance.dairy_name = self.request.user.dairy
        messages.success(self.request, 'User created successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class EndUserUpdateView(UpdateView):
    model = EndUser
    form_class = EndUserForm
    template_name = 'end_user_management/enduser_update.html'
    success_url = reverse_lazy('end_user_management:user-list')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(dairy_owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'User updated successfully.')
        return super().form_valid(form)

class EndUserDeleteView(DeleteView):
    model = EndUser
    template_name = 'enduser_confirm_delete.html'
    success_url = reverse_lazy('end_user_management:enduser-list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'User deleted successfully.')
        return super().delete(request, *args, **kwargs)
