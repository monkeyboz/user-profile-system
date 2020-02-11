import os

from django.http import HttpResponse, Http404
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from app.models import File,Client
import requests
import json

class FileHandler():
    def __init__(self,request,id=0,expert=False):
        self.request = request
        self.id = id
        self.filelist = []
        self.virusscanurl = 'https://www.virustotal.com/vtapi/v2/file/scan'
        self.scanreporturl = 'https://www.virustotal.com/vtapi/v2/file/report'
        self.params = {'apikey':'a1863c550dcecef277a9d0f9b1ae0dd596e53f760dfe4c5626f484baed968d1d'}

    #scan file for virus by placing in virus total queue
    def scanfileforvirus(self,filename,fullfilename):
        f = open(fullfilename,'rb')
        filestore = {'file':(str(filename),f)}
        response = requests.post(self.virusscanurl,files=filestore,params=self.params)
        return response.json()

    def scanallnonprocessed(self):
        return self.getReports()

    #upload file to media directory
    def uploadFile(self,file):
        file = self.request.FILES[file]
        fsys = FileSystemStorage()
        fullfilename = os.getcwd()+settings.MEDIA_DIR+str(self.id)+"\\"+file.name

        if os.path.isfile(fullfilename):
            fsys.delete(fullfilename)

        filename = fsys.save(fullfilename,file)

        upload_file_url = fsys.url(filename)
        scanned = self.scanfileforvirus(file,fullfilename)
        if scanned['response_code'] == 1:
            if len(File.objects.filter(path=fullfilename).values()) < 1:
                f = File()
                f.path = fullfilename
                f.virusscan_resource = scanned['resource']
                f.file_type = 't'
                f.client_id = Client.objects.filter(id=self.id)[0]
                f.save()
            else:
                self.getReports()
        else:
            print('deleted')
            fsys.delete(fullfilename)

    #get report for file in media directory
    def getReports(self):
        files = File.objects.exclude(virus__contains='total')
        print(len(files.values()))
        for a in files.values():
            params = self.params
            params['resource'] = a['virusscan_resource']
            v = requests.post(self.scanreporturl,params)
            if v.status_code == requests.codes.ok:
                m = v.json()
                if 'scan_date' in m:
                    #save file with virus definitions
                    f = File.objects.filter(virusscan_resource=m['resource'])
                    update = {}
                    update['virus'] = json.dumps(m)
                    update['scan_date'] = m['scan_date']
                    f.update(**update)
                else:
                    print(m)
            else:
                print(v)

    #download file from media directory
    def downloadFile(self,file,client_id):
        f = File.objects.filter(path__contains=file).values()
        if len(f) > 0:
            fullfilename = str(self.user_id)+"/"+file
            filestore = {'file':(file,open(fullfilename,'rb'))}
        
            self.filelist = filestore
            self.scanfileforvirus(file,fullfilename)

            if os.path.isfile(fullfilename):
                with open(fullfilename,'rb') as fh:
                    t = file.split('.')
                    extensions = {'png':'image',
                                  'jpg':'image',
                                  'jpeg':'image',
                                  'bmp':'image',
                                  'zip':'compressed-file',
                                  'bz':'compressed-file'}
                
                    response = HttpResponse(fh.read(),content_type=t[1]+'/'+extensions[t[1]])
                    response['Content-Disposition'] = 'inline; filename='+file
                    return response
        raise Http404