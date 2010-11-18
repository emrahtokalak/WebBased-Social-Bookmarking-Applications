# -*- coding: utf-8 -*-
from django.contrib.syndication.feeds import Feed
from LikedFeed.bookmarks.models import Bookmark
class RecentBookmarks(Feed):
	title = 'LikedFeed | Son yayınlar'
	link = '/feeds/recent/'
	description = 'Kullanıcıların son hareketlerinden oluşuyor.'
	
	def items(self):
		return Bookmark.objects.order_by('-id')[:10] 
