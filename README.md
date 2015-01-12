opentaba-poster
===============

A social poster for the [opentaba-server](http://github.com/niryariv/opentaba-server) project.

This project is an independant service that can recieve a title, content and url from [opentaba-server](http://github.com/niryariv/opentaba-server) and post it to [Facebook](http://facebook.com) and [Twitter](http://twitter.com), while in the process shortening the url using [Bit.ly](http://bit.ly).
To use it just run it ([heroku](http://heroku.com) ready), and point your [opentaba-server](http://github.com/niryariv/opentaba-server) instance to it using the instruction found at the [DEPLOYMENT readme](https://github.com/niryariv/opentaba-server/blob/social_poster/DEPLOYMENT.md).

###Enabling Bit.ly
If you want links to be shortened before they are posted, you can enable Bit.ly shortening (not a must for neither Facebook nor Twitter posting).
The needed variable is only `BITLY_TOKEN`. Set it by running: `heroku config:set BITLY_TOKEN="token" --app poster`

###Adding a New Poster
No interface at the moment, to add a new poster with tokens and an assigned id, add a new document to the database that looks like this (Facebook is not dependent upon Twitter, and vice-versa. Technically, no fields are mandatory besides id):
```
{
    "id": "1",
    "desc": "opentaba-server-holon",
    "fb_tok": "holon-facebook-token",
    "fb_page": "holon-facebook-page-id",
    "tw_tok": "holon-twitter-token",
    "tw_tsec": "holon-twitter-token-secret",
    "tw_con": "holon-twitter-consumer-id",
    "tw_csec": "holon-twitter-consumer-secret"
}
```

A new poster can now be added using a [fabric](http://fabfile.org) task which exists in the [opentaba-server](http://github.com/niryariv/opentaba-server) repository.
Further details can be found on its [Deployment Readme](http://github.com/niryariv/opentaba-server/blob/master/DEPLOYMENT.md#all-fabric-tasks).

###Getting The Tokens
There are two helper scripts made to help you authorize the Facebook and Twitter apps, which require manual web authorization, and get your access tokens easily.
Before you can run them there are two things you must do:
  1. Install their required libraries on your environment, ie. `pip install -r scripts/requirements.txt`
  2. Set the app id and app secret on the Facebook script, or consumer key and consumer secret on the Twitter script. These are obviously not provided with the script, and are attainable at both apps' settings pages.

####Facebook
Run the `scripts/get_facebook_token.py` script, and browse [http://0.0.0.0:8080](http://0.0.0.0:8080).
After authorizing the app, you will be redirected to a page which will list all your pages, their ids and their access tokens. Our server only posts to one page, so pick one and set the environment variables accordingly.
####Twitter
Run the `scripts/get_twitter_token.py` script, and browse [http://0.0.0.0:8080](http://0.0.0.0:8080).
After authorizing the app, you will be redirected to a page with your access token and access token secret.
####Bit.ly
Simply go to the Bit.ly website's [apps page](https://bitly.com/a/oauth_apps) and generate a generic access token, which you can use.
