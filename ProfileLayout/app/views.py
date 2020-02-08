"""
Definition of views.
"""

import json
import random
import hashlib
from faker import Faker
from django.core.serializers.json import DjangoJSONEncoder
import fileinput
from app.templates.classes.request_objects import RequestObjects
from app.templates.classes.file_handler import FileHandler
from os import path
from os import urandom
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.generic import ListView, DetailView
from app.models import Client, ClientInfo, PositionInfo, Position, File, Calendar
from django.views.decorators.csrf import csrf_exempt
from django import template

def home(request):
    return render(
        request,
        'app/index.html'
        )

def GetFile(request):
    assert isinstance(request,HttpRequest)
    return render(
        request,
        'app/index.html'
        )

def getObject(request,object_name=0,user_id=0,id=0,start=0,limit=0):
    get = RequestObjects(request,"getobject","GET",object_name,user_id,id,start,limit)
    return get.display()

def login(request):
    assert isinstance(request,HttpRequest)
    if 'sessionid' in request.session:
        print(request.session.get('sessionid'))
        return False
    else:
        return True

@csrf_exempt
def objectApi(request,object_name=0,user_id=0,id=0):
    put = RequestObjects(request,'api','POST',object_name,user_id,id)
    return put.response()

def download(request,user_id=0,image=0,expert=0):
    d = FileHandler(request)
    return d.downloadFile(image,user_id)

def putObject(request,object_name=0,user_id=0,id=0):
    put = RequestObjects(request,"putobject","POST",object_name,user_id,id)
    request = isinstance(request,HttpRequest)
    print(put.display())
    if put.display() == None:
        return render(
                put.request,
                'app/index.html'
            )
    return put.display()

#class PollListView(ListView):
#    """Renders the home page, with a list of all polls."""
#    model = Poll

#    def get_context_data(self, **kwargs):
#        context = super(PollListView, self).get_context_data(**kwargs)
#        context['title'] = 'Polls'
#        context['year'] = datetime.now().year
#        return context

class UserDetailView(DetailView):
    model = Client.objects.all()[:1]

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        context['title'] = 'Client'
        context['year'] = datetime.now().year
        return context

#class PollDetailView(DetailView):
#    Renders the poll details page."""
#    model = Poll

#    def get_context_data(self, **kwargs):
#        context = super(PollDetailView, self).get_context_data(**kwargs)
#        context['title'] = 'Poll'
#        context['year'] = datetime.now().year
#        return context

#class PollResultsView(DetailView):
#    Renders the results page."""
#    model = Poll

#    def get_context_data(self, **kwargs):
#        context = super(PollResultsView, self).get_context_data(**kwargs)
#        context['title'] = 'Results'
#        context['year'] = datetime.now().year
#        return context

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )

#def vote(request, poll_id):
#    """Handles voting. Validates input and updates the repository."""
#    poll = get_object_or_404(Poll, pk=poll_id)
#    try:
##        selected_choice = poll.choice_set.get(pk=request.POST['choice'])
#    except (KeyError, Choice.DoesNotExist):
#       return render(request, 'app/details.html', {
#            'title': 'Poll',
#           'year': datetime.now().year,
#            'poll': poll,
#            'error_message': "Please make a selection.",
#    })
#    else:
#        selected_choice.votes += 1
#        selected_choice.save()
#        return HttpResponseRedirect(reverse('app:results', args=(poll.id,)))

@login_required
def seed(request):
    """Seeds the database with sample polls."""
    #samples_path = path.join(path.dirname(__file__), 'samples.json')
    #with open(samples_path, 'r') as samples_file:
    #    samples_polls = json.load(samples_file)

    #for sample_poll in samples_polls:
    #    poll = Poll()
    #    poll.text = sample_poll['text']
    #    poll.pub_date = timezone.now()
    #    poll.save()

    #    for sample_choice in sample_poll['choices']:
    #        choice = Choice()
    #        choice.poll = poll
    #        choice.text = sample_choice
    #        choice.votes = 0
    #        choice.save()
    
    fake = Faker()
    #for i in range(10,100):
    #    RandomPosition(fake)
    #for a in range(0,random.randrange(4,10)):
    #    RandomClient(fake)
    for b in range(1,random.randrange(5,10)):
        RandomClientInfo(fake)
    return HttpResponseRedirect(reverse('app:home'))

def RandomPosition(faker):
    position = Position()

    latln = faker.location_on_land(coords_only=False)

    position.location = latln[0]+','+latln[1]
    position.save()

    positioninfo = PositionInfo()
    positioninfo.city = latln[2]
    positioninfo.country = latln[3]
    positioninfo.state = latln[4].split('/')[1]
    positioninfo.created = faker.date_object()
    positioninfo.position_id = position
    positioninfo.save()

def RandomClientInfo(faker):
    clientinfo = ClientInfo()
    profile = faker.profile()
    clientinfo.address = profile['address']
    clientinfo.created = faker.date_object()
    first_name = faker.first_name_male()
    last_name = faker.last_name_male()
    if random.randrange(1,2):
        first_name = faker.first_name_female()
        last_name = faker.last_name_female()

    clientinfo.firstname = first_name
    clientinfo.lastname = last_name
    clientsize = Client.objects.all().count()
    names = []
    for i in range(1,10):
        names.append(faker.first_name_male())

    names = names[random.randrange(0,len(names))]
    clientinfo.access_key = hashlib.sha1((clientinfo.firstname+clientinfo.lastname+names).encode())
    clientinfo.access_key = clientinfo.access_key.hexdigest()
    clientinfo.client_id = Client.objects.filter(pk=random.randrange(1,clientsize))[0]
    count = PositionInfo.objects.all().count()
    clientinfo.position_info = PositionInfo.objects.filter(pk=random.randrange(1,count))[0]
    clientinfo.save()

def RandomClient(faker):
    client = Client()
    sex = 'male'
    active = True
    if random.randrange(1,2) == 1:
        sex = 'female'
    if random.randrange(1,10) == 1:
        active = False
    profile = faker.profile(fields=['username','password','mail','address'],sex=sex)
    client.username = profile['username']
    client.email = profile['mail']
    client.password = faker.md5(raw_output=False)
    client.active = active
    client.created = faker.date_object()
    client.save()
