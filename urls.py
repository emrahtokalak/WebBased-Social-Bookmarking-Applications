# -*- coding: utf-8 -*-

from django.views.generic.simple import direct_to_template 
import os.path
from django.conf.urls.defaults import *
from LikedFeed.bookmarks.views import *
from LikedFeed.bookmarks.feeds import *

from django.contrib import admin
admin.autodiscover()

site_media = os.path.join(os.path.dirname(__file__), 'site_media')

feeds = {  'recent': RecentBookmarks,
           'user': UserBookmarks
            }
urlpatterns = patterns('',
                      #browsing, buradan altı..
                      (r'^$', main_page), 
                      (r'^user/(\w+)/$', user_page),
                      
                      # Auth olaylarının hepsi (neredeyse)
                      (r'^login/$', 'django.contrib.auth.views.login'),
                      (r'^logout/$', logout_page),
                      (r'^register/logged_out/$', direct_to_template,
                         { 'template': 'registration/logged_out.html' }),
                      (r'^register/$', register_page),
                      (r'^register/success/$', direct_to_template,
                         { 'template': 'registration/register_success.html' }),
                      (r'^password_change/$', 'django.contrib.auth.views.password_change'),
                      (r'^password_change/done/$', 'django.contrib.auth.views.password_change_done'),
                      (r'^password_reset/$', 'django.contrib.auth.views.password_reset'),
                      (r'^password_reset/done/$', 'django.contrib.auth.views.password_reset_done'),
                      (r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm'),
                      (r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete'),
                      ##Diğer site urlleri
                      
                      (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
                         { 'document_root': site_media }),
                      (r'^tag/([^\s]+)/$', tag_page),
                      (r'^tag/$', tag_cloud_page),
                      (r'^popular/$', popular_page),
                      (r'^bookmark/(\d+)/$', bookmark_page),
                      (r'^aboutus/$', aboutus),
                      (r'^tour/$', tour),
                      
                       #Hesap yönetimi..
                      (r'^save/$', bookmark_save_page),
                      (r'^delete/$', delete_own_bookmark),
                      (r'^search/$', search_page),
                      (r'^vote/$', bookmark_vote_page),
                      
                      # ajax ile ilgililer..
                      (r'^ajax/tag/autocomplete/$', ajax_tag_autocomplete),                      
                      
                      #Yorumlar için
                      (r'^comments/', include('django.contrib.comments.urls')), 
                  
                      
                      ## Arkadaşlık
                      (r'^friends/(\w+)/$', friends_page),
                      (r'^friend/add/$', friend_add),
                      (r'^friend/invite/$', friend_invite),
                      (r'^friend/accept/(w+)/$', friend_accept),
  
                      
                      
                      #admin arayüzü için urller..
                      (r'^yonetici/(.*)', admin.site.root),
                      
                      #Feeds beslemesi için..
                      
                      (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed',
                                                 {'feed_dict': feeds}),

                      
                      )
