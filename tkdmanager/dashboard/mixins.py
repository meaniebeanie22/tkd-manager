from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse
from django.http import HttpResponseRedirect
from .decorators import req_user_is_mfa


class MFARequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return req_user_is_mfa(self.request)

    def handle_no_permission(self) -> HttpResponseRedirect:
        print(
            f"Failed MFA, request: {self.request}\nSession: {self.request.session.items()}"
        )
        return HttpResponseRedirect(reverse("mfa_authenticate"))
