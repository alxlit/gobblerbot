# Gobblerbot

It's a bot (of sorts) that works on [Gobblerpedia], the student run Virginia
Tech wiki. Really it's a single-worker task queue with a minimal web interface.
It's all rather hacked together to be honest.

Still in development. You can see it online (maybe) [here](http://gobblerbot.alxlit.name/).

  * It's written in Python 2.7
  * It requires: [flask], [lxml], [mongodb], [pystache], [shovel], and
    [wikitools].

Note that `config.py` is in the `.gitignore` since it has the admin username
and password. Also note that some online resources, such as the [CDCD]'s master
building list, are only accessible to the Virginia Tech VPN.

[CDCD]:         http://www.cdcd.vt.edu
[Gobblerpedia]: http://gobblerpedia.org

[flask]:      http://flask.pocoo.org
[lxml]:       http://lxml.de/
[mongodb]:    http://mongodb.org
[pystache]:   https://github.com/defunkt/pystache
[shovel]:     http://github.com/seomoz/shovel
[wikitools]:  http://code.google.com/p/python-wikitools/
