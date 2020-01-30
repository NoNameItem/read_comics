from allauth.account.adapter import get_adapter
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import DetailView, RedirectView, UpdateView, ListView
import django_magnificent_messages as dmm

from users.forms import UserInfoForm
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


class UserSendEmailConfirmationView(LoginRequiredMixin, RedirectView):
    def get(self, request, *args, **kwargs):
        email = request.user.emailaddress_set.get(primary=True)
        if not email.verified:
            email.send_confirmation(request)
            get_adapter(self.request).add_message(
                self.request,
                messages.INFO,
                'account/messages/'
                'email_confirmation_sent.txt',
                {'email': email})
        return super(UserSendEmailConfirmationView, self).get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return self.request.GET.get("next", reverse_lazy("home"))


user_send_email_confirmation_view = UserSendEmailConfirmationView.as_view()


class UserEditView(BreadcrumbMixin, LoginRequiredMixin, UpdateView):
    model = User
    breadcrumb = [{'url': reverse_lazy("users:edit"), 'text': 'Edit profile'}]
    context_object_name = "user"
    form_class = UserInfoForm

    def get_success_url(self):
        return reverse_lazy("users:edit")

    def get_object(self, queryset=None):
        return User.objects.get(username=self.request.user.username)

    def form_valid(self, form):
        dmm.notifications.success(self.request, "Info successfully updated")
        email = self.request.user.emailaddress_set.get(primary=True)
        if form.cleaned_data["email"] != email.email:
            email.change(self.request, form.cleaned_data["email"])
            get_adapter(self.request).add_message(
                self.request,
                messages.INFO,
                'account/messages/'
                'email_confirmation_sent.txt',
                {'email': email})
        return super().form_valid(form)

    def form_invalid(self, form):
        dmm.notifications.error(self.request, "Please check entered data", "Error while saving info")
        return super(UserEditView, self).form_invalid(form)


user_edit_view = UserEditView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()


class UserChangePhotoView(LoginRequiredMixin, View):
    def post(self, request):
        user = request.user
        user.user_image = request.FILES['file']
        user.save()
        return JsonResponse(data={"image_url": user.image_url})


user_change_photo_view = UserChangePhotoView.as_view()


class UserDeletePhotoView(LoginRequiredMixin, View):
    def post(self, request):
        user = request.user
        user.user_image = None
        user.save()
        return JsonResponse(data={"image_url": user.image_url})


user_delete_photo_view = UserDeletePhotoView.as_view()
