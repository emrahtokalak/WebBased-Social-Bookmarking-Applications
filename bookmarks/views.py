# -*- coding: utf-8 -*-
# Emrah Tokalak emrah@alemgir.com
# Anlamaya yardımcı olucak bir kaç yorum eklemeye çalıştım.

from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.template import RequestContext
def main_page(request):
	shared_bookmarks = SharedBookmark.objects.order_by(
	  '-date'
	)[:20]
	variables = RequestContext(request, {
	  'shared_bookmarks': shared_bookmarks
	})
        return render_to_response(
          'main_page.html', variables
         )
    
from django.http import HttpResponse, Http404
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from LikedFeed.helpers import EasyPagination

def user_page(request, username):
  user = get_object_or_404(User, username=username)
  bookmarks = user.bookmark_set.order_by('-id')
  paged_data = EasyPagination(request, bookmarks, 15) 
  if request.user.is_authenticated():
    is_friend = Friendship.objects.filter(
            from_friend=request.user,
            to_friend=user
    )
  else:
    is_friend = False
  
  variables = RequestContext(request, {
        'bookmarks':bookmarks,  
        'username': username,
        'show_tags': True,
        'show_edit': username == request.user.username,
        'show_delete': username == request.user.username,
        'is_friend': is_friend
        
  })
  return render_to_response('user_page.html',variables)
  
from django.http import HttpResponseRedirect
from django.contrib.auth import logout
def logout_page(request):
  logout(request)
  return HttpResponseRedirect('/register/logged_out/')
  

 
def aboutus(request):
  return render_to_response(
       'aboutus.html', request) 


def tour(request):
  return render_to_response(
       'tour.html', request ) 
  
from LikedFeed.bookmarks.forms import *
def register_page(request):
  if request.method == 'POST':
     form = RegistrationForm(request.POST)
     if form.is_valid():
       user = User.objects.create_user(
         username=form.cleaned_data['username'],
         password=form.cleaned_data['password1'],
         email=form.cleaned_data['email']
       )
       if 'invitation' in request.session:
             #kişi invite ile gelirse onu arkadaş olarak ekliyoruz.
        invitation = Invitation.objects.get(
          id=request.session['invitation']
        )
        
        friendship = Friendship(
          from_friend=user,
          to_friend=invitation.sender
        )
        friendship.save()
        
        friendship = Friendship (
          from_friend=invitation.sender,
          to_friend=user
        )
        friendship.save()
        # davetiyeyide db den siliyoruz
        invitation.delete()
        del request.session['invitation']
     return HttpResponseRedirect('/register/success/')
  else:
       form = RegistrationForm()
  variables = RequestContext(request, {
          'form': form 
  })
  return render_to_response(
       'registration/register.html', variables ) 


         
from LikedFeed.bookmarks.models import *         
from django.contrib.auth.decorators import login_required  
from django.core.exceptions import ObjectDoesNotExist       
@login_required
def delete_own_bookmark(request, id):
     yerimi = Bookmark.objects.get(pk = id)
     yerimi.delete()
     return HttpResponseRedirect('bookmark_list.html')

         
         
         
         
         
         
from LikedFeed.bookmarks.models import *
from django.contrib.auth.decorators import permission_required       
#login required yerine artık permission_required kullanıyorum. hem yönlendirme özelliğide var.
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required  
@login_required
def bookmark_save_page(request):
  ajax = request.GET.has_key('ajax')
  if request.method == 'POST':
      form = BookmarkSaveForm(request.POST)
      if form.is_valid():
         bookmark = _bookmark_save(request, form)
         if ajax:
	    variables = RequestContext(request, {
	      'bookmarks': [bookmark],
	      'show_edit': True,
	      'show_tags': True
	      })
	    return render_to_response('bookmark_list.html', variables)
	 else:
	   return HttpResponseRedirect(
	      '/user/%s' % request.user.username
	      )
      else:
	if ajax:
	  return HttpResponse('failure')
	  
  elif request.GET.has_key('url'):
  	 url = request.GET['url']
  	 title = ''
  	 tags = ''
  	 try:
  	 	 link = Link.objects.get(url=url)
  	 	 bookmark = Bookmark.objects.get(
  	 	    link=Link,
  	 	    user=request.user
  	 	 )
  	 	 title = bookmark.title
  	 	 tags = ' '.join(tag.name for tag in bookmark.tag_set.all())
         except:
          pass
         form = BookmarkSaveForm({
            'url': url,
            'title': title,
            'tags': tags
         })
     
  else:
      form = BookmarkSaveForm()
  variables = RequestContext(request, {
         'form': form
    })
  if ajax:
    return render_to_response(
       'bookmark_save_form.html',
        variables
    )
  else:
    return render_to_response(
      'bookmark_save.html',
      variables
    )

def tag_page(request, tag_name):
  tag = get_object_or_404(Tag, name=tag_name)
  bookmarks = tag.bookmarks.order_by('-id')
  variables = RequestContext(request, {
    'bookmarks': bookmarks,
    'tag_name': tag_name,
    'show_tags': True,
    'show_user': True
  })
  return render_to_response('tag_page.html', variables)
        
        
def tag_cloud_page(request):
  MAX_WEIGHT = 5
  tags = Tag.objects.order_by('name')
  # Etiketleri hesaplama, minimum maksimum filan..
  min_count = max_count = tags[0].bookmarks.count()
  for tag in tags:
    tag.count = tag.bookmarks.count()
    if tag.count < min_count:
      min_count = tag.count
    if max_count < tag.count:
      max_count = tag.count
  # etiket aralığı range'i hesaplama. sıfıra bölerek hesaplıyorum.
  range = float(max_count - min_count)
  if range == 0.0:
    range = 1.0
  # etiket ağırlıgını hesaplama
  for tag in tags:
    tag.weigth = int(
      5 * (tag.count - min_count) / range
    )
  variables = RequestContext(request, {
    'tags': tags
  })
  return render_to_response('tag_cloud_page.html', variables)  

from django.db.models import Q  
def search_page(request):
  form = SearchForm()
  bookmarks = []
  show_results = False
  if request.GET.has_key('query'):
    show_results = True
    query = request.GET['query'].strip()
    if query:
       keywords = query.split()
       q = Q()
       for keyword in keywords:
       	 q = q & Q(title__icontains=keyword)
       form = SearchForm({'query' : query})
       bookmarks = Bookmark.objects.filter(q) [:10]
  variables = RequestContext(request, { 'form': form,
     'form': form,     
     'bookmarks': bookmarks,
     'show_results': show_results,
     'show_tags': True,
     'show_user': True
    })
  if request.GET.has_key('ajax'):
       return render_to_response('bookmark_list.html', variables)
  else:
       return render_to_response('search.html', variables)
  
def _bookmark_save(request, form):
  #oluştur 
  link, dummy = \
    Link.objects.get_or_create(url=form.cleaned_data['url'])
  #bookmark oluştur yada get ile çek
  bookmark, created = Bookmark.objects.get_or_create(
    user=request.user,
    link=link
  )
  #başlığı güncelle update
  bookmark.title = form.cleaned_data['title']
  #bookmark güncellendikten sonra eski etiketleri sil..
  if not created:
  	 bookmark.tag_set.clear()
  #yeni tag list oluştur.
  tag_names = form.cleaned_data['tags'].split()
  for tag_name in tag_names:
    tag, dummy = Tag.objects.get_or_create(name=tag_name)
    bookmark.tag_set.add(tag)
  #İstek Gelirse anasayfada paylaş
  if form.cleaned_data['share']:
  	 shared_bookmark, created = SharedBookmark.objects.get_or_create(
  	   bookmark=bookmark
  	 )
  	 if created:
  	 	shared_bookmark.users_voted.add(request.user)
  	 	shared_bookmark.save()
  	 	  
  # yerimlerini db ye kaydet ve tekrarla.
   
  bookmark.save()
  return bookmark

def ajax_tag_autocomplete(request):
   if request.GET.has_key('q'):
    tags = \
	Tag.objects.filter(name__istartswith=request.GET['q'])[:10]
    return HttpResponse('\n'.join(tag.name for tag in tags))
   return HttpResponse()


from django.contrib.auth.decorators import login_required  
@login_required 

def bookmark_vote_page(request):
	if request.GET.has_key('id'):
		try:
		    id = request.GET['id']
		    shared_bookmark = SharedBookmark.objects.get(id=id)
		    user_voted = shared_bookmark.users_voted.filter(username=request.user.username)
		    if not user_voted:
			shared_bookmark.votes += 1
			shared_bookmark.users_voted.add(request.user)
			shared_bookmark.save()
		except ObjectDoesNotExist:
	          raise Http404('Yerimi bulunamadı!')
	if request.META.has_key('HTTP_REFERER'):
		return HttpResponseRedirect(request.META['HTTP_REFERER'])
	return HttpResponseRedirect('/')
	

from datetime import datetime, timedelta
def popular_page(request):
	today = datetime.today()
	yesterday = today - timedelta(1)
	shared_bookmarks = SharedBookmark.objects.filter(
		date__gt=yesterday
	)
	shared_bookmarks = shared_bookmarks.order_by(
		'-votes'
	
	)[:10]
	variables = RequestContext(request, {
		'shared_bookmarks': shared_bookmarks
	})
	return render_to_response('popular_page.html', variables)

def bookmark_page(request, bookmark_id):
	shared_bookmark = get_object_or_404(
	  SharedBookmark,
	  id=bookmark_id
	)
	variables = RequestContext(request, {
		'shared_bookmark': shared_bookmark
	})
	return render_to_response('bookmark_page.html', variables)

	
from django.contrib.syndication.feeds import Feed
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
class UserBookmarks(Feed):
	def get_object(self, bits):
		if len(bits) !=1:
			raise ObjectDoesNotExist
		return User.objects.get(username=bits[0])
	def title(self, user):
		return 'LikedFeed | Kullanıcının yerimleri %s' % user.username  
	def link(self, user):
		return '/feeds/user/%s/' % user.username
	def description(self, user):
		return 'Son paylaşımı yapan  %s' % user.username
	def items(self, user):
		return user.bookmark_set.order_by('-id')[:10]
        
### arkadaşlık sistemi

def friends_page(request, username):
  user = get_object_or_404(User, username=username)
  friends = [friendship.to_friend
             for friendship in user.friend_set.all()]
  friend_bookmarks = Bookmark.objects.filter(
    user__in=friends
  ).order_by('-id')
  variables = RequestContext(request, {
    'username': username,
    'friends': friends,
    'bookmarks': friend_bookmarks[:10],
    'show_tags': True,
    'show_user': True
  })
  return render_to_response('friends_page.html', variables)

from LikedFeed.bookmarks.models import *
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required  
@login_required
def friend_add(request):
  if 'username' in request.GET:
    friend = get_object_or_404(
      User, username=request.GET.get['username']
    )
    friendship = Friendship(
      from_friend=request.user,
      to_friend=friend
    )
    try:
      friendship.save()
      request.user.message_set.create(
        message=u'%s arkadaş listene eklendi.' %
          friend.username
      ) 
    except:
      request.user.message_set.create(
        message=u'%s ile zaten arkadaşsnınız.' %
          friend.username
      )
   
    return HttpResponseRedirect(
      '/friends/%s/' % request.user.username
    )
  else:
    raise Http404


from LikedFeed.bookmarks.forms import FriendInviteForm
import smtplib         #yeni versiyonda sanırım bu değişicek..
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required  
@login_required
def friend_invite(request):
  if request.method == 'POST':
    form = FriendInviteForm(request.POST)
    if form.is_valid():
      invitation = Invitation(
        name=form.cleaned_data['name'],
        email=form.cleaned_data['email'],
        code=User.objects.make_random_password(20),
        sender=request.user
      )
      invitation.save()
      try:
        invitation.send()
        request.user.message_set.create(
          message=u'davetiye gönderildi %s.' %
           invitation.email
        )
      except smtplib.SMTPException:
        request.user.message_set.create(
          message=u'Davetiyeyi gönderirken '
            u'bir hata oluştu.'
        )
      return HttpResponseRedirect('/friend/invite/')
  else:
    form = FriendInviteForm()

  variables = RequestContext(request, {
    'form': form
  })
  return render_to_response('friend_invite.html', variables)
  
  
def friend_accept(request, code):
  invitation = get_object_or_404(Invitation, code__exact=code)
  request.session['invitation'] = invitation.id                            ## eğer kişi kabul koduyla gelirse
  return HttpResponseRedirect('/register/')                                 ## register sayfasına yönlendiriyoruz
	
	
	
	
	##############################auth için olanlar aldığımın seettirilmiş halleri##############################333
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.sites.models import Site, RequestSite
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.utils.http import urlquote, base36_to_int
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.views.decorators.cache import never_cache
	
	
def password_reset(request, is_admin_site=False, template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        password_reset_form=PasswordResetForm, token_generator=default_token_generator,
        post_reset_redirect=None):
    if post_reset_redirect is None:
        post_reset_redirect = reverse('django.contrib.auth.views.password_reset_done')
    if request.method == "POST":
        form = password_reset_form(request.POST)
        if form.is_valid():
            opts = {}
            opts['use_https'] = request.is_secure()
            opts['token_generator'] = token_generator
            if is_admin_site:
                opts['domain_override'] = request.META['HTTP_HOST']
            else:
                opts['email_template_name'] = email_template_name
                if not Site._meta.installed:
                    opts['domain_override'] = RequestSite(request).domain
            form.save(**opts)
            return HttpResponseRedirect(post_reset_redirect)
    else:
        form = password_reset_form()
    return render_to_response(template_name, {
        'form': form,
    }, context_instance=RequestContext(request))

def password_reset_done(request, template_name='registration/password_reset_done.html'):
    return render_to_response(template_name, context_instance=RequestContext(request))

def password_reset_confirm(request, uidb36=None, token=None, template_name='registration/password_reset_confirm.html',
                           token_generator=default_token_generator, set_password_form=SetPasswordForm,
                           post_reset_redirect=None):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.
    """
    assert uidb36 is not None and token is not None # checked by URLconf
    if post_reset_redirect is None:
        post_reset_redirect = reverse('django.contrib.auth.views.password_reset_complete')
    try:
        uid_int = base36_to_int(uidb36)
    except ValueError:
        raise Http404

    user = get_object_or_404(User, id=uid_int)
    context_instance = RequestContext(request)

    if token_generator.check_token(user, token):
        context_instance['validlink'] = True
        if request.method == 'POST':
            form = set_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(post_reset_redirect)
        else:
            form = set_password_form(None)
    else:
        context_instance['validlink'] = False
        form = None
    context_instance['form'] = form    
    return render_to_response(template_name, context_instance=context_instance)

def password_reset_complete(request, template_name='registration/password_reset_complete.html'):
    return render_to_response(template_name, context_instance=RequestContext(request,
                                                                             {'login_url': settings.LOGIN_URL}))

def password_change(request, template_name='registration/password_change_form.html',
                    post_change_redirect=None):
    if post_change_redirect is None:
        post_change_redirect = reverse('registration/password_change_done')
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(post_change_redirect)
    else:
        form = PasswordChangeForm(request.user)
    return render_to_response(template_name, {
        'form': form,
    }, context_instance=RequestContext(request))
password_change = login_required(password_change)

def password_change_done(request, template_name='registration/password_change_done.html'):
    return render_to_response(template_name, context_instance=RequestContext(request))


##############Free Comments####################################


from django import http
from django.conf import settings

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.html import escape
from django.views.decorators.http import require_POST
from django.contrib import comments
from django.contrib.comments import signals

class CommentPostBadRequest(http.HttpResponseBadRequest):
    """
    Response returned when a comment post is invalid. If ``DEBUG`` is on a
    nice-ish error message will be displayed (for debugging purposes), but in
    production mode a simple opaque 400 page will be displayed.
    """
    def __init__(self, why):
        super(CommentPostBadRequest, self).__init__()
        if settings.DEBUG:
            self.content = render_to_string("comments/400-debug.html", {"why": why})

def post_comment(request, next=None):
    """
    Post a comment.

    HTTP POST is required. If ``POST['submit'] == "preview"`` or if there are
    errors a preview template, ``comments/preview.html``, will be rendered.
    """
    # Fill out some initial data fields from an authenticated user, if present
    data = request.POST.copy()
    if request.user.is_authenticated():
        if not data.get('name', ''):
            data["name"] = request.user.get_full_name() or request.user.username
        if not data.get('email', ''):
            data["email"] = request.user.email

    # Check to see if the POST data overrides the view's next argument.
    next = data.get("next", next)

    # Look up the object we're trying to comment about
    ctype = data.get("content_type")
    object_pk = data.get("object_pk")
    if ctype is None or object_pk is None:
        return CommentPostBadRequest("Missing content_type or object_pk field.")
    try:
        model = models.get_model(*ctype.split(".", 1))
        target = model._default_manager.get(pk=object_pk)
    except TypeError:
        return CommentPostBadRequest(
            "Invalid content_type value: %r" % escape(ctype))
    except AttributeError:
        return CommentPostBadRequest(
            "The given content-type %r does not resolve to a valid model." % \
                escape(ctype))
    except ObjectDoesNotExist:
        return CommentPostBadRequest(
            "No object matching content-type %r and object PK %r exists." % \
                (escape(ctype), escape(object_pk)))

    # Do we want to preview the comment?
    preview = "preview" in data

    # Construct the comment form
    form = comments.get_form()(target, data=data)

    # Check security information
    if form.security_errors():
        return CommentPostBadRequest(
            "The comment form failed security verification: %s" % \
                escape(str(form.security_errors())))

    # If there are errors or if we requested a preview show the comment
    if form.errors or preview:
        template_list = [
            "comments/%s_%s_preview.html" % tuple(str(model._meta).split(".")),
            "comments/%s_preview.html" % model._meta.app_label,
            "comments/preview.html",
        ]
        return render_to_response(
            template_list, {
                "comment" : form.data.get("comment", ""),
                "form" : form,
                "next": next,
            },
            RequestContext(request, {})
        )

    # Otherwise create the comment
    comment = form.get_comment_object()
    comment.ip_address = request.META.get("REMOTE_ADDR", None)
    if request.user.is_authenticated():
        comment.user = request.user

    # Signal that the comment is about to be saved
    responses = signals.comment_will_be_posted.send(
        sender  = comment.__class__,
        comment = comment,
        request = request
    )

    for (receiver, response) in responses:
        if response == False:
            return CommentPostBadRequest(
                "comment_will_be_posted receiver %r killed the comment" % receiver.__name__)

    # Save the comment and signal that it was saved
    comment.save()
    signals.comment_was_posted.send(
        sender  = comment.__class__,
        comment = comment,
        request = request
    )

    return next_redirect(data, next, comment_done, c=comment._get_pk_val())
   
from django.contrib.auth.models import User  
from django.contrib.auth.decorators import login_required
from django.contrib.comments.models import Comment
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib import comments

def delete_own_comment(request, message_id):
    comment = get_object_or_404(comments.get_model(), pk=message_id,
            site__pk=settings.SITE_ID)
    if comment.user == request.user:
        comment.is_removed = True
        comment.save()





