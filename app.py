#!/usr/bin/python

import os
import logging
from json import loads
from threading import Thread
from Queue import Queue
import pymongo

from flask import Flask, request, abort, make_response
import bitly_api
from facepy import GraphAPI
from twitter import *

from conn import db

logging.basicConfig(format='%(asctime)-15s %(name)s %(levelname)s %(message)s', level=logging.WARNING)
log = logging.getLogger(__name__)
app = Flask(__name__)
post_queue = Queue()


#### WORKER ####

def post_worker():
    while True:
        # this will block the thread indefinetly until an item is popped
        post_params = post_queue.get()
        
        # get the poster's data from our db
        poster_data = db.posters.find_one({'id': post_params['poster_id']})
        
        if poster_data is None:
            log.exception('poster_id not valid')
        else:
            # get post details
            url = (post_params['url'] if 'url' in post_params.keys() else '')
            title = (post_params['title'] if 'title' in post_params.keys() else '')
            content = (post_params['content'] if 'content' in post_params.keys() else '')
            
            # if bitly access token is defined shorten the link
            if len(url) > 0 and 'BITLY_TOKEN' in os.environ.keys():
                try:
                    b = bitly_api.Connection(access_token=os.environ['BITLY_TOKEN'])
                    shortie = b.shorten(url)
                    url = shortie['url']
                except Exception, e:
                    log.exception('Could not shorten the link using bit.ly - %s', e)
                
            # facebook-needed params
            if all(param in poster_data.keys() for param in ['fb_tok', 'fb_page']):
                try:
                    graph = GraphAPI(poster_data['fb_tok'])
                    graph.post(
                        path = 'v2.2/%s/feed' % poster_data['fb_page'],
                        message = '%s: %s %s' % (title, content, url),
                        retry = 10
                    )
                except Exception, e:
                    log.exception('Could not post new plan to facebook page - %s', e)
                
            # twitter-needed params
            if all(param in poster_data.keys() for param in ['tw_tok', 'tw_tsec', 'tw_con', 'tw_csec']):
                try:
                    tweet_content = '%s: %s' % (title, content)
                    
                    # shorten our content - max size should be 118, not including the link which will be
                    # shortened by twitter if bit.ly is not enabled
                    if len(tweet_content) > 118:
                        tweet = '%s... %s' % (tweet_content[0:114], url)
                    else:
                        tweet = '%s %s' % (tweet_content, url)
                    
                    t = Twitter(auth=OAuth(consumer_key=poster_data['tw_con'], consumer_secret=poster_data['tw_csec'], token=poster_data['tw_tok'], token_secret=poster_data['tw_tsec']))
                    t.statuses.update(status=tweet)
                except Exception, e:
                    log.exception('Could not post new plan to twitter feed - %s', e)
        
        # done with this task. release
        post_queue.task_done()


#### ROUTES ####

@app.route('/post', methods=['POST'])
def post_route():
    """
    post plan data to facebook, twitter or both
    """
    
    # check if poster_id is given, otherwise bad request
    if 'poster_id' not in request.form.keys():
        abort(400)
    
    # queue the request
    try:
        post_queue.put(request.form)
    except Exception, e:
        log.exception('Could not push post into queue - %s', e)
    
    # respond quickly to end the connection
    r = make_response('{"status":"ok"}')
    r.headers['Content-Type'] = 'application/json'
    return r


@app.route('/status')
def status_route():
    return "There are approximately %s posts waiting in queue..." % post_queue.qsize()


#### MAIN ####

if __name__ == '__main__':
    # start the worker thread
    t = Thread(target=post_worker)
    t.daemon = True
    t.start()
    
    # bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
