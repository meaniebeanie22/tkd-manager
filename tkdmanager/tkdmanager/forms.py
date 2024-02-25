from allauth.mfa.forms import AuthenticateForm


class CustomAuthenticateForm(AuthenticateForm):
    def __init__(self, *args, **kwargs):
        super(CustomAuthenticateForm, self).__init__(*args, **kwargs)
        self.fields["code"].widget.attrs.update({"autofocus": ""})
