from django.urls import path
from . import auth_views

urlpatterns = [
    path("/signup/admin", auth_views.BasicSignUpView.as_view(), name="basic_signup"),
    path("/signup/app", auth_views.AppSignUpView.as_view(), name="app_signup"),
    path(
        "/login/admin", auth_views.BasicSignInView.as_view(), name="basic_admin_login"
    ),
    path("/login/app", auth_views.AppSignInView.as_view(), name="app_login"),
    path("/leave", auth_views.SecessionView.as_view(), name="basic_leave"),
]

urlpatterns += [
    path("/token/refresh", auth_views.TokenRefreshView.as_view(), name="token_refresh"),
]

urlpatterns += [
    path(
        "/check-email",
        auth_views.CheckDuplicateUsernameView.as_view(),
        name="check_email",
    ),
    path(
        "/email-verification",
        auth_views.EmailVerification.as_view(),
        name="verify_email",
    ),
    path(
        "/email-confirmation", auth_views.EmailConfirmation.as_view(), name="activate"
    ),
    path(
        "/password-change",
        auth_views.PasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "/password-reset", auth_views.PasswordResetView.as_view(), name="password_reset"
    ),
]
