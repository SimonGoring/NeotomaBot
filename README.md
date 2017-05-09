NeotomaBot
==========

by: Simon Goring

May 4, 2015

Description
----------------------
A twitter bot to search for new records in the [Neotoma Paleoecology Database](http://neotomadb.org) and then post them to the [@neotomadb](http://twitter.com/neotomadb) Twitter account.

This program was an experiment to see how good my Python programming skills are.  Apparently they're okay.  The code could probably use some cleaning, but I'm generally happy with the way it turned out.

The program runs on a free [Heroku](https://heroku.com) dyno and tweets semi-regularly.

Requirements
-----------------------------
The program uses `tweepy`, `time`, `sys`, `json`, `requests`, `random` and `imp` package for Python, as well as the Neotoma [API](http://api.neotomadb.org/doc/about).  It was coded in Notepad++ because I wanted to try to do it quickly.

The OAuth information is hidden on my computer and added to the `.gitignore`.  If you want to run this yourself you'll need to go to the Twitter [apps](https://apps.twitter.com/) page and register a bot of your own.  Once you get the `CONSUMER_KEY` and the other associated KEYs and SECRETs put them in a file called `apikeys.txt`.  The code will work.

Contributions and Bugs
----------------
This is a work in progress.  I'd like to add some more functionality in the near future, for example, following and reposting any posts using the hashtag [`#neotomadb`](https://twitter.com/search?f=realtime&q=%23neotomadb), and posting links to articles using the Neotoma Database.

If you have any issues (about the program!), would like to fork the repository, or would like to help improve or add functionality please feel free to contribute.

License
-------------------
This project is distributed under an [MIT](http://opensource.org/licenses/MIT) license.
