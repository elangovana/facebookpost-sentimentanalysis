# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import urllib
import re

import sys
import urllib2

from django.shortcuts import render
# Create your views here.

from django.http import HttpResponse

reload(sys)
sys.setdefaultencoding('utf8')


def transform_reponse(html):
    result = html
    result = re.sub(r"\"https://[^\"]*facebook.com", "http://localhost/proxy", html)
    return result


def index(request):
    # Accept-Language: da, en-gb
    req = urllib2.Request('https://www.facebook.com')
    req.add_header('Accept-Language', 'en-gb')
    response = urllib2.urlopen(req)
    html = response.read()
    transformed_html = transform_reponse(html)
    return HttpResponse(transformed_html)
