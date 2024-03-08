from functools import wraps
from urllib.parse import urlparse
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import resolve_url
from django.urls import reverse


def req_user_is_mfa(request):
    try:
        session = request.session
        if session:
            for method in session.get("account_authentication_methods", []):
                if method.get("method") == "mfa":
                    return True
            print(f"MFA check session: ")
        return False

    except Exception as error:
        print(f"Error in req_user_is_mfa: {error}")
        return False


def request_decorator(
    test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME
):
    """
    Decorator for views that checks that the request passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the request object and returns True if the request passes.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapper_view(request, *args, **kwargs):
            if test_func(request):
                return view_func(request, *args, **kwargs)
            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if (not login_scheme or login_scheme == current_scheme) and (
                not login_netloc or login_netloc == current_netloc
            ):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login

            return redirect_to_login(path, resolved_login_url, redirect_field_name)

        return _wrapper_view

    return decorator


def mfa_required(function=None, login_url=reverse("mfa_authenticate")):
    actual_decorator = request_decorator(
        lambda r: req_user_is_mfa(r),
        login_url=login_url,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
