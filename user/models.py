from django.db import models
from django.contrib.auth.models import User, Permission
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import Group
from django.contrib.auth.models import AbstractUser, AbstractBaseUser


class ActionSet(models.Model):
    action = models.CharField(max_length=64, null=False)
    description = models.TextField(max_length=1024, null=True)
    permission = models.ForeignKey(Permission, models.CASCADE, related_name='permission')


class Permission(models.Model):
    name = models.CharField(max_length=128, null=False)
    description = models.TextField(max_length=1024, null=True)


class Role(models.Model):
    name = models.CharField(max_length=128, null=False)
    description = models.TextField(max_length=1024, null=True)
    actions = models.ManyToManyField(ActionSet, blank=True)


class ZstUser(AbstractUser):
    REQUIRED_FIELDS = ['telephone', 'email', 'is_active']
    telephone = PhoneNumberField(blank=True, null=True)
    roles = models.ManyToManyField(Role, blank=True)
    actions = models.ManyToManyField(ActionSet, blank=True)

    def __str__(self):
        return f"User: {self.username}"



