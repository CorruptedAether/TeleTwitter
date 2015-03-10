import threading
import Queue
import teletype
from twython import TwythonStreamer

TERMS = None #'#makeathon'

#Twitter API stuff
apiKey = '4asy4QbguR1ekoNYspzFG33GI'
apiSecret = 'wolfgQCcdjEmizkA8gW61x3oxueIlRPXCnw5BdAfPRYGoYSgdb'
accessToken = '2813902646-wDBQECBKirtejL5aqVlMYfw1o4dMPTJougM0sKA'
accessTokenSecret = 'NxclZEwpPvn85Pn4FTU1FZdRgkT5sVmoK30UDKHEOtn03'

queue = Queue.Queue()

class Streamer(TwythonStreamer):
#     def __init__(self, queue):
#         TwythonStreamer.__init__(self)
#         self.queue = queue
    def on_success(self, data):
        if 'text' in data:
            queue.put(data['text'].encode('utf-8'))
            

class TwitterThread(threading.Thread):
    
    def __init__(self,queue):
        threading.Thread.__init__(self)
        self.queue = queue
    def run(self):
            stream = Streamer(apiKey, apiSecret, accessToken, accessTokenSecret)
            stream.statuses.filter(track=TERMS)

#TERMS = raw_input("Please input a hash tag to track (include #): ")

twitterThread = TwitterThread(queue)
twitterThread.setDaemon(True)
twitterThread.start()

teletype.start()
while True:
    sentence = queue.get()
    teletype.txstr(sentence)