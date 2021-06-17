from .utils import rememberMeet
from .models import Meet,MeetParticipant
from django.core.mail import send_mail
from django.utils.timezone import now
import datetime
from django.contrib.auth.models import User


def my_scheduled_job():
    meetsData = Meet.objects.all()
    meets = meetsData.values('id','title','start_date')
    userData = []
    for meet in meets:
        test = meet.get('start_date') - now()
        if((datetime.timedelta(minutes=15)) > test and str(test).startswith("-") == False):
            members = MeetParticipant.objects.filter(meet_id=meet.get('id')).values('participant')
            for i in members:
                email = User.objects.filter(id=i.get('participant')).values('email')
                for e in email:
                    userData.append(e.get('email'))
            
            messages = meet.get('title') + "başlık toplantınız" +str(meet.get('start_date')) + "başlamaktadır."
            send_mail("Toplantı Hatırlatma",messages,"brainsforce@gmail.com",userData,fail_silently=False)
