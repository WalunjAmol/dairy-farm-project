from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import auth
from django.contrib.auth.mixins import LoginRequiredMixin


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

class DashboardView(LoginRequiredMixin,TemplateView):
    template_name='dairy_owner_dashboard/content.html'
    login_url= '/dairy-management/login/'
    redirect_field_name = 'redirect_to'