# -*- coding: utf-8 -*-
from django.db import models
class Link(models.Model):
  url = models.URLField(unique=True)
  def __unicode__(self):                      #eski django sürümlerinde __str__ kullanılıyormuş.
  	 return '%s, %s' % (self.user.username, self.link.url)
  class Admin:
  	 list_display = ('title', 'link','user')
  	 list_filter = ('user', )       #kullanıcının bookmarkları filtreleyebilmesi için
  	 ordering = ('title', )         #başlıkları sıralayabilmesi için..
  	 search_fields = ('title', )    #başlığa göre bookmark araması yapabilmesi için.
  	 
from django.contrib.auth.models import User
class Bookmark(models.Model):
   title = models.CharField (max_length=200)
   user = models.ForeignKey (User)
   link = models.ForeignKey (Link) 
   def __str__(self):
		return '%s, %s' % (self.user.username, self.link.url)
   def get_absolute_url(self):
      return self.link.url
   
class Tag(models.Model):
   name = models.CharField(max_length=64, unique=True)
   bookmarks = models.ManyToManyField(Bookmark)
   def __str__(self):
     return self.name
     
class SharedBookmark(models.Model):
	bookmark = models.ForeignKey(Bookmark, unique= True)
	date = models.DateTimeField(auto_now_add=True)
	votes = models.IntegerField(default=1)
	users_voted = models.ManyToManyField(User)
	def __str__(self):
		return '%s, %s' % self.bookmark, self.votes
        
        
class Friendship(models.Model):
    from_friend = models.ForeignKey(
        User, related_name='friend_set'
        )
    to_friend = models.ForeignKey(
        User, related_name='to_friend_set'
        )
    def __unicode__(self):
        return u'%s, %s' % (
            self.from_friend.username,
            self.to_friend.username
        )
    class Admin:
        pass
    class Meta:
        unique_together = (('to_friend', 'from_friend'), )
    class Meta: 
      permissions = (
        ('can_list_friend_bookmarks',
         'Can list friend bookmarks'),
      )



from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context
from django.conf import settings

class Invitation(models.Model):
  name = models.CharField(max_length=50)
  email = models.EmailField()
  code = models.CharField(max_length=20)
  sender = models.ForeignKey(User)

  def __unicode__(self):
    return u'%s, %s' % (self.sender.username, self.email)
  class Admin:
        pass
  def send(self):
    subject = u'LikedFeed katılın'
    link = 'http://%s/friend/accept/%s/' % (
      settings.SITE_HOST,
      self.code
    )
    template = get_template('davetiye_mail.txt')
    context = Context({
      'name': self.name,
      'link': link,
      'sender': self.sender.username,
    })
    message = template.render(context)
    send_mail(
      subject, message,
      settings.DEFAULT_FROM_EMAIL, [self.email]
    )
   