"""
Customizations for the Django administration interface.
"""
from django.contrib import admin
from django.db import models
from app.models import Client, ClientInfo, CalendarFile, Calendar, Position, File, PositionInfo

from django.forms.models import modelformset_factory, inlineformset_factory
from django.template.defaultfilters import escape
from django.utils.html import format_html
from django.urls import reverse
from django import forms

#class ChoiceInline(admin.TabularInline):
    #Choice objects can be edited inline in the Poll editor."""
    #model = Choice
    #extra = 3

#class PollAdmin(admin.ModelAdmin):
    #Definition of the Poll editor."""
    #fieldsets = [
    #    (None, {'fields': ['text']}),
    #    ('Date information', {'fields': ['pub_date']}),
    #]
    #inlines = [ChoiceInline]
    #list_display = ('text', 'pub_date')
    #list_filter = ['pub_date']
    #search_fields = ['text']
    #date_hierarchy = 'pub_date'

class ClientAdmin(admin.ModelAdmin):    
    list_display = ('username','id')
    list_filter = ['username']
    search_fields = ['username']
    char_hierarchy = 'username'

class CalendarAdmin(admin.ModelAdmin):
    def getclient(self,obj):
        return obj.client_id.username
    
    getclient.short_description = 'Client Name'
    list_display = ('date','time','calendar_duration','getclient')
    list_filter = ['client_id','date']
    search_field = ['date']
    date_hierarchy = 'date'

class PositionAdmin(admin.ModelAdmin):
    list_display = ('id','getlatlon')
    
    def getdate(self,obj):
        return obj.calendar_id.date
    def getclient(self,obj):
        return format_html('<a href="%s">%s</a>' % (reverse('admin/app/client/{0}/change'.format(obj.calendar_id.id),args=(obj.calendar_id.client_id.id,)),escape(obj.calendar_id.client_id.username)))

    def getlatlon(self,obj):
        ltln = obj.location.split(',')
        return 'lat: {}, lon: {}'.format(ltln[0],ltln[1])
    getlatlon.short_description = 'Lat Lon'
    getclient.short_description = 'Client Name'
    
class FileAdmin(admin.ModelAdmin):
    list_display = ('id','getfilename','getusername','gettype')

    def getfilename(self,obj):
        return obj.path

    def getusername(self,obj):
        return obj.client_id.username

    def gettype(self,obj):
        type = {'c':'calendar','t':'temporary','p':'permenant'}
        return type[obj.file_type]

    getfilename.short_description = 'Filename'
    getusername.short_description = 'Username'
    gettype.short_description = 'Type'

class PositionInline(admin.TabularInline):
    model = Position

#class PositionClientInfoForm(forms.ModelForm):
    #firstname = models.CharField(max_length=200)
    #lastname = models.CharField(max_length=200)
    #address = models.CharField(max_length=200)

class ClientInfoAdmin(admin.ModelAdmin):
    list_display = ('id','getusername','getname','getpositioninfo')
    
    def getusername(self,obj):
        return obj.client_id.username
        
    def getname(self,obj):
        return obj.firstname+" "+obj.lastname

    def getpositioninfo(self,obj):
        return obj.position_info.address()
    
    getpositioninfo.short_description = 'Position Info'
    getusername.short_description = 'Username'
    getname.short_description = 'Name'

class PositionInfoAdmin(admin.ModelAdmin):
    list_display = ('id','country','city','state','zip')

class ClientFileAdmin(admin.ModelAdmin):
    list_display = ('getcalendar','getfile')

    def getcalendar(self,obj):
        return obj.calendar_id.name

    def getfile(self,obj):
        return obj.file_id.path

#admin.site.register(Poll, PollAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Calendar,CalendarAdmin)
admin.site.register(Position,PositionAdmin)
admin.site.register(PositionInfo,PositionInfoAdmin)
admin.site.register(ClientInfo,ClientInfoAdmin)
admin.site.register(File,FileAdmin)
admin.site.register(CalendarFile,ClientFileAdmin)
