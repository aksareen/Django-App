from django.utils.encoding import smart_str
import hashlib
from random import random

def get_hexdigest(algorithm, salt, raw_password):
    raw_password, salt = smart_str(raw_password), smart_str(salt)
    if algorithm == 'sha1':
        return hashlib.sha1(salt + raw_password).hexdigest()
    raise ValueError("Got unknown password algorithm type in password.")


def make_password(raw_password):
    algo = 'sha1'
    salt = get_hexdigest(algo, str(random()), str(random()))[:10]
    hashh = get_hexdigest(algo, salt, raw_password)
    return '%s$%s$%s' % (algo, salt, hashh)

def check_password(raw_password, password):
    algo, salt, hashh = password.split('$')
    return hashh == get_hexdigest(algo, salt, raw_password) 


#mypassword = 'MY_PWD'
#encrypted_pwd = make_password(mypassword)
#check_password('MY_PD',make_password('MY_pd'))
