from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404,render
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
#from django.template.response import TemplateResponse
from django.contrib.auth.forms import PasswordChangeForm
from .models import User
from django.contrib.auth import authenticate, login , logout, update_session_auth_hash
from django.views.decorators.csrf import csrf_protect
from .forms import UserRegisterForm,UserChangeForm2
import requests
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib import messages
from Voting.settings import GOOGLESECRET_KEY,GOOGLECAPTCHA_URL
#from django.views.decorators.cache import cache_page,never_cache

""" USe TemplateResponse only when caching or need to lazy render check documentation """

def profile(request,username):
    #print username
    usr = get_object_or_404(User, pk=username)
    return HttpResponse(usr.username)


@login_required
def dashboard(request):
    return render(request, 'users/dashboard.html')

#edit user settings
@login_required
def user_settings(request):
    if not request.user.is_authenticated():
        return HttpResponse("ACCESS DENIED",status=403)#never will occur probably
        
        """Add Function to Email Admin. Probably some error never supposed to occur"""

    context = {}
    if request.method=='POST':
        form = UserChangeForm2(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            context['form'] = form
            messages.success(request, 'Profile details updated.')            
            return render(request,"users/user_settings.html",context)

        context['form'] = form
        return render(request,"users/user_settings.html",context)

    form = UserChangeForm2(instance=request.user)
    context['form'] = form
    return render(request,"users/user_settings.html",context)



def signup_form(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('users:dashboard'))
    
    if request.method=='GET':
        return render(request,"users/signup.html",{'form' : UserRegisterForm})

    elif request.method=='POST':
        form = UserRegisterForm(data=request.POST.copy())
        captcha = request.POST.get('g-recaptcha-response',None)

        dicr = {}
        dicr['secret']=GOOGLESECRET_KEY
        dicr['response']=captcha
        result = requests.post(GOOGLECAPTCHA_URL, data=dicr)
        captcha_bool = False
        context = {}
        if result.json()["success"]:
            captcha_bool=True
        else:
            context['Captcha_Error']="Please Verify the Captcha Properly"
        
        if form.is_valid() and captcha_bool:
            form.save()
            return HttpResponse("congratulations Verify your email now")
        
        context['form'] = form #UserRegisterForm(initial=form.cleaned_data)
        return render(request,"users/signup.html",context)


    else:
        return HttpResponse("BAD REQUEST",status=400)

@sensitive_post_parameters()
@csrf_protect
@login_required
def UpdatePassword(request):
    
    form = PasswordChangeForm(user=request.user)

    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return render(request,'users/update_password.html',{'pwd_changed' : True})

    return render(request, 'users/update_password.html', {
        'form': form,
    })

@login_required
def verify_email(request):
    return HttpResponse("EMAIL VERIFIER PAGE")

@login_required
def unverified_email(request):
    return render(request, 'users/unverified.html')