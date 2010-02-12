#!/usr/bin/env python

"""
Upload Google Bookmarks to delicious
"""

import sys
import base64
from pydelicious import DeliciousAPI
from pydelicious import PyDeliciousThrottled
from pydelicious import PyDeliciousUnauthorized
from getpass import getpass
from time import sleep
import xml.dom.minidom
from xml.dom.minidom import Node
import time

if (len(sys.argv) < 2):
    print "This script will copy your Google Bookmarks to Delicious. Any bookmarks at Delicious that point to the same url as a bookmark being imported will have it's tags and date updated. You will be prompted for your delicious username and password. All utf-8 characters are converted to ascii. Sorry i18n users."
    print "usage:\n" + sys.argv[0] + " <googleBookmark.xml>\n\nWhere <googleBookmark.xml> is your google bookmark feed from http://www.google.com/bookmarks/find?q=&output=rss&num=10000"
    exit(0)

doc = xml.dom.minidom.parse(sys.argv[1])
username = raw_input('username:')
delish = DeliciousAPI(username, getpass('Password:'))
items = doc.getElementsByTagName("item")
print "Found ", len(items), " bookmarks. This script will take 1 second for each bookmark (per delicious rules)"

for node in items:
    tag_string = title = url = ddate = desc = ""
    labels = []
    t = node.getElementsByTagName("title")
    if (len(t) > 0 and len(t[0].childNodes) > 0):
	title = t[0].childNodes[0].data.encode('ascii','replace')
    u = node.getElementsByTagName("link")
    if (len(u) > 0 and len(u[0].childNodes) > 0):
	url = u[0].childNodes[0].data.encode('ascii','replace')
    da = node.getElementsByTagName("pubDate")
    if (len(da) > 0 and len(da[0].childNodes) > 0):
	date = da[0].childNodes[0].data.encode('ascii','replace')
        ddate = time.strftime("%Y-%m-%dT%H:%M:%SZ",time.strptime(date,"%a, %d %b %Y %H:%M:%S %Z"))
    d = node.getElementsByTagName("description")
    if (len(d) > 0 and len(d[0].childNodes) > 0):
        desc = d[0].childNodes[0].data.encode('ascii','replace')
    labelNodes = node.getElementsByTagName("smh:bkmk_label")
    for l in labelNodes:
	if (len(l.childNodes) > 0):
	    labels.append(l.childNodes[0].data.encode('ascii','replace'))
    for tag in labels:
	tag_string += tag.replace(" ","_") + " "
    print ddate + " " + title + ":" + url + ":" + desc + ":'" + tag_string + "'"
    try:
	delish.posts_add(url, title, extended=desc, tags=tag_string, dt=ddate, replace=True)
    except PyDeliciousUnauthorized:
	print "Authorization to Delicious failed"
	exit(0)
    except PyDeliciousThrottled:
	print "Being throttled by delicious, waiting 2 seconds"
	sleep(2)
	try:
	    delish.posts_add(url, title, extended=desc, tags=tag_string, dt=ddate, replace=True)
	except PyDeliciousThrottled:
	    print "Still throttled, quitting."
	    exit(0)
    sleep(1) #delicious doesn't want to be flooded with requests. Fair enough
