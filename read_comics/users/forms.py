import allauth.account.forms
from crispy_forms.layout import Field, Layout, Div, HTML
from django.contrib.auth import get_user_model, forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from utils.form_helpers import DefaultFormHelper

User = get_user_model()


class UserChangeForm(forms.UserChangeForm):
    class Meta(forms.UserChangeForm.Meta):
        model = User


class UserCreationForm(forms.UserCreationForm):
    error_message = forms.UserCreationForm.error_messages.update(
        {"duplicate_username": _("This username has already been taken.")}
    )

    class Meta(forms.UserCreationForm.Meta):
        model = User

    def clean_username(self):
        username = self.cleaned_data["username"]

        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username

        raise ValidationError(self.error_messages["duplicate_username"])


class LoginForm(allauth.account.forms.LoginForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        self.fields["login"].widget.attrs.update({
            "data-validation-required-message": "This field is required"
        })
        self.fields["login"].widget.attrs.pop("autofocus")
        self.fields["password"].widget.attrs.update({
            "data-validation-required-message": "This field is required"
        })
        self.fields["remember"].label = _("<small>Remember Me</small>")

        self.helper = DefaultFormHelper()
        self.helper.attrs = {"novalidate": "novalidate"}

        self.helper.layout = Layout(
            Field("login", wrapper_class="mb-50"),
            Field("password"),
            Div(
                Div(
                    Field("remember", wrapper_class="checkbox-sm"),
                    css_class="text-left"
                ),
                HTML(
                    """<div class="text-right">
                        <a href="{% url "account_reset_password" %}" class="card-link">
                            <small>Forgot Password?</small>
                        </a>
                    </div>"""),
                css_class="form-group d-flex flex-md-row flex-column justify-content-between align-items-center"
            ),
            HTML("""<button type="submit" class="btn btn-primary glow w-100 position-relative">
                    Login<i id="icon-arrow" class="bx bx-right-arrow-alt"></i>
                    </button>""")
        )


class ResetPasswordForm(allauth.account.forms.ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(ResetPasswordForm, self).__init__(*args, **kwargs)

        self.fields["email"].widget.attrs.update({
            "data-validation-required-message": "This field is required"
        })

        self.helper = DefaultFormHelper()
        self.helper.attrs = {"novalidate": "novalidate"}
        self.helper.form_class = "mb-2"

        self.helper.layout = Layout(
            Field("email", wrapper_class="mb-2"),
            HTML("""
            <button type="submit" class="btn btn-primary glow position-relative w-100">
            RESET PASSWORD<i id="icon-arrow" class="bx bx-right-arrow-alt"></i>
            </button>
            """)
        )


class ResetPasswordKeyForm(allauth.account.forms.ResetPasswordKeyForm):
    def __init__(self, *args, **kwargs):
        super(ResetPasswordKeyForm, self).__init__(*args, **kwargs)

        self.helper = DefaultFormHelper()
        self.helper.attrs = {"novalidate": "novalidate"}
        self.helper.form_class = "mb-2"

        self.helper.layout = Layout(
            Field("password1"),
            Field("password2", wrapper_class="mb-2"),
            HTML("""
            <button type="submit" class="btn btn-primary glow position-relative w-100">
            Reset my password<i id="icon-arrow" class="bx bx-right-arrow-alt"></i>
            </button>
            """)
        )


class SignupForm(allauth.account.forms.SignupForm):
    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)

        self.helper = DefaultFormHelper()
        self.helper.attrs = {"novalidate": "novalidate"}

        self.fields["username"].widget.attrs.pop("autofocus")

        self.helper.layout = Layout(
            Field("username", wrapper_class="mb-50"),
            Field("email", wrapper_class="mb-50"),
            Field("password1", wrapper_class="mb-50"),
            Field("password2", wrapper_class="mb-2"),
            HTML("""
            <button type="submit" class="btn btn-primary glow position-relative w-100">
            SIGN UP<i id="icon-arrow" class="bx bx-right-arrow-alt"></i>
            </button>
            """)
        )
