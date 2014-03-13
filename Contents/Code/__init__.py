################################################################################
PREFIX = '/video/dotacinema'

TITLE  = 'DotaCinema'
ART    = 'art-default.jpg'
ICON   = 'icon-default.png'

################################################################################
def Start():
	ObjectContainer.art    = R(ART)
	DirectoryObject.thumb  = R(ICON)
	ObjectContainer.title1 = TITLE
	VideoClipObject.thumb  = R(ICON)

################################################################################
@handler(PREFIX, TITLE, thumb=ICON, art=ART)
def Main():
	object_container = ObjectContainer()
	object_container.add(DirectoryObject(key=Callback(recent, title='Recent Uploads'), title='Recent Uploads'))
	object_container.add(DirectoryObject(key=Callback(shows, title='Shows'), title='Shows'))
	object_container.add(DirectoryObject(key=Callback(vods, title='VODs'), title='VODs'))
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

################################################################################
@route(PREFIX + '/vods')
def vods(title):
	object_container = ObjectContainer(title2=title)
	object_container.add(DirectoryObject(key=Callback(vods_search, title='Recent Matches', tournament_id='__EMPTY__'), title='Recent Matches'))
	object_container.add(DirectoryObject(key=Callback(vods_tournaments, title='Tournaments'), title='Tournaments'))
	return object_container

################################################################################
@route(PREFIX + '/vods/tournaments')
def vods_tournaments(title):
	html_url     = 'http://www.dotacinema.com/vods'
	html_content = HTML.ElementFromURL(html_url)

	object_container = ObjectContainer(title2=title)
	for html_item in html_content.xpath('//*[@class="filter_box tourbox"]'):
		tournament_name = html_item.get('data-description').split(';')[0]
		tournament_id   = html_item.get('id')
		object_container.add(DirectoryObject(key=Callback(vods_search, title=tournament_name, tournament_id=tournament_id), title=tournament_name))

	return object_container

################################################################################
@route(PREFIX + '/vods_search')
def vods_search(title, tournament_id):
	tournament_id = '' if tournament_id == '__EMPTY__' else tournament_id

	html_url     = 'http://www.dotacinema.com/vods?tournaments={0}'.format(tournament_id)
	html_content = HTML.ElementFromURL(html_url)

	object_container = ObjectContainer(title2=title)
	for html_item in html_content.xpath('//*[@class="vod_container"]/a'):
		tournament_name = html_item.xpath('./div/div[@class="tournament"]/@title')[0]
		team1_name      = html_item.xpath('./div/div[@class="team1"]/span[2]/@title')[0]
		team2_name      = html_item.xpath('./div/div[@class="team2"]/span[2]/@title')[0]
		match_type      = html_item.xpath('./div/div[@class="matchtype"]/text()')[0]
		caster_names    = vod_get_casters(html_item)

		vod_name    = '{0} - {1} ({2})'.format(team1_name, team2_name, match_type)
		vod_tagline = title
		vod_summary = '{0}\n\nCasted by {1}'.format(tournament_name, caster_names)
		vod_url  = 'http://www.dotacinema.com' + html_item.get('href')
		object_container.add(DirectoryObject(key=Callback(vod, title=vod_name, vod_summary=vod_summary, vod_url=vod_url), title=vod_name, tagline=vod_tagline, summary=vod_summary))

	return object_container

################################################################################
@route(PREFIX + '/vod')
def vod(title, vod_summary, vod_url):
	html_url     = vod_url
	html_content = HTML.ElementFromURL(html_url)

	object_container = ObjectContainer(title2=title)
	for html_item in html_content.xpath('//a[@class="gamelink"]'):
		game_name    = html_item.xpath('./div/text()')[0]
		game_summary = vod_summary
		game_url     = 'http://www.youtube.com/watch?v={0}'.format(html_item.xpath('./div/@data-youtube')[0])
		object_container.add(VideoClipObject(title=game_name, summary=game_summary, url=game_url))

	return object_container

################################################################################
def vod_get_casters(html_item):
	casters = []
	for caster_name in html_item.xpath('./div/div[@class="caster "]/span[@class="caster_icon"]/@title'):
		casters.append(caster_name)
	for caster_name in html_item.xpath('./div/div[@class="caster full-width"]/span[@class="caster_icon"]/@title'):
		casters.append(caster_name)
	for caster_name in html_item.xpath('./div/div[@class="caster caster_text"]/text()'):
		casters.append(caster_name)
	for caster_name in html_item.xpath('./div/div[@class="caster full-width caster_text"]/text()'):
		casters.append(caster_name)
	return ', '.join(casters)
