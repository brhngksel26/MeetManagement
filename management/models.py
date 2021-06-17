from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Account(models.Model):
    DEPARTMENT = (
        ("R&D","R&D"),
        ("Human Resource","Human Resource"),
        ("Financing","Financing"),
        ("board of Directors","board of Directors"),
    )

    user = models.OneToOneField(User,null=True,blank=True,on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=25,null=True)
    profile_image = models.ImageField(default="profil_dafault.jpg")
    department = models.CharField(max_length=20,choices=DEPARTMENT)


    def __str__(self):
        return str(self.user)

class Meet(models.Model):
    LOCATION = (
        ('Office','Office'),
        ('Online','Online'),
    )
    creater_account = models.ForeignKey(Account,null=False,blank=True,on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    meet_links = models.URLField(max_length=100,null=True)
    meet_location = models.CharField(max_length=10,choices=LOCATION)
    start_date = models.DateTimeField(blank=True)
    finish_date = models.DateTimeField(blank=True)
    finished = models.BooleanField(default=False)
    summary = models.TextField()


    def __str__(self):
        return self.title

    def get_participant(self):
        participant = list(self.meetparticipant_set.all())
        return participant
    
    

class MeetParticipant(models.Model):
    meet = models.ForeignKey(Meet,on_delete=models.CASCADE)
    participant = models.ForeignKey(User,null=False,blank=True,on_delete=models.CASCADE)


    def __str__(self):
        return (str(self.meet) +"-"+str(self.participant))
    
    def get_meet(self):
        meet = list(self.meet_set.all())
        return meet
