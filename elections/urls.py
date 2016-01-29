from django.conf.urls import url,include
from elections import views

urlpatterns = [
    url(r'^vote/$', views.VoterLogin , name = 'VoterLogin'),
    url(r'^vote/dashboard/$', views.VoterDashboard , name = 'VoterDashboard'),
    url(r'^create/$', views.CreateElection, name='CreateElection'),
    url(r'^(?P<election_slug>[\w-]+)/edit/$', views.EditElection,{'edit_id' : '1'},name='EditElectionDefault'),
    url(r'^(?P<election_slug>[\w-]+)/edit/(?P<edit_id>\d)/$', views.EditElection, name='EditElection'),
    url(r'^(?P<election_slug>[\w-]+)/questions/add/$', views.CreateQuestion,name='CreateQuestion'),
    url(r'^(?P<election_slug>[\w-]+)/questions/edit/(?P<question_id>\d+)/$', views.EditQuestion, name='EditQuestion'),
    url(r'^(?P<election_slug>[\w-]+)/activate/$', views.ActivateElection,name='ActivateElection'),
]