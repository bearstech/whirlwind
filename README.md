Whirlwind
=========

Whirlwind is a modern fork of the Graphite stack : Graphite + Carbon + Whisper.

The objective is to remove Django and Cairo as dependency, adding unit tests, removing pythonic parts of protocols.

Whirlwind is built as a framework, with a simple application : something client side, with d3js.

Whirlwind is modular, should play well with pypy, Tornado, Numpy or Panda. As option, not mandatory.

Whirlwind provides time series as a service, add your own dashbord, even in Ruby or PHP, make some stats with scipy or R.

Whirlwind is built with security and confidentiality in mind, for shared network.
SSL or localhost is the norm.

Sub parts
---------

This projects, scratch built, forked or as is, can be used in the Whirlwind big picture.

 * [Kluczy](https://github.com/bearstech/kluczy) handles your SSL certificates.
 * [Diamond](https://github.com/bearstech/Diamond) sends some metrics.
 * [Statsd](https://github.com/bearstech/statsd) sends more metrics, the official one.
 * [Gstatsd](https://github.com/bearstech/gstatsd) the gevent's statsd fork, features are missing.
 * [MySlow](https://github.com/bearstech/myslow) use mysql slow log to build metrics. POC.
 * [Whirlwind-Tornado](https://github.com/bearstech/whirlwind-tornado) is Tornado specific parts. Carbon clone with Redis. POC.
 * [Basho Bench](https://github.com/bearstech/basho_bench) benchmark carbon server. Patch accepted in official application.

Blog posts
----------

 * [Managing your own Certificate Authority, the declarative way](http://blog.bearstech.com/2013/11/managing-your-own-certificate-authority-the-declarative-way.html)
 * [Bench everything](http://blog.bearstech.com/2013/05/bench-everything.html)
 * [http://blog.bearstech.com/2013/03/authenticate-everything-with-ssl.html](http://blog.bearstech.com/2013/03/authenticate-everything-with-ssl.html)

Status
------

[![Build Status](https://travis-ci.org/bearstech/whirlwind.png?branch=master)](https://travis-ci.org/bearstech/whirlwind)
 * √ Using perlin's noise for testing.
 * √ Use Bottle for REST web services.
 * _ Time series computation.

Licence
-------

Apache Licence 2 © 2013 Mathieu Lecarme.

Large parts of code come from Graphite and Whisper projects,
under the same licence.

Perlin noise from https://github.com/caseman/noise
