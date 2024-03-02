from allauth.mfa.forms import AuthenticateForm, ActivateTOTPForm, DeactivateTOTPForm
from allauth.account.forms import (
    LoginForm,
    SignupForm,
    AddEmailForm,
    ChangePasswordForm,
    SetPasswordForm,
    ResetPasswordForm,
    ResetPasswordKeyForm,
)
from django.forms.widgets import CheckboxInput


class BSMixin:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if isinstance(visible.field.widget, CheckboxInput):
                visible.field.widget.attrs["class"] = "form-check-input"
            else:
                visible.field.widget.attrs["class"] = "form-control"


class CustomAuthenticateForm(BSMixin, AuthenticateForm):
    def __init__(self, *args, **kwargs):
        super(CustomAuthenticateForm, self).__init__(*args, **kwargs)
        self.fields["code"].widget.attrs.update(
            {
                "autofocus": "",
                "inputmode": "numeric",
                "pattern": "[0-9]*",
                "autocomplete": "one-time-code",
            }
        )


class CustomLoginForm(BSMixin, LoginForm):
    pass


class CustomSignupForm(BSMixin, SignupForm):
    pass


class CustomAddEmailForm(BSMixin, AddEmailForm):
    pass


class CustomChangePasswordForm(BSMixin, ChangePasswordForm):
    pass


class CustomSetPasswordForm(BSMixin, SetPasswordForm):
    pass


class CustomResetPasswordForm(BSMixin, ResetPasswordForm):
    pass


class CustomResetPasswordKeyForm(BSMixin, ResetPasswordKeyForm):
    pass


class CustomActivateTOTPForm(BSMixin, ActivateTOTPForm):
    pass


class CustomDeactivateTOTPForm(BSMixin, DeactivateTOTPForm):
    pass
