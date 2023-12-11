#Django Imports
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

#Internal Imports
from .models import EndUser
from .forms import EndUserForm
@method_decorator(login_required, name='dispatch')
class EndUserListView(ListView):
    model = EndUser
    template_name = 'end_user_management/enduser_list.html'
    context_object_name = 'users'
    ordering = ['custom_id']

    def get_queryset(self):
        user_dairy_role = self.request.user.dairy.role
        if self.request.user.is_superuser:
            queryset = self.model.objects.filter(dairy_name__role=user_dairy_role)
        else:
            queryset = self.model.objects.filter(dairy_name__role=user_dairy_role)

        # Apply ordering here
        queryset = queryset.order_by(*self.ordering)

        return queryset


@method_decorator(login_required, name='dispatch')
class EndUserCreateView(CreateView):
    model = EndUser
    form_class = EndUserForm
    template_name = 'end_user_management/enduser_create.html'
    success_url = reverse_lazy('end_user_management:user-list')

    def form_valid(self, form):
        custom_id = form.cleaned_data['custom_id']
        existing_users_with_same_id = EndUser.objects.filter(dairy_name=self.request.user.dairy, custom_id=custom_id)
        if existing_users_with_same_id:
            form.add_error('custom_id', "A user with this custom ID already exists within this dairy.")
            return self.form_invalid(form) 

        form.instance.dairy_owner = self.request.user
        form.instance.dairy_name = self.request.user.dairy
        messages.success(self.request, 'User created successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

@method_decorator(login_required, name='dispatch')
class EndUserUpdateView(UpdateView):
    model = EndUser
    form_class = EndUserForm
    template_name = 'end_user_management/enduser_update.html'
    success_url = reverse_lazy('end_user_management:user-list')

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            return queryset.filter(dairy_owner=self.request.user)
        else:
            return queryset.filter(dairy_owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'User updated successfully.')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class EndUserDeleteView(DeleteView):
    model = EndUser
    template_name = 'enduser_confirm_delete.html'
    success_url = reverse_lazy('end_user_management:enduser-list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'User deleted successfully.')
        return super().delete(request, *args, **kwargs)
