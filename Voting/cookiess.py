import datetime

def set_cookie(response, key, value, days_expire = 7):
  if days_expire is None:
    max_age = 365 * 24 * 60 * 60  #one year
  else:
    max_age = days_expire * 24 * 60 * 60 
    expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key, value, max_age=max_age, expires=expires, domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE or None)
#Use the following code before sending a response.

def view2(request):
  response = HttpResponse("hello")
  set_cookie(response, 'name', 'jujule')
  return response



 # Setting a cookie:

def view4(request):
  response = HttpResponse( 'blah' )
  response.set_cookie( 'cookie_name', 'cookie_value' )
#Retrieving a cookie:

def view3(request):
  if request.COOKIES.has_key( 'cookie_name' ):
    value = request.COOKIES[ 'cookie_name' ]