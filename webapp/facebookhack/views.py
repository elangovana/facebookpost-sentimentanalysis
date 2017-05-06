# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import cookielib
import logging
import urllib
import re



import sys
import urllib2
import pdb

from django.shortcuts import render
# Create your views here.

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

reload(sys)
sys.setdefaultencoding('utf8')


def transform_reponse(html):
    result = html
    #TODO: fix path issue
    result = re.sub(r"\"https://[^\"]*facebook.com", "\"http://localhost:8000/proxy", result)
    return result

def transform_request(html):
    result = html
    # TODO: fix path issue
    result = re.sub(r"\"http://localhost:8000/proxy", "\"https://www.facebook.com",  result)
    return result

@csrf_exempt
def index(request):
    # Accept-Language: da, en-gb
    #TODO:fix path issue
    path_info = request.path_info
    fbrelativePath = re.sub(r"^/proxy/", "", path_info)

    fbreponse, cookie_jar = get_fbresponse(fbrelativePath, request)

    html = fbreponse.read()
    transformed_html = transform_reponse(html)
    #return
    response = HttpResponse(transformed_html)
    set_cookies(cookie_jar, response)
    return response


def set_cookies(cookies, response):
    if cookies == '':
        return

    for item in cookies:

        response.set_cookie( item.name, item.value)



def get_fbresponse(fbrelativePath, request):
    path = 'https://www.facebook.com/' + fbrelativePath
    cookiejar = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
    fbrequest = urllib2.Request(path)
    fbrequest.add_header('Accept-Language', 'en-gb')
    # add cookies
    cookie = "; ".join('%s=%s' % (k, v) for k, v in request.COOKIES.items())
    #TODO: fix domain in cookie
    re.sub("domain=[^;]+","",cookie)
    re.sub("original-domain=", "domain=", cookie)
    fbrequest.add_header('Cookie', cookie)

    if (request.method != 'GET'):
        fbrequest.add_data(transform_request(request.body))
    #pdb.set_trace()

    fbreponse = opener.open (fbrequest)
    return fbreponse, cookiejar
