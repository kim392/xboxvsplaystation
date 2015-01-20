#!/home/adrian/.virtualenvs/twitter/bin/python


xbox_hashtags = ['#xbox', '#xboxone', '#xbox360', '#halo']

playstation_hashtags = ['#playstation', '#ps4', 'ps3', 'ps2']

from textblob import TextBlob
from collections import deque
import MySQLdb
import time
import warnings
warnings.filterwarnings('ignore', category=MySQLdb.Warning)
class RateLimit:
    def __init__(self, allowed_requests, seconds):
        self.allowed_requests = allowed_requests
        self.seconds = seconds
        self.made_requests = deque()

    def __reload(self):
        t = time.time()
        while len(self.made_requests) > 0 and self.made_requests[0] < t:
            self.made_requests.popleft()

    def add_request(self):
        self.made_requests.append(time.time() + self.seconds)

    def request_available(self):
        self.__reload()
        return len(self.made_requests) < self.allowed_requests



from twitter import *
con_secret='WbpxprmtVdhc4ha2Rx9jx5P6W'
con_secret_key='gbMLFzBVWw0EIThAnbiPOdhDgjZOHGJgfIX9hxDfY37TbMxsDX'
token='2707762099-ykCIl3covDcvNsjt2MRl2oFf1VGNU9IfT7zAreW'
token_key='GeKqZnHG6rGcuIlihvlRNV6trznBImQygJX6dG31K58vR'

limit = RateLimit(180, 900)


t = Twitter(
    auth=OAuth(token, token_key, con_secret, con_secret_key))

sleep = 180/15*60
def can_make_request(limits):
    for lim in limits:
        if not lim.request_available():
            return False
    return True


toggle_xbox = True

id_diff = 1000000000000

max_id = 557346367329554432 
since_id = max_id - id_diff



connection = MySQLdb.Connection(host='localhost', user='root', passwd='password', db='twitter',use_unicode=True,charset='UTF8')
cursor = connection.cursor(MySQLdb.cursors.DictCursor)
from datetime import datetime
sql = """insert into twitter (text, polarity, date, type) values ("%(text)s", %(polarity)s, %(date)s, %(type)s);"""
while(True):
    while(not can_make_request([limit])):
        pass
    if(toggle_xbox):
        q= " OR ".join(xbox_hashtags)
    else:
        q= " OR ".join(playstation_hashtags)
    toggle_xbox = not toggle_xbox
    #print q
    tweets = t.search.tweets(q=q, count=100, max_id=max_id, since_id=since_id)
    max_id = max_id - id_diff
    since_id = max_id - id_diff
    print len(tweets['statuses'])
    for status in tweets['statuses']:
        #print status['text']
        polarity = TextBlob(status['text']).sentiment.polarity
        #print polarity
        #if(polarity > .25): 
        #    print "Positive"
        #elif(polarity < -.25): 
        #    print "Negative"
        #else:
        #    print "Neutral"
        ##print "\n"
        row = {}
        if(toggle_xbox):
            row['type'] = 'xbox'
        else:
            row['type'] = 'playstation'
        row['text'] = status['text']
        row['polarity'] = polarity
        d = datetime.strptime(status['created_at'],'%a %b %d %H:%M:%S +0000 %Y');
        row['date'] = d.strftime('%Y-%m-%d');
        #print row['date']
        #print sql % row
        cursor.execute(sql, row)
        connection.commit()

















