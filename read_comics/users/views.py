import allauth.account.signals
from allauth.account.adapter import get_adapter
from allauth.account.utils import logout_on_password_change
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import DetailView, RedirectView, UpdateView, ListView
import django_magnificent_messages as dmm

from users.forms import UserInfoForm, ChangePasswordForm
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
    info_form_class = UserInfoForm
    password_form_class = ChangePasswordForm

    def get_form(self, form_class=None):
        kwargs = self.get_form_kwargs()
        if 'info' in self.request.POST:
            return self.info_form_class(**kwargs)
        elif 'password' in self.request.POST:
            user = kwargs.pop('instance')
            kwargs['user'] = user
            return self.password_form_class(**kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserEditView, self).get_context_data(**kwargs)
        if not context.get('info_form'):
            context['info_form'] = self.info_form_class(instance=self.get_object())
        if not context.get('password_form'):
            context['password_form'] = self.password_form_class()
        show_tab = self.request.GET.get("show_tab")
        if show_tab:
            context['show_tab'] = show_tab
        return context

    def get_success_url(self):
        return reverse_lazy("users:edit")

    def get_object(self, queryset=None):
        return User.objects.get(username=self.request.user.username)

    def form_valid(self, form):
        if 'info' in self.request.POST:
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
        elif 'password' in self.request.POST:
            form.save()
            logout_on_password_change(self.request, form.user)
            get_adapter(self.request).add_message(
                self.request,
                messages.SUCCESS,
                'account/messages/password_set.txt')
            allauth.account.signals.password_set.send(sender=self.request.user.__class__,
                                                      request=self.request, user=self.request.user)
            return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        context = {}
        if 'info' in self.request.POST:
            dmm.notifications.error(self.request, "Please check entered data", "Can't save info")
            context = {'info_form': form, 'show_tab': 'info'}
        elif 'password' in self.request.POST:
            dmm.notifications.error(self.request, "Please check entered data", "Can't change password")
            context = {'password_form': form, 'show_tab': 'password'}
        return self.render_to_response(self.get_context_data(**context))


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
