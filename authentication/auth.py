from django.http import HttpResponseRedirect
import mycrypt
import json

def isuser(f):
    def wrap(request, *args, **kwargs):
        try:
            token = request.META['HTTP_ACCESSTOKEN']
            token = mycrypt.parse(token)
            if (token[:len(mycrypt.VALIDATION_KEY)] != mycrypt.VALIDATION_KEY) or (json.loads(token[len(mycrypt.VALIDATION_KEY):])['access_level']>0):
                return HttpResponseRedirect("/authentication/bad_request")
            return f(request, *args, **kwargs)
        except:
            return HttpResponseRedirect("/authentication/bad_request")
    wrap.__doc__=f.__doc__
    wrap.__name__=f.__name__
    return wrap

def isvalid(f):
    def wrap(request, *args, **kwargs):
        try:
            token = request.META['HTTP_ACCESSTOKEN']
            token = mycrypt.parse(token)
            if (token[:len(mycrypt.VALIDATION_KEY)] != mycrypt.VALIDATION_KEY):
                return HttpResponseRedirect("/authentication/bad_request")
            return f(request, *args, **kwargs)
        except:
            return HttpResponseRedirect("/authentication/bad_request")
    wrap.__doc__=f.__doc__
    wrap.__name__=f.__name__
    return wrap


def get_user(request):
    token = request.META['HTTP_ACCESSTOKEN']
    token = mycrypt.parse(token)
    return json.loads(token[len(mycrypt.VALIDATION_KEY):])

#expects dictionary as argument
def get_token(user_details):
    tmp = json.dumps(user_details)
    return mycrypt.encrypt(mycrypt.VALIDATION_KEY + tmp)