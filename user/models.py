from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
class ZstUser(AbstractUser):
   telephone = PhoneNumberField(blank=True, null=True)
   birth_date = models.DateField(blank=True, null=True)
