from __future__ import unicode_literals
from django.db import models
from django.core import validators
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.http import urlquote
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager
from tz_cntry import COUNTRY,TIMEZONES

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not username or not email:
            raise ValueError('The given username and email must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, is_active=True,last_login=now,date_joined=now,verified_email=False, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)



class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        _('username'),
        max_length=30,
        db_index=True,
        primary_key=True,
        unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, digits and _ only.'),
        validators=[
            validators.RegexValidator(
                r'^[A-Z0-9a-z_]*[A-Z0-9a-z][A-Z0-9a-z_]*$',
                _('Enter a valid username. This value may contain only '
                  'letters, numbers and _ characters with atleast one letter or digit.')
            ),
        ],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(_('email address'), max_length=254, unique=True,help_text="Email")
    first_name = models.CharField(_('first name'), max_length=30,help_text="First Name",blank=False,
        validators=[
            validators.RegexValidator(
                r'^[A-Za-z][A-Za-z]*$',
                _('Enter a valid First Name. This value may contain only '
                  'alphabets..')
            ),
        ],)
    last_name = models.CharField(_('last name'), max_length=30,help_text="Last Name",blank=False,
        validators=[
            validators.RegexValidator(
                r'^[A-Za-z][A-Za-z]*$',
                _('Enter a valid Last Name. This value may contain only '
                  'alphabets.')
            ),
        ],)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    """
    is_locked = models.BooleanField(
        _('locked'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as locked. '
        ),
    )"""
    verified_email = models.BooleanField(_('email verified'),default=False,help_text="Has Email been verified or not")
    hashcheck = models.CharField(_('hash check'),blank=True,max_length=256,help_text="Hash Check for Email Verification")
    phone = models.CharField(_('Contact Number(digits only)'),max_length=25,help_text="Contact Number.",blank=False,validators=[
            validators.RegexValidator(
                r'^[0-9][0-9]*$',
                _('Enter a valid Mobile Number. Only digits.No need for Area codes.')
            ),
        ],)
    country = models.CharField(_('Country'),default='INDIA;IN',max_length=60,choices=COUNTRY,help_text='Country')
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now,help_text='Date of Registeration')
    timezone = models.CharField(_('TimeZone'),default='Asia/Kolkata',max_length=50,choices=TIMEZONES,help_text='Timezone')
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        app_label = 'users'
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __unicode__(self):
        return "%s" % (self.username)    

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def get_absolute_url(self):
        return reverse('users:profileview', args=(self.username,))


    def delete(self, *args, **kwargs):
        super(User, self).delete(*args, **kwargs)

    def is_emailverified(self):
        "Returns whether email is verified or not."
        return self.verified_email