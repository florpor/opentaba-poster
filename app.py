#!/usr/bin/python

import os
import logging
from json import loads
from threading import Thread
from Queue import Queue

from flask import Flask, request
import bitly_api
from facepy import GraphAPI
from twitter import *

logging.basicConfig(format='%(asctime)-15s %(name)s %(levelname)s %(message)s', level=logging.WARNING)
log = logging.getLogger(__name__)
app = Flask(__name__)
post_queue = Queue()


#### WORKER ####

def post_worker():
    while True:
        # this will block the thread indefinetly until an item is popped
        post_params = post_queue.get()
        
        plan = loads(post_params['plan'])
    
        # if bitly access token is defined shorten the link
        if 'BITLY_TOKEN' in os.environ.keys():
            try:
                b = bitly_api.Connection(access_token=os.environ['BITLY_TOKEN'])
                shortie = b.shorten(plan['details_link'])
                plan['url'] = shortie['url']
            except Exception, e:
                log.exception('Could not shorten the link using bit.ly - %s', e)
        
        
    
        # facebook-needed params
        if all(param in ['fb_tok', 'fb_page'] for param in post_params.keys()):
            try:
                graph = GraphAPI(post_params['fb_tok'])
                graph.post(
                    path = 'v2.2/%s/feed' % post_params['fb_page'],
                    message = '%s: %s %s' % (plan['title'], plan['content'], plan['url']),
                    retry = 10
                )
            except Exception, e:
                log.exception('Could not post new plan to facebook page - %s', e)
    
        # twitter-needed params
        if all(param in ['tw_tok', 'tw_tsec', 'tw_con', 'tw_csec'] for param in post_params.keys()):
            try:
                tweet_content = '%s: %s' % (plan['title'], plan['content'])
            
                # shorten our content - max size should be 118, not including the link which will be shortened by twitter if bit.ly is not enabled
                if len(tweet_content) > 118:
                    tweet = '%s... %s' % (tweet_content[0:114], url)
                else:
                    tweet = '%s %s' % (tweet_content, url)
            
                t = Twitter(auth=OAuth(consumer_key=post_params['tw_con'], consumer_secret=post_params['tw_csec'], token=post_params['tw_tok'], token_secret=post_params['tw_tsec']))
                t.statuses.update(status=tweet)
            except Exception, e:
                log.exception('Could not post new plan to twitter feed - %s', e)
        
        post_queue.task_done()


#### ROUTES ####

@app.route('/post', methods=['POST'])
def post_route():
    """
    post plan data to facebook, twitter or both
    """
    
    # check if post is given, otherwise bad request
    if 'plan' not in request.form.keys():
        return 400
    
    try:
        post_queue.put(request.form)
    except Exception, e:
        log.exception('Could not push post into queue - %s', e)
    
    return 200


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
