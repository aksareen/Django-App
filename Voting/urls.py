from django.conf.urls import patterns, include, url
from django.contrib import admin
from Voting import views
from django.contrib.auth import views as auth_views

urlpatterns = patterns('',  
    url(r'^$', views.homepage , name = 'homepage'),
    url(r'^login/$',views.user_login, name = 'user_login'),
    url(r'^logout/$', views.user_logout, name='user_logout'),
    url(r'^contact/$',views.contact_us, name = 'contact_us'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^users/', include('users.urls' , namespace="users")),
    url(r'^elections/', include('elections.urls' , namespace="elections")),
    url(r'^admin/password_reset/$', auth_views.password_reset, name='admin_password_reset'),
    url(r'^admin/password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
    url(r'^set/$',views.set_timezone,name='set_timezone'),

)
