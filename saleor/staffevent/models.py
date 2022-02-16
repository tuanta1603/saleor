from typing import Union

from django.conf import settings
from django.contrib.auth.models import _user_has_perm  # type: ignore
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    Group,
    Permission,
    PermissionsMixin,
)
from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.db.models import JSONField  # type: ignore
from django.db.models import Q, QuerySet, Value
from django.db.models.expressions import Exists, OuterRef
from django.forms.models import model_to_dict
from django.utils import timezone
from django.utils.crypto import get_random_string
from django_countries.fields import Country, CountryField
from phonenumber_field.modelfields import PhoneNumber, PhoneNumberField
from versatileimagefield.fields import VersatileImageField

# from ..app.models import App
# from ..core.models import ModelWithMetadata
# from ..core.permissions import AccountPermissions, BasePermissionEnum, get_permissions
# from ..core.utils.json_serializer import CustomJsonEncoder
# from ..order.models import Order
# from . import CustomerEvents
# from .validators import validate_possible_number

class StaffEvent(models.Model):
    # id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    staff_email = models.EmailField(blank=True, null=True)
    userid = models.CharField(max_length=256)
    title = models.CharField(max_length=256)
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    send_email = models.BooleanField(default=True)
    ischeck = models.BooleanField(default=False)