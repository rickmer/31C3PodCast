from lxml import objectify, etree
from urllib2 import Request, urlopen
from urllib import urlopen as header
from datetime import datetime
from string import replace

# fetch data
fahrplan_url = 'https://events.ccc.de/congress/2014/Fahrplan/schedule.xml'
cdn_url = 'http://cdn.media.ccc.de/congress/2014/mp3/'
fahrplan_xml = urlopen(Request(url=fahrplan_url)).read()
cdn_html = urlopen(Request(url=cdn_url)).read()

# parse data
fahrplan = objectify.fromstring(fahrplan_xml)
cdn = etree.HTML(cdn_html)

# extract urls
media_urls = {} 
for row in cdn.getchildren()[1].getchildren()[1].getchildren():
    if len(row.getchildren()) > 1 and row.getchildren()[1].tag == 'td' and row.getchildren()[1].getchildren()[0].attrib['href'][0] != '/':
        media_urls[int(row.getchildren()[1].getchildren()[0].attrib['href'][5:9])] = row.getchildren()[1].getchildren()[0].attrib['href']
items = []
# process events
for day in fahrplan.day:
    for room in day.getchildren():
        for event in room.getchildren():
            item = {}
            if int(event.attrib['id']) in media_urls:
                item['title'] =  replace(event.title.text.encode('utf8', 'replace'), '&', '&amp;')
                if event.description.text is not None:
                    item['desc'] = replace(event.description.text.encode('utf8', 'replace'),'&', '&amp;')
                else:
                    item['desc'] = ''
                author = []
                for person in event.persons.getchildren():
                     author.append(person.text.encode('utf8', 'replace'))
                item['author'] =  replace(', '.join(author), '&', '&amp;')
                item['length'] = header(cdn_url + media_urls[int(event.attrib['id'])]).info().getheaders('Content-Length')[0]
                date = datetime.strptime(event.date.text[:-6], '%Y-%m-%dT%H:%M:%S')
                item['date'] = date.strftime(' %a, %d %b %Y %H:%M:%S ')
                item['url'] = cdn_url + media_urls[int(event.attrib['id'])]  
                items.append(item)

 
print """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/DTDs/Podcast-1.0.dtd" xmlns:media="http://search.yahoo.com/mrss/">
<channel>
<title> 31C3 Talks - audio mp3 </title>
<description>all talks of the biggest hacker conference in the free world</description>
<itunes:author>CCC e.V.</itunes:author>
<link> https://media.ccc.de </link>
<itunes:image href="https://raw.githubusercontent.com/rickmer/31C3PodCast/master/logo.png" />
<pubDate> Sat, 27 Dec 2014 00:00:00 EST </pubDate>
<language>en-de</language>
<copyright> CC-BY-3.0 </copyright>
"""
for item in items:
    print '<item>'
    print ''.join(['<title>', item['title'], '</title>'])
    print ''.join(['<description><![CDATA[', item['desc'], ']]></description>'])
    print ''.join(['<itunes:author>', item['author'], '</itunes:author>'])
    print ''.join(['<pubDate>', item['date'], '</pubDate>'])
    print ''.join(['<enclosure url="', item['url'], '" length="', item['length'], '" type="audio/mpeg" />'])
    print '</item>'
print """</channel>
</rss>"""
