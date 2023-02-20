from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
import logging

from config.mixins import TimeStampMixin, SoftDeleteMixin


class UserManager(BaseUserManager):
    """
    Custom account model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    use_in_migrations = True

    def create_user(
        self,
        email=None,
        password=None,
        **extra_fields,
    ):
        """
        Create and save a User with the given email and password.
        """
        extra_fields.setdefault("is_superuser", False)

        if not email:
            raise ValueError("Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)

        user.save(using=self._db)
        logging.info(f"User [{user.id}] 회원가입")
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_deleted", False)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email=email, password=password, **extra_fields)


class User(AbstractBaseUser, TimeStampMixin, SoftDeleteMixin, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(max_length=64, unique=True, null=False)
    name = models.CharField(max_length=10, null=False)

    is_staff = models.BooleanField(
        default=False,
    )

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        db_table = "user"
        unique_together = ["email"]

    def __str__(self):
        return f"[{self.id}] {self.get_username()}"

    def __repr__(self):
        return f"User({self.id}, {self.get_username()})"
