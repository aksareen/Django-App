from authentication.models import OTP
import datetime
def send_otp(uid, phone):
    otp = ''.join(["%s" % randint(0, 9) for num in range(0, 4)])
    p, created = OTP.objects.get_or_create(user_id = uid)
    if created:
        p.otp = otp
        p.tries += 1
        p.save()
    else:
        if p.tries <= 3 or (datetime.datetime.now() - p.time).total_seconds() > 1800: 
            p.time = datetime.datetime.now()
            p.tries = (p.tries + 1)%4
            p.otp = otp
            p.save()
        else:
            return False
    # to add the otp sending part

def confirm_otp(id, otp):
    try:
        p = OTP.objects.get(user_id=id)
        return p.otp == otp
    except:
        return False