from django import forms
from .models import User
from django.contrib.auth import authenticate

"""
class Meta:
        model = User
        fields = ("first_name","last_name","username","email","phone","country","timezone")
        error_messages = {
            'username': {
                'max_length': "This username name is too long.",
            },
        }
        labels = {
            'username': _('Username'),
        }
        help_texts = {
            'username': _('Some useful help text.'),
        }
"""

class UserRegisterForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': "The two password fields didn't match.",
        'username_exists': "The username already exists.",
        'email_exists': "The email id is already registered.",
        'terms_unchecked' : "You haven't accepted our Terms and Conditions.",
    }
    username =  forms.CharField(min_length = 4,max_length=30,label="Username",help_text="Username",widget=forms.TextInput)
    password1 = forms.CharField(min_length= 4,required=True,label="Password",help_text="Password",widget=forms.PasswordInput)
    password2 = forms.CharField(min_length= 4,required=True,label="Password confirmation",widget=forms.PasswordInput,help_text="Enter the same password as before, for verification.")
    terms = forms.BooleanField(required=True,label="Terms and Conditions")
   
    class Meta:
        model = User
        fields = ("first_name","last_name","username","email","phone","country","timezone")
        error_messages = {
            'username': {
                'max_length': "This username name is too long.",
            },
        }
    
    def __init__(self,*args,**kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            field = self.fields.get(field_name)
            if field:
                field.widget.attrs.update({
                    'placeholder': field.help_text,
                    'required' : True,
                })

    def clean_username(self):
        username1 = self.cleaned_data.get("username")

        if User.objects.filter(username=username1).exists():
            raise forms.ValidationError(
                self.error_messages['username_exists'],
                code='username_exists',
            )
        
        return username1

    def clean_email(self):
        email1 = self.cleaned_data.get("email")

        if User.objects.filter(email=email1).exists():
            raise forms.ValidationError(
                self.error_messages['email_exists'],
                code='email_exists',
            )
        return email1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        #self.instance.username = self.cleaned_data.get('username')
        #validate_password(self.cleaned_data.get('password2'), self.instance)
        """ Validate password for validators and password strength"""
        return password2

    def clean_terms(self):
        terms1 = self.cleaned_data.get("terms")
        if not terms1:
            raise forms.ValidationError(
                self.error_messages['terms_unchecked'],
                code='terms_unchecked',
            )
        return terms1

    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user




class UserChangeForm2(forms.ModelForm):
    error_messages = {
        'password_mismatch': "The password entered is incorrect.",
        'No_username': "No Username Provided",
        'email_exists': "The email id is already registered.",
    }

    password1 = forms.CharField(required=True,label="Password to Verify Changes(if made)",help_text="Enter the password to verify changes if made",widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = fields = ("first_name","last_name","email","password1")

    def __init__(self, *args, **kwargs):
        super(UserChangeForm2, self).__init__(*args, **kwargs)
        userid = self.instance.username
        if userid is None:
            raise forms.ValidationError(
                self.error_messages['No_username'],
                code='No_username',
            )
        

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        userid = self.instance.username
        if userid and password1:
            usr = authenticate(username=userid,password=password1)
            if usr is None:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
            return password1
        else:
            raise forms.ValidationError(
                    self.error_messages['No_username'],
                    code='No_username',
                )

    def clean_email(self):
        email1 = self.cleaned_data.get("email")
        username1 = self.instance.username
        try:
            #HAVE TO MAKE CHANGES HERE WHEN UPDATE DB TO HOLD MULTIPLE EMAILS
            email_qry = User.objects.get(email=email1)
            if email_qry.username == username1:
                return email1
            else:
                raise forms.ValidationError(
                    self.error_messages['email_exists'],
                    code='email_exists',
                )        
        except User.DoesNotExist:
            self.instance.verified_email = False
            #ADD EMAIL VERIFY FUNCTION HERE VVVIIPPPP
            return email1


"""
     def confirm_login_allowed(self, user):
        
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.
        If the given user cannot log in, this method should raise a
        ``forms.ValidationError``.
        If the given user may log in, this method should return None.
        
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )
       
"""
# LATER USER BETTER CACHE
'''
class AuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    username = forms.CharField(max_length=254,label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    error_messages = {
        'invalid_login': "Please enter a correct username and password. "
                           "Note that both fields may be case-sensitive.",
        'inactive': "This account is inactive.",
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super(AuthenticationForm, self).__init__(*args, **kwargs)

        # Set the label for the "username" field.
        UserModel = get_user_model()
        self.username_field = UserModel._meta.get_field(UserModel.USERNAME_FIELD)
        if self.fields['username'].label is None:
            self.fields['username'].label = capfirst(self.username_field.verbose_name)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username,
                                           password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data
'''