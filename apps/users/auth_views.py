from typing import Any

from django.contrib.auth.models import update_last_login
from django.core.signing import Signer
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from datetime import datetime
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed, NotFound, ValidationError
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from config.settings import base as settings
from config.exceptions import (
    DuplicateInstance,
    UnprocessableException,
    ConflictException,
)
from config.renderer import CustomRenderer
from .models import User
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.hashers import check_password
from django.core.mail import EmailMessage

from .refresh_token_auth import RefreshTokenAuthentication
from .serializers import UserSerializer
from .services import UserService


class BasicSignUpView(APIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="어드민 유저 웹사이트 회원가입",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=[
                "email",
                "name",
                "password",
                "confirm_password",
            ],
            properties={
                "email": openapi.Schema(
                    type=openapi.FORMAT_EMAIL, description="가입하려는 이메일"
                ),
                "name": openapi.Schema(type=openapi.TYPE_STRING, description="이름"),
                "password": openapi.Schema(type=openapi.FORMAT_PASSWORD),
            },
        ),
        responses={
            201: openapi.Response("user", UserSerializer),
            400: "validate and confirm email first",
        },
    )
    def post(self, request, *args, **kwargs):
        # Check if email confirmation is completed
        is_confirmed = request.COOKIES.get("email_confirmation")
        if not is_confirmed:
            raise UnprocessableException("validate and confirm email first")

        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")

        if password != confirm_password:
            raise ValidationError("Passwords doesn't match")

        # check duplicate email
        try:
            existing_user = get_object_or_404(
                User, email=request.data.get("email"), role=User.UserType.ADMIN
            )
            raise DuplicateInstance("user with the provided email already exists")
        except Http404:
            data = request.data
            data["role"] = User.UserType.ADMIN.value
            serializer = UserSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)


class BasicSignInView(APIView):
    serializer = UserSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="어드민 유저 웹사이트 로그인",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.FORMAT_EMAIL),
                "password": openapi.Schema(type=openapi.FORMAT_PASSWORD),
            },
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "access_token": openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            user = get_object_or_404(User, email=email)
        except Http404:
            raise AuthenticationFailed("No user by the provided email")

        if not check_password(password, user.password):
            raise AuthenticationFailed("Incorrect password")

        update_last_login(None, user)
        serializer = UserSerializer(user)
        access_token, refresh_token = UserService.generate_tokens(user)

        data = serializer.data
        data["access_token"] = access_token

        res = Response(
            data,
            status=status.HTTP_200_OK,
        )

        res.set_cookie(
            settings.SIMPLE_JWT["AUTH_COOKIE"],
            refresh_token,
            max_age=settings.SIMPLE_JWT["AUTH_COOKIE_EXPIRES"],
        )  # 7 days
        return res


class SecessionView(APIView):
    serializer = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="계정 탈퇴",
        responses={200: openapi.Response("user", UserSerializer)},
    )
    def post(self, request, *args, **kwargs):
        service = UserService(request.user)
        user = service.deactivate_user()
        serializer = UserSerializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CheckDuplicateUsernameView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="중복 이메일이 존재하는지 확인합니다",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"email": openapi.Schema(type=openapi.FORMAT_EMAIL)},
        ),
        responses={
            200: openapi.Response(
                "ok",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "email": openapi.Schema(
                            type=openapi.TYPE_STRING, description="email"
                        ),
                    },
                ),
            ),
            409: "Provided email already exists",
        },
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")

        existing_email = User.objects.filter(email=email).first()
        if existing_email:
            raise DuplicateInstance("Provided email already exists")

        res = Response({"email": email}, status=status.HTTP_200_OK)
        res.set_cookie("email_duplication_check", "complete", max_age=3600)

        return res


class PasswordChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="어드민 유저 웹사이트 비밀번호 변경",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "current_password": openapi.Schema(type=openapi.FORMAT_PASSWORD),
                "new_password": openapi.Schema(type=openapi.FORMAT_PASSWORD),
            },
        ),
        responses={
            200: openapi.Response("Success", UserSerializer),
            401: "Password do not match",
        },
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        if current_password == new_password:
            raise ValidationError(
                "new password should be different from the old password"
            )

        if not check_password(current_password, user.password):
            raise AuthenticationFailed("Password do not match")

        user.set_password(new_password)
        user.updated_at = datetime.now()
        user.save(update_fields=["password", "updated_at"])

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="비밀번호를 초기화합니다. 랜덤한 문자열이 임시 비밀번호로 설정되며 이메일로 전송됩니다",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"email": openapi.Schema(type=openapi.FORMAT_EMAIL)},
        ),
        responses={
            404: "User with the provided email does not exist",
            500: "Failed to send email. Try again later.",
        },
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")

        try:
            user = get_object_or_404(User, email=email)
        except Http404:
            raise NotFound("User with the provided email does not exist")

        new_password = UserService.generate_random_code(3, 8)
        user.set_password(new_password)
        user.save(update_fields=["password"])

        email = EmailMessage(
            "[Convey] 비밀번호가 초기화 되었습니다.",
            f"비밀번호가 아래의 임시 비밀번호로 변경되었습니다. 아래 비밀번호로 다시 로그인하신 뒤 꼭 비밀번호를 변경해주세요.\n임시 비밀번호: {new_password}",
            to=[email],  # 받는 이메일
        )
        success = email.send()

        if success > 0:
            return Response(status=status.HTTP_200_OK)
        elif success == 0:
            return Response(
                {"detail": "Failed to send email. Try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class EmailVerification(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="회원가입 과정에서의 이메일 검증을 위해 인증 코드를 이메일로 전송합니다",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"email": openapi.Schema(type=openapi.FORMAT_EMAIL)},
        ),
        responses={
            500: "Failed to send email. Try again later or try with a valid email."
        },
    )
    def post(self, request, *args, **kwargs):
        # check email duplication check status
        is_confirmed = request.COOKIES.get("email_duplication_check")
        if not is_confirmed:
            raise UnprocessableException("proceed email duplication check first")

        email = request.data.get("email")
        generated_code = UserService.generate_random_code(5, 8)
        signer = Signer()
        signed_cookie_obj = signer.sign_object(
            {"email_verification_code": generated_code}
        )

        # set code in cookie
        res = Response({"detail": "email sent"}, status=status.HTTP_200_OK)
        res.set_cookie("email_verification_code", signed_cookie_obj, max_age=300)

        # send email
        email = EmailMessage(
            "[Convey] 이메일 인증 코드입니다.",
            generated_code,
            to=[email],  # 받는 이메일
        )
        success = email.send()

        if success > 0:
            return res
        elif success == 0:
            return Response(
                {
                    "detail": "Failed to send email. Try again later or try with a valid email."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class EmailConfirmation(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="입력한 이메일 인증코드가 정확한지 확인합니다",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"verification_code": openapi.Schema(type=openapi.TYPE_STRING)},
        ),
        responses={
            204: "success",
            400: "No cookies attached",
            409: "Verification code does not match",
        },
    )
    def post(self, request, *args, **kwargs):
        if "email_verification_code" in request.COOKIES:
            code_cookie = request.COOKIES.get("email_verification_code")
            signer = Signer()
            unsinged_code_cookie = signer.unsign_object(code_cookie).get(
                "email_verification_code"
            )
        else:
            raise UnprocessableException("proceed email verification first")

        code_input = request.data.get("verification_code")
        if unsinged_code_cookie == code_input:
            res = Response(status=status.HTTP_204_NO_CONTENT)
            if "email_confirmation_code" in request.COOKIES:
                res.delete_cookie("email_verification_code")
            res.set_cookie("email_confirmation", "complete", max_age=600)
            return res
        else:
            raise ConflictException("Verification code does not match")


class TokenRefreshView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [CustomRenderer]

    @swagger_auto_schema(
        operation_summary="Refresh token",
        operation_description="refresh token 을 쿠키에 저장합니다. 유효기간은 7일 입니다",
        manual_parameters=[
            openapi.Parameter(
                "Authentication",
                openapi.IN_HEADER,
                description="bearer token",
                type=openapi.TYPE_STRING,
            )
        ],
        responses={
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "access_token": openapi.Schema(
                        type=openapi.TYPE_STRING, description="새로운 액세스 토큰"
                    )
                },
            ),
            401: "Authentication Failed",
        },
    )
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"]) or None
        print(request.META.get("HTTP_COOKIE"))
        access_token = request.META.get("HTTP_AUTHORIZATION") or None

        # authenticate() verifies and decode the token
        # if token is invalid, it raises an exception and returns 401
        refresh_token_authenticator = RefreshTokenAuthentication()
        access_token_authenticator = JWTAuthentication()

        try:
            access_token_validation = access_token_authenticator.authenticate(request)
            return Response(
                "Access token not expired", status=status.HTTP_204_NO_CONTENT
            )
        except InvalidToken:
            # access_token is invalid
            try:
                user, validated_token = refresh_token_authenticator.authenticate(
                    request
                )
                new_access, new_refresh = UserService.generate_tokens(user)
                res = Response(
                    dict(access_token=new_access, refresh_token=new_refresh),
                    status=status.HTTP_201_CREATED,
                )
                res.set_cookie(
                    settings.SIMPLE_JWT["AUTH_COOKIE"],
                    new_refresh,
                    max_age=60 * 60 * 24 * 14,
                )  # 2 weeks
                return res

            except InvalidToken:
                raise AuthenticationFailed("Both tokens are invalid. Login again.")


class AppSignInView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="앱 사용자를 위한 로그인",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name", "email", "social_provider"],
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING),
                "email": openapi.Schema(type=openapi.TYPE_STRING),
                "social_provider": openapi.Schema(
                    type=openapi.TYPE_STRING, description="소셜 로그인 플랫폼 ex) kakao"
                ),
            },
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "access_token": openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
        },
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        if len(request.data) != 3:
            raise ValidationError(
                "body should include 'name', 'email' and 'socialProvider'"
            )

        try:
            user = get_object_or_404(User, **request.data)
        except Http404:
            raise AuthenticationFailed("No user with the provided data")

        update_last_login(None, user)
        serializer = UserSerializer(user)
        access_token, refresh_token = UserService.generate_tokens(user)

        data = serializer.data
        data["access_token"] = access_token
        data["refresh_token"] = refresh_token

        res = Response(
            data,
            status=status.HTTP_200_OK,
        )

        # TODO: secure, http-only
        res.set_cookie(
            settings.SIMPLE_JWT["AUTH_COOKIE"],
            refresh_token,
            max_age=settings.SIMPLE_JWT["AUTH_COOKIE_EXPIRES"],
        )  # 7 days
        return res


class AppSignUpView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="앱 사용자들을 위한 회원가입, 회원의 정보를 보냅니다",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name", "email", "social_provider", "privacy_policy_agreed"],
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING),
                "email": openapi.Schema(type=openapi.TYPE_STRING),
                "social_provider": openapi.Schema(
                    type=openapi.TYPE_STRING, description="소셜 로그인 플랫폼 ex) kakao"
                ),
                "privacy_policy_agreed": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN, description="개인정보동의 여부"
                ),
            },
        ),
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        if len(request.data) != 4:
            raise ValidationError(
                "body should include 'name', 'email', 'socialProvider' and 'privacyPolicyAgreed' fields"
            )

        # check duplicate email
        try:
            existing_user = get_object_or_404(
                User, email=request.data.get("email"), role=User.UserType.SUBJECT
            )
            raise DuplicateInstance(
                "app user with the provided email already exists, check other social provider?"
            )
        except Http404:
            data = request.data
            data["role"] = User.UserType.SUBJECT.value
            data["password"] = "00000000"
            print(data)
            serializer = UserSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
