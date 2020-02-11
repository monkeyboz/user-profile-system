"""
Definition of models.
"""

import json

from django.db import models
from django.utils import timezone
from django.db.models import Sum

class Client(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=200,unique=True)
    email = models.CharField(max_length=200,unique=True)
    password = models.CharField(max_length=200)
    active = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return 'Client: '+self.username+' - '+str(self.id)

    def getMainClientInfo(self):
        return MainClientInfo.objects.filter(client_id=self.id)

    def getClientInfo(self):
        return ClientInfo.objects.filter(client_id=self.id)
    def getPositionInfo(self):
        return PositionInfo.objects.filter(client_id=self.id)
    def getFile(self):
        return File.objects.filter(client_id=self.id)
    
class Position(models.Model):
    id = models.AutoField(primary_key=True)
    location = models.CharField(max_length=100,unique=True)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)

    def save(self):
        size = len(Position.objects.filter(location=self.location).values())
        if size < 1:
            super().save()

    def __str__(self):
        return 'Location: '+self.location+' - '+str(self.id)

class Calendar(models.Model):
    id = models.AutoField(primary_key=True)
    name=models.CharField(max_length=100,default="nothing")
    client_id = models.ForeignKey(Client,on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    calendar_duration = models.FloatField(max_length=10,default=1)
    description = models.TextField()
    type=[('e','event'),('c','calendar'),('p','public-event')]
    calendar_type = models.CharField(max_length=1,choices=type,default='e')
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return 'Calendar: '+self.name+' - ('+str(self.id)+')'

class File(models.Model):
    id = models.AutoField(primary_key=True)
    type = [('c','calendar'),('t','temporary'),('p','permenant')] 
    file_type = models.CharField(max_length=1,choices=type,default='c') #required
    path = models.TextField(unique=True) #required
    virusscan_resource = models.CharField(max_length=200,null=True) #required
    scan_date = models.DateTimeField(null=True)
    virus = models.TextField()
    client_id = models.ForeignKey(Client,on_delete=models.CASCADE) #required
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return 'File: '+self.path+' - ('+str(self.id)+')'

    def getVirusDefs(self):
        tl = ''
        scans = json.loads(self.virus)
        totals = ''
        for a in scans['scans']:
            if scans['scans'][a]['detected'] == True:
                detected = 'true'
                info = '<span class="'+detected+'">'+a+'</span>'
                sections = []
                for m in scans['scans'][a]:
                    info += '<div>'+m+': '+str(scans['scans'][a][m])+'</div>'
                totals += info+'<br/>'
        if len(totals) < 1:
            totals = '<div style="color: #00ff00;">No Viruses</div>'
        return totals

class CalendarFile(models.Model):
    id = models.AutoField(primary_key=True)
    calendar_id = models.ForeignKey(Calendar,on_delete=models.CASCADE)
    file_id = models.ForeignKey(File,on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)

class PositionInfo(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.CharField(max_length=200)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zip = models.CharField(max_length=255)
    position_id = models.ForeignKey(Position,on_delete=models.DO_NOTHING,db_constraint=False)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)

    def save(self,*args,**kargs):
        print(self.country+' '+self.state+' '+self.city)
        size = len(PositionInfo.objects.filter(country=self.country,city=self.city,state=self.state).values())
        if size < 1:
            super().save(*args,**kargs)
    def __str__(self):
        return self.city+' '+self.state+' - '+str(self.id)

    def address(self):
        return '{} {}, {} {}'.format(self.country,self.city,self.state,self.zip)

class ClientInfo(models.Model):
    id = models.AutoField(primary_key=True)
    client_id = models.ForeignKey(Client,on_delete=models.DO_NOTHING,db_constraint=False)
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    position_info = models.ForeignKey(PositionInfo,on_delete=models.DO_NOTHING,db_constraint=False)
    access_key = models.CharField(max_length=150) #uses AES encryption or RSA encryption
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)

class MainClientInfo(models.Model):
    id = models.AutoField(primary_key=True)
    client_id = models.ForeignKey(Client,on_delete=models.CASCADE)
    client_info_id = models.ForeignKey(ClientInfo,on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now())
    modified = models.DateTimeField(default=timezone.now())

#class Poll(models.Model):
#   A poll object for use in the application views and repository.
#   text = models.CharField(max_length=200)
#   pub_date = models.DateTimeField('date published')

#    def total_votes(self):
#        #Calculates the total number of votes for this poll.
#        return self.choice_set.aggregate(Sum('votes'))['votes__sum']

#    def __unicode__(self):
#        #Returns a string representation of a poll.
#        return self.text

#class Choice(models.Model):
#    #A poll choice object for use in the application views and repository.
#    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
#    text = models.CharField(max_length=200)
#    votes = models.IntegerField(default=0)

#    def votes_percentage(self):
#        #Calculates the percentage of votes for this choice.
#        total=self.poll.total_votes()
#        return self.votes / float(total) * 100 if total > 0 else 0

#    def __unicode__(self):
#        #Returns a string representation of a choice.
#        return self.text