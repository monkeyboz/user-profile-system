"""
Definition of urls for polls viewing and voting.
"""

from django.urls import path
import app.views

urlpatterns = [
    path('',app.views.home,name='home'),
    #path('',
    #    app.views.PollListView.as_view(
    #        queryset=Poll.objects.order_by('-pub_date')[:5],
    #        context_object_name='latest_poll_list',
    #        template_name='app/index.html',),
    #    name='home'),
    #path('<int:pk>/',
    #    app.views.PollDetailView.as_view(
    #        template_name='app/details.html'),
    #    name='detail'),

    #path('users', app.views.getUsers , name='getuser'),
    #path('users/<int:id>', app.views.getUsers , name='getuserfromid'),
    #path('users/<int:id>/<int:start>', app.views.getUsers, name='getuserfromidstart'),
    #path('users/<int:id>/<int:start>/<int:limit>', app.views.getUsers , name='getusersfromidpagination'),
    #path('users/<int:start>/<int:limit>', app.views.getUsers , name='getusersfrompagination'),
    #path('users/<int:start>',app.views.getUsers,name='getusersfromstart'),

    #path('profile/<int:id>',app.views.getUsers,name='getuserprofile'),

    path('get/<str:object_name>',app.views.getObject,name='getobject'),
    path('get/<str:object_name>/<int:user_id>',app.views.getObject,name='getuserobject'),
    path('get/<str:object_name>/<str:user_id>/<int:start>',app.views.getObject,name='getuserobjectstart'),
    path('get/<str:object_name>/<str:user_id>/<int:start>/<int:limit>',app.views.getObject,name='getuserobjectspagination'),
    path('get/<str:object_name>/<int:id>',app.views.getObject,name='getobjectbyid'),
    path('get/<str:object_name>/<int:start>',app.views.getObject,name='getobjectbyidstart'),
    path('get/<str:object_name>/<int:start>/<int:limit>',app.views.getObject,name='getobjectbyidpagination'),
    path('get/<str:object_name>/<int:user_id>/<int:start>/<int:limit>',app.views.getObject,name='getobjectsstartlimit'),

    #put information into objects for storage on database
    path('put/<str:object_name>',app.views.putObject,name='putobject'), 
    path('put/<str:object_name>/<int:id>',app.views.putObject,name='putobjectuser'),
    path('put/<str:object_name>/<str:user_id>/<int:id>',app.views.putObject,name='putobjectuserid'),

    path('api/login',app.views.login,name='apilogin'),
    path('api/logout',app.views.logout,name='apilogout'),
    path('api/user/login',app.views.login,name='apilogin'),
    path('api/user/logout',app.views.logout,name='apilogout'),
    path('api/<str:object_name>',app.views.objectApi,name='apicall'),
    path('api/<str:object_name>/<int:id>',app.views.objectApi,name='apicallid'),
    path('api/<str:object_name>/<str:user_id>/<int:id>',app.views.objectApi,name='apicalluserid'),

    path('checkviruses',app.views.checkviruses,name='checkviruses'),
    path('download/<int:user_id>/<str:image>',app.views.download,name='download'),

    #path('get_file',app.views.getFile, name='getfile'),
    #path('<int:pk>/results/',
    #    app.views.PollResultsView.as_view(
    #        template_name='app/results.html'),
    #    name='results'),
    #path('<int:poll_id>/vote/', app.views.vote, name='vote'),
    path('seed',app.views.seed,name='seed'),
]
