# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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
    result = re.sub(r"\"https://[^\"]*facebook.com", "http://localhost:8000/proxy", result)
    return result

def transform_request(html):
    result = html
    # TODO: fix path issue
    result = re.sub(r"\"http://localhost:8000/proxy", "https://www.facebook.com",  result)
    return result

@csrf_exempt
def index(request):
    # Accept-Language: da, en-gb
    #TODO:fix path issue
    fbrelativePath = re.sub(r"^/proxy/", "",request.path_info)

    fbreponse = get_fbresponse(fbrelativePath, request)


    #fbreponse cookies
    cookies = fbreponse.info()['Set-Cookie']
    #fbhtmlcontent
    html = fbreponse.read()
    transformed_html = transform_reponse(html)
    #return
    response = HttpResponse(transformed_html)
    response.set_cookie( cookies)
    return response


def get_fbresponse(fbrelativePath, request):
    path = 'https://www.facebook.com/' + fbrelativePath
    fbrequest = urllib2.Request(path)
    fbrequest.add_header('Accept-Language', 'en-gb')
    # add cookies
    fbrequest.add_header('Cookie', "; ".join('%s=%s' % (k, v) for k, v in request.COOKIES.items()))
    if (request.method != 'GET'):
        fbrequest.add_data(transform_request(request.body))

    # get resposne
    fbreponse = urllib2.urlopen(fbrequest)
    return fbreponse
