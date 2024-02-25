from allauth.mfa.models import Authenticator
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse
from django.http import HttpResponseRedirect


def user_is_mfa(userobj):
    try:
        user = userobj.pk
        # test if anon
        if user == None:
            return False
        has_mfa = Authenticator.objects.filter(user__pk=user).exists()
        return has_mfa
    except Exception as error:
        print(f"Error in user_is_mfa: {error}")
        return False


class MFARequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return user_is_mfa(self.request.user)

    def handle_no_permission(self) -> HttpResponseRedirect:
        return HttpResponseRedirect(reverse("mfa_activate_totp"))
