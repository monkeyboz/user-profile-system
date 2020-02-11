from app.models import Client, ClientInfo, MainClientInfo, Position, File, Calendar
from django.http import HttpRequest, HttpResponseRedirect,HttpResponse, Http404
from django.db.models.options import Options
from django.shortcuts import get_object_or_404, render
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from app.templates.classes.file_handler import FileHandler
from django.core.serializers.json import DjangoJSONEncoder

import hashlib
import os
import json

#Request Object for getting information from url calls
class RequestObjects():
    def __init__(self,request,request_type,method,logout=0,object_name=0,user_id=0,id=0,start=0,limit=0):
        assert isinstance(request,HttpRequest)
        #set client and mainclientinfo objects for retreiving information
        self.client = None;
        self.mainclientinfo = None;

        #check if logout is selected
        if logout == 1:
            self.request = request
            self.logout()
            self.initCompleted = self.completeInit()
        else:
            self.method = method

            self.request = request
            self.login = self.checklogin()
            if self.login:
                self.initCompleted = self.completeInit(request_type,method,object_name,user_id,id,start,limit)
    
    #Get Api Key
    def getApiKey(self):
        if 'api_result_key' in self.request.session:
            return render(
                    self.request,
                    'app/objects_bk.html',
                    {
                        'objects':list(self.mainclientinfo.values())
                    }
                )
        else:
            return render(
                    self.request,
                    'app/json.html',
                    {
                        'object':'is not logged-in',
                        'id':'0',
                        'response':'OK'
                    }
                )

    #Get Login Results (returns object)
    def getLoginResult(self):
        if self.mainclientinfo != None and self.client != None:
            return render(
                    self.request,
                    'app/objects_bk.html',
                    {
                        'objects':list(self.mainclientinfo.values())
                    }
                )
        else:
            return render(
                    self.request,
                    'app/json.html'
                )

    #Get Request Object
    def getRequestObject(self):
        return self.request

    #Log out
    def logout(self):
        del self.request.session
        return True

    #complete the initialization of RequestObjects
    def completeInit(self,request_type=0,method=0,object_name=0,user_id=0,id=0,start=0,limit=0):
        self.request_type = request_type
        
        self.object_name = self.checkVariable(object_name)
        self.user_id = self.checkVariable(user_id)
        self.id = self.checkVariable(id)
        self.start = self.checkVariable(start)
        self.limit = self.checkVariable(limit)

        if self.request_type != 'getobject':
            if self.request_type == 'api':
                if 'api_type' in self.request.POST:
                    self.request_type = self.request.POST['api_type']
                    return self.checkPost()
                else:
                    self.request_type = 'null'
                    return False
            else:
                return self.checkPost()

    #check post for information and get client information
    def checkPost(self):
        if len(self.request.POST) > 0:
            if self.object_name == 'client' or self.object_name == 'user':
                if self.request.POST['api_key'] != None:
                    if self.getClient(self.request.POST['api_key']):
                        if len(self.client) > 0:
                            self.mainclientinfo = self.client[0].getMainClientInfo()
                            self.updateRecord()
                            self.uploadFiles()
                            return True
                else:
                    return False
            return True
        else:
            return False

    #Get client information
    def getClient(self,api_key):
        self.client = Client.objects.filter(clientinfo__access_key=api_key)
        if len(self.client) > 0:
            return True
        else:
            return False

    #upload files to media directory
    def uploadFiles(self):
        if self.request.FILES != None and len(self.request.FILES) > 0:
            id = self.id
            if self.user_id != 0:
                id = self.user_id
            filehandler = FileHandler(self.request,id)
            for a in self.request.FILES:
                filehandler.uploadFile(a)
    
    #check if user is logged in
    def checklogin(self):
        if 'api_result_key' in self.request.session:
            if 'api_key' in self.request.POST:
                self.mainclientinfo = MainClientInfo.objects.filter(client_info_id__access_key=self.request.POST['api_key'])
                if len(self.mainclientinfo.values()) > 0:
                    self.client = Client.objects.get(pk=self.mainclientinfo[0].client_id.id)
                    return True
                else:
                    return False
            else:
                self.mainclientinfo = MainClientInfo.objects.filter(client_id=self.request.session['user_id'])
                if len(self.mainclientinfo.values()) > 0:
                    self.client = Client.objects.get(pk=self.mainclientinfo[0].client_id.id)
                return False
        else:
            if len(self.request.POST) > 0 and ('api_key' in self.request.POST and 'password' in self.request.POST and 'username' in self.request.POST) or ('password' in self.request.POST and 'username' in self.request.POST):
                self.client = Client.objects.filter(password=self.request.POST['password'])
                if len(self.client.values()):
                    self.mainclientinfo = MainClientInfo.objects.filter(client_id=self.client.values()[0]['id'])
                    if len(self.mainclientinfo) > 0:
                        if('api_key' in self.request.POST and self.request.POST['api_key'] == self.mainclientinfo[0].client_info_id.access_key):
                            self.request.session['api_result_key'] = hashlib.sha1(self.request.POST['api_key'].encode()).hexdigest()
                            #self.request.session['user_id'] = self.mainclientinfo[0].client_id.id
                            print('session_started: '+self.request.session['api_result_key'])
                            return True
                        else:
                            self.request.session['api_result_key'] = hashlib.sha1(self.mainclientinfo[0].client_info_id.access_key.encode()).hexdigest()
                            #self.request.session['user_id'] = self
                            print('session_started_with_new_api_key: '+self.mainclientinfo[0].client_info_id.access_key)
                            return True
                    else:
                        print('cannot find user')
                else:
                    print('cannot login')
                return False
            else:
                print('No way to login')
                return False

    #save record for database
    def saveRecord(self):
        classObj = self.initModel(self.object_name)
        for a in self.request.POST:
            if hasattr(classObj,a):
                setattr(classObj,a,self.request.POST[a])

        obj = self.getObject(self.object_name)
        result = self.query()

        if result['result'].count() > 0:
            self.updateRecord()
        else:
            classObj.save()

    #update record for database
    def updateRecord(self):
        if self.id != 0:
            classObj = self.initModel(self.object_name)
            update = {};
            for a in self.request.POST:
                if hasattr(classObj,a):
                    update[a] = self.request.POST[a]
            self.query()['result'].update(**update)

    #check variables
    def checkVariable(self,object_name):
        test = 0
        try:
            if object_name == None: 
                test = 0
            else:
                test = object_name
        except NameError:
            test = 0
        return test

    #initalize object_type model reference for record creation
    def initModel(self,obj):
        if obj == 'calendar':
            return Calendar()
        elif obj == 'file':
            return File()
        elif obj == 'position':
            return Position()
        elif obj == 'client' or obj == 'user':
            return Client()
        else:
            return 0

    #get object for querying
    def getObject(self,obj):
        objclass = {}
        if obj == 'calendar' or obj == 'calendars':
            objclass['class'] = Calendar
            objclass['name'] = 'calendars'
            objclass['user_id'] = 'client_id'
            objclass['template'] = 'app/calendar.html'
            objclass['size'] = len(Calendar._meta.fields)
        elif obj == 'file':
            objclass['class'] = File
            objclass['name'] = 'filess'
            objclass['user_id'] = 'client_id' 
            objclass['template'] = 'app/file.html'
            objclass['size'] = len(File._meta.fields)
        elif obj == 'position':
            objclass['class'] = Position
            objclass['name'] = 'position'
            objclass['user_id'] = 'calendar_id'
            objclass['template'] = 'app/position.html'
            objclass['size'] = len(Position._meta.fields)
        elif obj == 'user' or obj == 'users':
            objclass['class'] = Client
            objclass['name'] = 'clients'
            objclass['user_id'] = 'id'
            objclass['template'] = 'app/client.html'
            objclass['size'] = len(Client._meta.fields)
        else:
            objclass = 0

        return objclass

    #get a response from the query search
    def response(self):
        #checks to make sure that all variables are initalized
        if self.login == False or self.initCompleted == False:
            return render(
                    self.request,
                    'app/json.html'
                )
        object = self.query()

        if object != None:
            result = object['result']
            return render(
                self.request,
                'app/json.html',
                {
                    'response' : 'OK',
                    'object' : str(list(result.values())).replace("'",'"'),
                    'id' : self.user_id
                }
            )
        else:
            return render(
                    self.request,
                    'app/json.html',
                    {
                        'response':'Not OK',
                        'object': "{ }",
                        'id': 'null'
                    }
                )

    #post request response
    def postRequest(self):
        object = self.query()
        if object != 0 or object != None:
            result = object['result']
            id = object['user_id']
            return render(
                self.request,
                'app/form.html',
                {
                    'response':'OK',
                    'content':result.values(),
                    'id':id
                }
            )
        else:
            return object

    #query object for search
    def query(self):
        if hasattr(self,'object_name'):
            object = self.getObject(self.object_name)
            if object == 0:
                return object
            my_filter = {}
            if self.user_id != 0:
                my_filter[object['user_id']] = self.user_id
            
            if self.id != 0:
                my_filter['id'] = self.id
        
            if len(my_filter) > 0:
                if self.limit != 0 and self.start != 0:
                    l = object['class'].objects.filter(**my_filter)[self.start-1:self.limit]
                elif(self.limit == 0 and self.start != 0):
                    l = object['class'].objects.filter(**my_filter)[self.start-1:]
                elif(self.limit != 0 and self.start == 0):
                    l = object['class'].objects.filter(**my_filter)[:self.limit]
                else:
                    l = object['class'].objects.filter(**my_filter)
            else:
                if self.limit != 0 and self.start != 0:
                    l = object['class'].objects.all()[self.start-1:self.limit]
                elif(self.limit == 0 and self.start != 0):
                    l = object['class'].objects.all()[self.start-1:]
                elif(self.limit != 0 and self.start == 0):
                    l = object['class'].objects.all()[:self.limit]
                else:
                    l = object['class'].objects.all()

            object['result'] = l
            return object
        else:
            print('no object_name')
            return None

    #get request for object_type
    def getRequest(self):
        result = self.query()  #returns None if it is completed without an object

        if result != None:
            answer = render(self.request,'app/objects_bk.html',{
                    'objects':result['result'].list()
                })
        else:
            answer = render(
                    self.request,
                    'app/json.html',
                    {
                        'id':'null',
                        'object':'No object type',
                        'response':'OK'
                    }
                )

        return answer

    # get database object queries for the
    def display(self):
        # check variables being passed through GET
        if self.request_type == 'getobject':
            return self.getRequest()
        else:
            return self.postRequest()