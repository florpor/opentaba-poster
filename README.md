opentaba-poster
===============

A social poster for the [opentaba-server](http://github.com/niryariv/opentaba-server) project.

This project is an independant service that can recieve a plan from [opentaba-server](http://github.com/niryariv/opentaba-server) and post it to [Facebook](http://facebook.com) and [Twitter](http://twitter.com), while in the process shortening the url using [Bit.ly](http://bit.ly).
To use it just run it ([heroku](http://heroku.com) ready), and point your [opentaba-server](http://github.com/niryariv/opentaba-server) instance to it using the instruction found at the [DEPLOYMENT readme](https://github.com/niryariv/opentaba-server/blob/social_poster/DEPLOYMENT.md).

####Enabling Bit.ly
If you want links to be shortened before they are posted, you can enable Bit.ly shortening (not a must for neither Facebook nor Twitter posting).
The needed variable is only `BITLY_TOKEN`. Set it by running: `heroku config:set BITLY_TOKEN="token" --app poster`
