#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# Copyright (c) Electronic Offense. GmbH
# All rights reserved.
#
# Daniel Zulla <dzulla@electronicoffense.com>

import os
import sys
import json
import time
import threading

from requests_futures.sessions import FuturesSession

extensions = ["php", "txt", "pdf", "zip", "tgz", "asp", "inc", "tpl"]
session = FuturesSession(max_workers=100)
randomseed = "1enjfn3i"
dumb_code = 404
dumb_length = 0
url_cache = {}
current_dir = ""
lock = threading.Lock()
difficult_extensions = []
tested_extensions = 0

def ext_callback(sess, resp):
  print "Ext URL: %s" %resp.url
  print "Extension callback %d" %resp.status_code
  test_ext = resp.url.split(".")[-1]
  ext_code = resp.status_code
  if resp.status_code != 404:
    lock.acquire()
    ++tested_extensions
    difficult_extensions.append(test_ext)
    lock.release()

def dumb_callback(sess, resp):
  lock.acquire()
  print "Dumb callback called %s" %resp.status_code
  dumb_code = resp.status_code
  dumb_length = len(resp.text)
  lock.release()

def bg_cb(sess, resp):
    if (resp.status_code != 404
      and resp.status_code != dumb_code
      and bool(filter(None, resp.text.split("\n"))) == True
      and resp.url not in url_cache.keys()
      and resp.url.count("-") <= 2
      and resp.url.count("_") <= 2):
      lock.acquire()
      url_cache[resp.url] = 1
      lock.release()
      x = {"%s" %resp.url: resp.status_code}
      print json.dumps(x)

def main():
    minimal = open("minimal.wl", "r").read()
    words = [line for line in minimal.split("\n")[:-1]]
    url = "%s%s" %(sys.argv[1], randomseed)
    future = session.get(url, background_callback=dumb_callback)
    future.result()

    for ext in extensions:
        future = session.get("%s%s%s.%s" %(url, current_dir, 
            randomseed, ext), background_callback=ext_callback)

    for word in words:
        url = "%s%s%s" %(sys.argv[1], word, ext)
        future = session.get(url, background_callback=bg_cb)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: ./pixel.py [url with trailing /]"
    else:
       main()
