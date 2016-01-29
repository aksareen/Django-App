from django import forms
from elections.models import Election,Question,Candidate,Voter,Vote
from datetime import timedelta
from django.utils import timezone
import pytz
from datetimewidget.widgets import DateTimeWidget
#from django.core.exceptions import ValidationError

"""
def is_dst(zonename):
    tz = pytz.timezone(zonename)
    now = pytz.utc.localize(datetime.utcnow())
    return now.astimezone(tz).dst() != timedelta(0)
    #example : is_dst("America/Los_Angeles")
    # True/False
    
UTC to local:-
>>> import datetime, pytz
>>> local_tz = pytz.timezone('Asia/Tokyo')
>>> datetime.datetime.now().replace(tzinfo=pytz.utc).astimezone(local_tz)
datetime.datetime(2011, 3, 4, 16, 2, 3, 311670, tzinfo=<DstTzInfo 'Asia/Tokyo' JST+9:00:00 STD>)

local to UTC:-

>>> import datetime, pytz
>>> datetime.datetime.now()
datetime.datetime(2011, 3, 4, 15, 6, 6, 446583)
>>> datetime.datetime.now(pytz.utc)
datetime.datetime(2011, 3, 4, 7, 6, 22, 198472, tzinfo=<UTC>)

"""
class ElectionCreateForm(forms.ModelForm):
    error_messages = {
        'No_User_exists' : "No User exists",
        'starts_too_early': "The election must start after minimum 1 hour from current UTC Time.",
        'ends_too_early': "The election must end after minimum 3 hours from start time.",
        'ends_too_late': "The election must end after maximum 48 hours from start time.",
        'slug_exists': "The slug already exists. Try another one",
        'prefix_exists' : "The prefix already exists.Please try another."
    }

    class Meta:
        model = Election
        fields = ("name","organisation","privacy","description","timezone","starts","ends","voter_prefix","slug","instructions")
        
        dateTimeOptions = {
        'format': 'yyyy-mm-dd hh:ii',
        'weekStart' : 1,
        #timezone.now() is in UTC format.
        #NEED AJAX TO DYNAMICALLY KNOW THE TIMEZONE and Set time values accordingly.
        'startDate' : (timezone.now()-timedelta(hours=26)).strftime("%Y-%m-%d %H:%M"), 
        'endDate' : (timezone.now()+timedelta(weeks=12)).strftime("%Y-%m-%d %H:%M"),
        'autoclose': True,
        'showMeridian' : True,
        #'minView' : 1,
        'maxView' : 2,
        #'todayHighlight' : True,
        'minuteStep' : 30,
        }

        #If using format then don't turn localisation = True
        widgets = {
            'starts': DateTimeWidget(usel10n = False, bootstrap_version=3, options = dateTimeOptions),
            'ends': DateTimeWidget(usel10n = False, bootstrap_version=3,options = dateTimeOptions),
            'instructions' :  forms.Textarea(attrs={"rows" : "7" }),
            'description' : forms.Textarea(attrs={"rows" : "7"}),  
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self._starts_utc = None
        super(ElectionCreateForm, self).__init__(*args, **kwargs)
        if self.user is None:
            raise forms.ValidationError(
                self.error_messages['No_User_exists'],
                code ='No_User_exists',
            )

        for field_name in self.fields:
            field = self.fields.get(field_name)
            if field:
                field.widget.attrs.update({
                    'placeholder': field.help_text,
                    'required' : True,
                })

    def save(self, commit=True):
        election = super(ElectionCreateForm, self).save(commit=False)
        election.user = self.user
        if commit:
            election.save()
        return election

    def clean_starts(self):
        tz_user = pytz.timezone(self.cleaned_data.get("timezone"))
        #print self.cleaned_data.get("starts").replace(tzinfo=None)
        starts1 = tz_user.localize(self.cleaned_data.get("starts").replace(tzinfo=None))
        #print starts1
        #starts_usertz = tz_user.normalize(self.cleaned_data.get("starts").astimezone(tz_user))
        self._starts_utc = starts1.astimezone(pytz.utc)
        #print starts_usertz
        #print self._starts_utc
        #print timezone.now() #+00:00
        #print timezone.localtime(timezone.now())#+05:30
        #print "self._starts_utc1 " ,self._starts_utc1
        if (timezone.now() +  timedelta(hours=1)) > self._starts_utc:
            raise forms.ValidationError(
                self.error_messages['starts_too_early'],
                code='starts_too_early',
            )
        return self._starts_utc

    def clean_ends(self):
        tz_user = pytz.timezone(self.cleaned_data.get("timezone"))
        ends1 = tz_user.localize(self.cleaned_data.get("ends").replace(tzinfo=None))
        #ends_usertz = tz_user.normalize(self.cleaned_data.get("ends").astimezone(tz_user))
        ends_utc = ends1.astimezone(pytz.utc)
        starts_utc = self._starts_utc
        #print "ENd utc"
        #print starts_utc
        if starts_utc + timedelta(hours=3) > ends_utc:
            raise forms.ValidationError(
                self.error_messages['ends_too_early'],
                code='ends_too_early',
            )
        if ends_utc > (starts_utc + timedelta(hours=48)):
            raise forms.ValidationError(
                self.error_messages['ends_too_late'],
                code='ends_too_late',
            )
        
        return ends_utc

    def clean_slug(self):
        if Election.objects.filter(slug=self.cleaned_data.get("slug")).exists():
            raise forms.ValidationError(
                self.error_messages['slug_exists'],
                code='slug_exists',
            )
        
        return self.cleaned_data.get("slug")

    def clean_voter_prefix(self):
        voter_prefix = self.cleaned_data.get("voter_prefix")

        #may need a prefix of username regex validator
        if Election.objects.filter(voter_prefix=voter_prefix).exists():
            raise forms.ValidationError(
                self.error_messages['prefix_exists'],
                code='prefix_exists',
            )
        
        return voter_prefix



class ElectionEditForm(forms.ModelForm):
    error_messages = {
        'No_User_exists' : "No User identified.",
    }

    class Meta:
        model = Election
        fields = ("name","organisation","privacy","description","instructions")
        
        #If using format then don't turn localisation = True
        widgets = {
            'instructions' :  forms.Textarea(attrs={"rows" : "7" }),
            'description' : forms.Textarea(attrs={"rows" : "7"}),  
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ElectionEditForm, self).__init__(*args, **kwargs)
        if self.user is None:
            raise forms.ValidationError(
                self.error_messages['No_User_exists'],
                code ='No_User_exists',
            )

        for field_name in self.fields:
            field = self.fields.get(field_name)
            if field:
                field.widget.attrs.update({
                    'placeholder': field.help_text,
                    'required' : True,
                })

    def save(self, commit=True):
        election = super(ElectionEditForm, self).save(commit=False)
        election.user = self.user
        if commit:
            election.save()
        return election



class ElectionDateTimeEditForm(forms.ModelForm):
    error_messages = {
        'No_User_exists' : "No User identified.",
        'starts_too_early': "The election must start after minimum 1 hour from current UTC Time.",
        'ends_too_early': "The election must end after minimum 3 hours from start time.",
        'ends_too_late': "The election must end after maximum 48 hours from start time.",
    }

    class Meta:
        model = Election
        fields = ("timezone","starts","ends")
        
        dateTimeOptions = {
        'format': 'yyyy-mm-dd hh:ii',
        'weekStart' : 1,
        
        #CHECK IF REGISTERED BEFORE AND I TRY TO CHANGE IT NOW
        'startDate' : (timezone.now()-timedelta(hours=26)).strftime("%Y-%m-%d %H:%M"), 
        'endDate' : (timezone.now()+timedelta(weeks=12)).strftime("%Y-%m-%d %H:%M"),
        'autoclose': True,
        'showMeridian' : True,
        #'minView' : 1,
        'maxView' : 2,
        #'todayHighlight' : True,
        'minuteStep' : 30,
        }

        #If using format then don't turn localisation = True
        widgets = {
            'starts': DateTimeWidget(usel10n = False, bootstrap_version=3, options = dateTimeOptions),
            'ends': DateTimeWidget(usel10n = False, bootstrap_version=3,options = dateTimeOptions),
            'instructions' :  forms.Textarea(attrs={"rows" : "6" }),
            'description' : forms.Textarea(attrs={"rows" : "6"}),  
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self._starts_utc = None
        if self.user is None:
            raise forms.ValidationError(
                self.error_messages['No_User_exists'],
                code ='No_User_exists',
            )
        super(ElectionDateTimeEditForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            field = self.fields.get(field_name)
            if field:
                field.widget.attrs.update({
                    'placeholder': field.help_text,
                    'required' : True,
                })

    def save(self, commit=True):
        election = super(ElectionDateTimeEditForm, self).save(commit=False)
        election.user = self.user
        if commit:
            election.save()
        return election

    #ASSUMES TIMEZONE ENTERED IS VALID (Which it is NOW)
    def clean_starts(self):
        tz_user = pytz.timezone(self.cleaned_data.get("timezone"))
        #print self.cleaned_data.get("starts").replace(tzinfo=None)
        starts1 = tz_user.localize(self.cleaned_data.get("starts").replace(tzinfo=None))
        #print starts1
        #starts_usertz = tz_user.normalize(self.cleaned_data.get("starts").astimezone(tz_user))
        self._starts_utc = starts1.astimezone(pytz.utc)

        if (timezone.now() +  timedelta(hours=1)) > self._starts_utc:
            raise forms.ValidationError(
                self.error_messages['starts_too_early'],
                code='starts_too_early',
            )
        return self._starts_utc

    def clean_ends(self):
        tz_user = pytz.timezone(self.cleaned_data.get("timezone"))
        ends1 = tz_user.localize(self.cleaned_data.get("ends").replace(tzinfo=None))
        #ends_usertz = tz_user.normalize(self.cleaned_data.get("ends").astimezone(tz_user))
        ends_utc = ends1.astimezone(pytz.utc)
        starts_utc = self._starts_utc
        #print "ENd utc"
        #print starts_utc
        if starts_utc + timedelta(hours=3) > ends_utc:
            raise forms.ValidationError(
                self.error_messages['ends_too_early'],
                code='ends_too_early',
            )
        if ends_utc > (starts_utc + timedelta(hours=48)):
            raise forms.ValidationError(
                self.error_messages['ends_too_late'],
                code='ends_too_late',
            )
        
        return ends_utc

class CandidatesInlineFormset(forms.models.BaseInlineFormSet):

    def clean(self):
        super(CandidatesInlineFormset, self).clean()
        if any(self.errors):
            raise forms.ValidationError("Incomplete Choice or Details Provided. Please Fill in atleast 2 choices and their Details properly.")
            
        names = []
        count  = 0

        for form in self.forms: #and not form.cleaned_data.get('DELETE', False):
            try:

                if form.cleaned_data:
                    count += 1
                    name = form.cleaned_data["name"]
                    description = form.cleaned_data["description"]
                    if name and description:
                        if name.lower() in names:
                            raise forms.ValidationError("You cannot have duplicate Candidate/Choice Names",code="Duplicate_Candidate")
                        names.append(name.lower())
                    elif name and not description:
                        raise forms.ValidationError("All Choices must have a description",code="Missing_Description")

                    elif description and not name:
                        raise forms.ValidationError("No Choice/Candidate Name Provided",code="Missing_Choice")

                    else:

                        raise forms.ValidationError("No Data Provided for both Choice and Description",code="Missing_Both")

            except AttributeError: #subform error Django raising error for cleaned_data
                pass

 
        if count < 2:
            raise forms.ValidationError('You must have at least 2 Choices',code="Min_choices")


class QuestionForm(forms.ModelForm):
    error_messages = {
        'No_User_exists' : "No User identified.", # Checking from view so not needed now
        'No_Election_Exists'  : "No exisiting Election by You",
    }

    class Meta:
        model = Question
        fields = ("qtype","text",)
        
        widgets = {
            'text' : forms.Textarea(attrs={"rows" : "3"}),  
        }

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            field = self.fields.get(field_name)
            if field:
                field.widget.attrs.update({
                    'placeholder': field.help_text,
                    'required' : True,
                })



from django.core.validators import validate_email
from elections.widgets import MultiEmailWidget


class MultiEmailField(forms.Field):
    message = 'Enter valid email addresses.'
    code = 'invalid_email_address'
    widget = MultiEmailWidget

    def to_python(self, value):
        "Normalize data to a list of strings."
        # Return None if no input was given.
        if not value:
            return []
        return [v.strip() for v in value.splitlines() if v != ""]

    def validate(self, value):
        "Check if value consists only of valid emails."

        # Use the parent's handling of required fields, etc.
        super(MultiEmailField, self).validate(value)


        try:
            for email in value:
                validate_email(email)
        except forms.ValidationError:
            raise forms.ValidationError(self.message, code=self.code)


class EmailForm(forms.ModelForm):
    error_messages = {
        'No_User_exists' : "No User identified.", # Checking from view so not needed now
        'No_Election_Exists'  : "No exisiting Election by You",
    }

    class Meta:
        model = Voter
        fields = ("email","name",)

    def __init__(self, *args, **kwargs):
        super(EmailForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            field = self.fields.get(field_name)
            if field:
                field.widget.attrs.update({
                    'placeholder': field.help_text,
                    'required' : True,
                })


class EmailBulkForm(forms.Form):
    email = MultiEmailField()



class EmailsInlineFormset(forms.models.BaseInlineFormSet):

    def clean(self):
        super(EmailsInlineFormset, self).clean()
        if any(self.errors):
            raise forms.ValidationError("Incomplete Details Provided. Please Fill in atleast 1 Email field.")
            
        emails = []
        count  = 0

        for form in self.forms: #and not form.cleaned_data.get('DELETE', False):
            try:

                if form.cleaned_data:
                    count += 1
                    email = form.cleaned_data["email"]
                    name = form.cleaned_data["name"]
                    if email:
                        if email in emails:
                            raise forms.ValidationError("You cannot have duplicate Emails",code="Duplicate_Email")
                        emails.append(email)
                    else:
                        raise forms.ValidationError("No Data Provided for Email Field",code="Missing_Email")

            except AttributeError: #subform error Django raising error for cleaned_data
                pass
        if count < 1:
            raise forms.ValidationError('You must have at least 1 Voter',code="Min_Voters_Error")
