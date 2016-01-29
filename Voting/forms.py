from django import forms

class ContactForm(forms.Form):
    fname = forms.CharField(max_length = 55 , required=True,help_text="First Name" , widget=forms.TextInput(attrs={'required': True,'class': 'form-control' , 'placeholder' : 'First Name',}))
    lname = forms.CharField(max_length = 55 , required=True,help_text="Last Name",widget=forms.TextInput(attrs={'required': True,'class': 'form-control', 'placeholder' : 'Last Name'}))
    email = forms.EmailField(max_length=254,required=True,help_text="Email Address",widget=forms.EmailInput(attrs={'required': True,'class': 'form-control', 'placeholder' : 'Email'}))
    phone = forms.CharField(max_length=25,required=True,help_text="Phone",widget=forms.TextInput(attrs={'required': True,'class': 'form-control', 'placeholder' : 'Phone'}))
    message = forms.CharField(max_length=1000,required=True,widget=forms.Textarea(attrs={'required': True,'class' : 'form-control','rows' : '7', 'placeholder' : 'Enter your Feedback/Query/Message for us here. We value our user\'s opinions.'}))
"""
    widgets = {
            'fname': forms.TextInput(
                attrs={'id': 'post-text', 'required': True, 'placeholder': 'Input fiels text placeholder...'}
            ),
        
        """