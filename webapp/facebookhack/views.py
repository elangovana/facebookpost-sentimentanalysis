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


def transform_reponse(html, content_type="text/html"):
    result = html

    if ("text/html" in content_type):
        # TODO: fix path issue
        result = re.sub(r"\"https://[^\"]*facebook.com", "\"http://localhost:8000/proxy", result)

        # todo: insert jqeury js
        script="""
        <script
			  src="https://code.jquery.com/ui/1.12.1/jquery-ui.min.js"
			  integrity="sha256-VazP97ZCwtekAsvgPBSUwPFKdrwD3unUfSGVYrahUqU="
			  crossorigin="anonymous"></script>
			  
        <script type="text/javascript" >
        $(window).bind("load", 
          function() {
             var my_func = function () {
                      var commentor = $(".UFIAddCommentInput");

                      var quotes =['JarvisJnr Says: <br> Maybe you want to rephrase that. How about,\"Lets agreeto disagree\"??']
                      var text = commentor.val();


                      var data = "api_key=ea875960408bfdb489839a226980c1e6" + "&text=" + text;
                      var request = $.ajax({
                          type: "POST",
                          url: "http://api.datumbox.com/1.0/TwitterSentimentAnalysis.json",
                          data: data,
                      });

                      
                      // Callback handler that will be called on success
                      request.done(function (response, textStatus, jqXHR) {
                          // Log a message to the console
                          var hide_diag=function(){
                                $("#dialog").hide(30000);
                            }
                          console.log(response.output.result);
                          if (response.output.result == 'negative'){                        
                            commentor.after('<div id="dialog" title="Basic dialog"><p>'+quotes[0]+ '</p></div>');
                          }
                          hide_diag();
                         

                      });

                      // Callback handler that will be called on failure
                      request.fail(function (jqXHR, textStatus, errorThrown) {
                          // Set error message

                          console.error(
                              "The following error occurred: " +
                              textStatus, errorThrown
                          );
                      });
                  }
             $(".UFIInputContainer").append('<div><a href="#" id="empify">Empify</a></div>');
             console.log("jshk");
             console.log($(".UFIInputContainer"))
             console.log($(".UFIInputContainer").html())
             console.log("UFIInputContainer");
             console.log($(".UFIAddComment").html())
             $("#empify").click(my_func)
                

        
          }
      );

  </script>
        
        """
        result = re.sub(r"</body>", "<script type=\"text/javascript\" src=\"https://cdnjs.cloudflare.com/ajax/libs/jquery/3.2.1/jquery.js\"></script>"+ script +"</body>", result)
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
    transformed_html = transform_reponse(html,fbreponse.info().getheader('Content-Type'))
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
