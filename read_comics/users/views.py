from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, RedirectView, UpdateView, ListView
from django.utils.translation import ugettext_lazy as _
from django_magnificent_messages import notifications, INFO

from utils.view_mixins import BreadcrumbMixin

User = get_user_model()


class UserListView(BreadcrumbMixin, ListView):
    model = User


class UserDetailView(BreadcrumbMixin, DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"
    context_object_name = "user"
    template_name = "users/user_detail.html"

    def get_breadcrumb(self):
        user = self.get_object()
        return [
            {'url': "#", 'text': "Users"},
            {'url': reverse_lazy("users:detail", args=(user.username,)), 'text': str(user)}
        ]


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, UpdateView):

    model = User
    fields = ["name"]

    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})

    def get_object(self, queryset=None):
        return User.objects.get(username=self.request.user.username)

    def form_valid(self, form):
        notifications.add(
            self.request, INFO, _("Infos successfully updated")
        )
        return super().form_valid(form)


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()
