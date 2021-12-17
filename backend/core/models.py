from django.db import models

from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)


class UserManager(BaseUserManager):

    def create_user(
            self,
            email: str,
            password: str = None,
            **kwargs
        ) -> AbstractBaseUser:
        """
        Creates and saves a new user

        Args:
        --------
            email (str):
                User email address
            password (str, default=None):
                User password

        Raises:
        --------
            ValueError: Email address not provided

        Returns:
        --------
            AbstractBaseUser: A user-model object
        """
        if not email:
            raise ValueError("Email address required")

        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(
            self,
            email: str,
            password: str = None
        ) -> AbstractBaseUser:
        """
        Creates and saves a new superuser

        Args:
        --------
            email (str):
                User email address
            password (str, default=None):
                User password

        Returns:
        --------
            AbstractBaseUser: A (super)user-model object
        """
        user = self.create_user(email=email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that supports using email instead of username
    """
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()
    USERNAME_FIELD = "email"
