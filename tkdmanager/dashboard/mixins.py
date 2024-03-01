from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.sessions.models import Session

def user_is_mfa(userobj):
    try:
        user = userobj.pk
        # test if anon
        if user == None:
            return False
        # get user session
        session = Session.objects.filter(_auth_user_id=userobj.pk).first()
        print(f'Session: {session.items()}')
        for method in session['account_authentication_methods']:
            if method['method'] == 'mfa':
                return True
            else:
                return False
            
    except Exception as error:
        print(f"Error in user_is_mfa: {error}")
        return False


class MFARequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return user_is_mfa(self.request.user)

    def handle_no_permission(self) -> HttpResponseRedirect:
        return HttpResponseRedirect(reverse("mfa_activate_totp"))
