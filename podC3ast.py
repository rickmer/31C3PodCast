from lxml import objectify, etree
from urllib2 import Request, urlopen
from urllib import urlopen as header

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

# process events
for day in fahrplan.day:
    for room in day.getchildren():
        for event in room.getchildren():
            if int(event.attrib['id']) in media_urls:
                print '<item>'
                print '<title>' + event.title.text.encode('utf8', 'replace') + '</title>'
                if event.description.text is not None:
                    print '<description><![CDATA[' + event.description.text.encode('utf8', 'replace') + ']]></description>'
                else:
                    print '<description></description>'
                author = []
                for person in event.persons.getchildren():
                     author.append(person.text.encode('utf8', 'replace'))
                print '<itunes:author>' + ', '.join(author) + '</itunes:author>'
                length = header(cdn_url + media_urls[int(event.                  attrib['id'])]).info().getheaders('Content-Length')[0]
                print '<pubDate> Sun, 01 Jan 2015 21:00:00 EST </pubDate>'
                print '<enclosure url="' + cdn_url + media_urls[int(event.attrib['id'])] + '" length="' + length + '" type="audio/mpeg" />' 
                print '</item>'
