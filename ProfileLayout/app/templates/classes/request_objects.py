from app.models import Client, ClientInfo, Position, File, Calendar
from django.http import HttpRequest, HttpResponseRedirect,HttpResponse, Http404
from django.db.models.options import Options
from django.shortcuts import get_object_or_404, render
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from app.templates.classes.file_handler import FileHandler
import hashlib

import os

class RequestObjects():
    def __init__(self,request,request_type,method,object_name=0,user_id=0,id=0,start=0,limit=0):
        assert isinstance(request,HttpRequest)

        self.method = method

        self.request = request
        self.login = self.checklogin()
        if self.login:
            self.initCompleted = self.completeInit(request_type,method,object_name,user_id,id,start,limit)
        else:
            self.initCompleted = self.completeInit(request_type,method,object_name,user_id,id,start,limit)
        
    #complete the initialization of RequestObjects
    def completeInit(self,request_type=0,method=0,object_name=0,user_id=0,id=0,start=0,limit=0):
        self.request_type = request_type
        self.client = ''
        self.clientinfo = ''
        
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
                            self.clientinfo = self.client[0].getClientInfo()
                            self.updateRecord()
                            self.uploadFiles()
                            return True
                else:
                    return False
            return True
        else:
            return False

    def getClient(self,api_key):
        self.client = Client.objects.filter(clientinfo__access_key=api_key)
        if len(self.client) > 0:
            return True
        else:
            return False

    #def updateRecord(self):
    #    if self.request.POST['password'] != None:                           
    #        if len(self.client) > 0:
    #            key = self.client[0].access_key
    #            cipher = AES.new(key,AES.MODE_GCM)
    #            ciphertext, tag = cipher.encrypt_and_digest(self.request.POST['password'].encode('UTF-8'))
    #            self.request.POST['password'] = ciphertext
    #
    #    uploadFiles()
    #
    #    if len(self.client) > 0:
    #        if self.id != 0:
    #            self.updateRecord()
    #        else:
    #            self.saveRecord()

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
            self.clientinfo = ClientInfo.objects.filter(access_key=self.request.POST['api_key'])
            return True
        else:
            if len(self.request.POST) > 0 and 'api_key' in self.request.POST:
                self.clientinfo = ClientInfo.objects.filter(access_key=self.request.POST['api_key'])
                if len(self.clientinfo) > 0:
                    self.request.session['api_result_key'] = hashlib.sha1(self.request.POST['api_key'].encode()).hexdigest()
                    self.request.session['user_id'] = self.clientinfo[0].client_id.id
                    return True
                return False
            else:
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
        if self.login == False or self.initCompleted == False:
            return render(
                    self.request,
                    'app/json.html'
                )
        object = self.query()

        if object != 0:
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
        if object != 0:
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

    #get request for object_type
    def getRequest(self):
        result = self.query()

        answer = render(self.request,'app/objects.html',{
                'objects':result['result'].values(),
                'length':len(list(result['result'].values())),
                'field_size':result['size']
            })

        return answer

    # get database object queries for the
    def display(self):
        # check variables being passed through GET
        if self.request_type == 'getobject':
            return self.getRequest()
        else:
            return self.postRequest()