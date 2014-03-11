################################################################################
PREFIX = '/video/dotacinema'

TITLE  = 'DotaCinema'
ART    = 'art-default.jpg'
ICON   = 'icon-default.png'

################################################################################
def Start():
	ObjectContainer.art    = R(ART)
	ObjectContainer.title1 = TITLE
	VideoClipObject.art    = R(ART)
	VideoClipObject.thumb  = R(ICON)

################################################################################
@handler(PREFIX, TITLE)
def Main():
	object_container = ObjectContainer(title2=TITLE)
	object_container.add(DirectoryObject(key=Callback(recent, title='Recent Uploads'), title='Recent Uploads', thumb=R(ICON)))
	object_container.add(DirectoryObject(key=Callback(shows, title='Shows'), title='Shows', thumb=R(ICON)))
	return object_container

################################################################################
@route(PREFIX + '/recent')
def recent(title):
	html_url     = 'http://www.youtube.com/user/DotaCinema/videos?view=0'
	html_content = HTML.ElementFromURL(html_url)

	object_container = ObjectContainer(title2=title)
	for html_item in html_content.xpath('//*[@class="channels-content-item yt-shelf-grid-item"]'):
		Log.Info('FOUND 1 ITEM')
		videoclip_name  = html_item.xpath('./div/div[2]/h3/a/text()')[0].strip()
		videoclip_url   = 'http://www.youtube.com' + html_item.xpath('./div/div[2]/h3/a/@href')[0].strip()
		videoclip_thumb = Resource.ContentsOfURLWithFallback('http:' + html_item.xpath('./div/div[1]/a/span[1]/span/span/img/@src')[0])
		object_container.add(VideoClipObject(title=videoclip_name, url=videoclip_url, thumb=videoclip_thumb))

	return object_container

################################################################################
@route(PREFIX + '/shows')
def shows(title):
	html_url     = 'http://www.dotacinema.com/media'
	html_content = HTML.ElementFromURL(html_url)

	object_container = ObjectContainer(title2=title)
	for html_item in html_content.xpath('//*[@class="show"]'):
		show_name         = html_item.xpath('./h1/text()')[0]
		show_thumb        = Resource.ContentsOfURLWithFallback('http://www.dotacinema.com' + html_item.xpath('./img/@src')[0])
		show_summary      = html_item.xpath('./p/text()')[0] if html_item.xpath('./p/text()') else ''
		show_playlist_url = html_item.xpath('./a/@href')[-1]

		object_container.add(DirectoryObject(key=Callback(show, title=show_name, playlist_url=show_playlist_url), title=show_name, thumb=show_thumb, summary=show_summary))

	return object_container

################################################################################
@route(PREFIX + '/show')
def show(title, playlist_url):
	html_url     = playlist_url
	html_content = HTML.ElementFromURL(html_url)

	object_container = ObjectContainer(title2=title)
	for html_item in html_content.xpath('//div[@class="pl-video-content"]'):
		videoclip_name  = html_item.xpath('./div/h3/a/text()')[0].strip()
		videoclip_url   = 'http://www.youtube.com' + html_item.xpath('./a/@href')[0].strip()
		videoclip_thumb = Resource.ContentsOfURLWithFallback('http:' + html_item.xpath('./a/span/span/span/img/@src')[0])
		object_container.add(VideoClipObject(title=videoclip_name, url=videoclip_url, thumb=videoclip_thumb))

	object_container.objects.reverse()
	return object_container
