import smtplib
from django.core.mail import send_mail
from .models import Meet,MeetParticipant
from django.utils.timezone import now
import datetime
from django.contrib.auth.models import User


def rememberMeet(message,to_user):
    send_mail("Toplantınız Başlama Üzere",message,"brainsforce@gmail.com",to_user,fail_silently=False)
    return True



def overlap(first_inter,second_inter):
    for f,s in ((first_inter,second_inter), (second_inter,first_inter)):
        #will check both ways
        for time in (f["start_date"], f["finish_date"]):
            if s["finish_date"] < time < s["finish_date"]:
                return True
    else:
        return False


def test():

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

            rememberMeet(messages,userData)

# {'id': 1, 'meet_id': 1, 'participant_id': 3}