from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render #,get_object_or_404
from django.core.urlresolvers import reverse
#from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
#from django.views.decorators.cache import cache_page #, never_cache
#from django.template.response import TemplateResponse
from users.models import User
from django.contrib.auth import authenticate, login , logout
import requests
from Voting.forms import ContactForm
from Voting.settings import GOOGLESECRET_KEY,GOOGLECAPTCHA_URL
from django.contrib import messages

""" USe TemplateResponse only when caching or need to lazy render check documentation or most likely a custom decorator """

from django.shortcuts import redirect
import pytz

#TEST PURPOSES ONLY. [Will be deprecated in future commits]
def set_timezone(request):
    if request.method == 'POST':
        request.session['django_timezone'] = request.POST['timezone']
        return redirect('/')
    else:
        return render(request, 'template.html', {'timezones': pytz.common_timezones})


#@sensitive_post_parameters()
def user_login(request):
    if request.method == 'GET':
        next = request.GET.get('next',None)
        if request.user.is_authenticated():
            if next:
                return HttpResponseRedirect(next)
            else:
                return HttpResponseRedirect(reverse('users:dashboard'))
        else:
            request.session.set_test_cookie()
            return render(request, "users/login.html")

    elif request.method == 'POST':
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
        else:
            messages.error(request,"Please enable cookies and try again.")
            request.session.set_test_cookie()
            return render(request, "users/login.html")
        #Hard-coded HTML FORM , not a django generated one
        username = request.POST.get('username',None)
        password = request.POST.get('password',None)
        user = authenticate(username=username, password=password)

        if user is not None:

            if user.is_active:

                #if is_safe_url only then else redirect
                login(request, user)
                response = HttpResponseRedirect(reverse('users:dashboard'))
                #response.set_cookie("user",user)
                #print "NOW"
                #for i in request.COOKIES:
                #    print request.COOKIES[i]
                return response
            else:
                # An inactive account was used - no logging in!
                messages.error(request, 'Your Account has been locked out.An email has been sent to you to verify your account details')
                request.session.set_test_cookie()
                return render(request, "users/login.html")
        else:
            # Invalid login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            messages.error(request, 'Invalid Username/Password combination.')
            request.session.set_test_cookie()
            return render(request, "users/login.html")
    else:
        return HttpResponse("BAD REQUEST",status=400)

def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('homepage'))



def homepage(request):
    return render(request,"homepage.html")



from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.template import Context

def contact_us(request):
    if request.method=='GET':
        return render(request,"Voting/contactus.html",{'form' : ContactForm})    

    elif request.method=='POST':
        new_data = request.POST.copy()
        form = ContactForm(data=new_data)
        captcha = request.POST.get('g-recaptcha-response',None)

        dicr = {}
        dicr['secret']=GOOGLESECRET_KEY
        dicr['response']=captcha
        result = requests.post(GOOGLECAPTCHA_URL, data=dicr)
        captcha_bool = False
        
        if result.json()["success"]:
            captcha_bool=True
        else:
            context = {}
            context['Error']="Please Verify the Captcha Properly"
            form = ContactForm(initial=new_data)
            context['form'] = form
            return render(request,"Voting/contactus.html",context)


        if form.is_valid() and captcha_bool:
            fname = form.cleaned_data['fname']
            lname = form.cleaned_data['lname']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            message = form.cleaned_data['message']
            template = get_template('Voting/contact_template.txt')
            context = Context({
                              'fname' : fname,
                              'lname' : lname,
                              'email' : email,
                              'phone' : phone,
                              'message' : message,
                              })
            content = template.render(context)
            email = EmailMessage("New form contact submission",content,"iVote Contact Query" ,
                                  ['ashish.sareen95@gmail.com'],
                                  headers = { 'Reply-To' : email }
                                 )
            email.send()
            messages.success(request, "Thank you for contacting us.We will get back to you within 48 hours. Have a Nice Day :D")
            return render(request,"Voting/contactus.html",{'form' : ContactForm})

        else:
            context = {} 
            context['Error']="Please refill in the required details correctly and Verify Captcha"
            form = ContactForm(initial=new_data)
            context['form'] = form
            return render(request,"Voting/contactus.html",context)
    else:
        return HttpResponse("BAD REQUEST",status=400)



"""
def send_email(user, pwd, recipient, subject, body):
    import smtplib

    gmail_user = user
    gmail_pwd = pwd
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = '''\From: %s\nTo: %s\nSubject: %s\n\n%s
    ''' % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print 'successfully sent the mail'
    except:
        print "failed to send mail"
to use Port 465 need to create an SMTP_SSL object:

# SMTP_SSL Example
server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
server_ssl.ehlo() # optional, called by login()
server_ssl.login(gmail_user, gmail_pwd)  
# ssl server doesn't support or need tls, so don't call server_ssl.starttls() 
server_ssl.sendmail(FROM, TO, message)
#server_ssl.quit()
server_ssl.close()
print 'successfully sent the mail'
"""