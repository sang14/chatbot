from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import re
import requests
# Create your views here.

VERIFY_TOKEN='7thSeptember2016'

PAGE_ACCESS_TOKEN='EAAZAB0PBZCJQUBAJ0jm8JXArYazQPym6pwSc57gG3LNNNxbYOBYWycuXkpOylehg1XmNslgpLsMruMrsdQ5ZC9IP6oZB1MdZC8QKIr2TuYoEJYwAMA4GRFrXW7rubQHxUXImufZAASZBryKYlepQnxZBdW09xbKzZC5gKTeMvrFzlZCwZDZD'

def index(request):
    post_facebook_message('1123','hi')
    handle_postback('123224','hi')
    output_text=[0,0]
    output_text[0]=chuck()
    output_text[1]=chuck()
    
    return HttpResponse(output_text)

def chuck():
    url='https://api.chucknorris.io/jokes/random'
    resp=requests.get(url=url).text
    data=json.loads(resp)
    
    val=data['value']
    
    url_info=data['url']
    
    icon=data['icon_url']
    return val,url_info,icon
    #return data['value'],data['url'],data['icon_url']


def wikisearch(title='tomato'):
    url = 'https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles=%s'%(title)
    resp = requests.get(url=url).text
    data = json.loads(resp)
    scoped_data = data['query']['pages']
    print scoped_data
    page_id = data['query']['pages'].keys()[0]
    wiki_url = 'https://en.m.wikipedia.org/?curid=%s'%(page_id)
    try:
        wiki_content = scoped_data[page_id]['extract']
        wiki_content = re.sub(r'[^\x00-\x7F]+',' ', wiki_content)
        wiki_content = re.sub(r'\([^)]*\)', '', wiki_content)
        
        if len(wiki_content) > 315:
            wiki_content = wiki_content[:315] + ' ...'
    except KeyError:
        wiki_content = ''

    return wiki_content



def post_facebook_message(fbid,message_text):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN

    #output_text = wikisearch(message_text)
    output_text=[0,0]
    joke_link=[0,0]
    output_image=[0,0]
    output_text[0],joke_link[0],output_image[0] =chuck()
    output_text[1],joke_link[1],output_image[1] =chuck()
    #output_text=output_text.replace("Chuck Norris","Rajnikanth")
    
    response_msg_generic={
        "recipient":{
            "id":fbid
          },
          "message":{
            "attachment":{
              "type":"template",
              "payload":{
                "template_type":"generic",
                "elements":[
                  {
                    "title":output_text[0],
                    "item_url":"https://petersfancybrownhats.com",
                    "image_url":output_image[0],
                    "subtitle":"he he =D",
                    "buttons":[
                      {
                        "type":"web_url",
                        "url":joke_link[0],
                        "title":"View Website"
                      },
                      {
                        "type":"postback",
                        "title":"Another Joke",
                        "payload":"RANDOM_JOKE"
                      }              
                    ]
                  },
                  {
                    "title":output_text[1],
                    "item_url":"https://petersfancybrownhats.com",
                    "image_url":output_image[1],
                    "subtitle":"he he =D",
                    "buttons":[
                      {
                        "type":"web_url",
                        "url":joke_link[1],
                        "title":"View Website"
                      },
                      {
                        "type":"postback",
                        "title":"Another Joke",
                        "payload":"RANDOM_JOKE"
                      }              
                    ]
                  }
                ]
              }
            }
          }
    }
    response_msg_with_button={
        "recipient":{
        "id":fbid
      },
      "message":{
        "attachment":{
          "type":"template",
          "payload":{
            "template_type":"button",
            "text":output_text[0],
            "buttons":[
              {
                "type":"web_url",
                "url":joke_link[0],
                "title":"Show Website"
              },
              {
                "type":"postback",
                "title":"Start Chatting",
                "payload":"USER_DEFINED_PAYLOAD"
              }
            ]
          }
        }
      }
    } 
            
            
    
    
    #response_msg = json.dumps(response_msg_with_button)
    response_msg = json.dumps(response_msg_generic)
    #response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":output_text}})
    #status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    print status.json()

def handle_postback(fbid,payload):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    output_text='Payload Recieved: '+payload
    logg(payload,symbol="*")

    if payload=='RANDOM_JOKE':
        post_facebook_message(fbid,'foo')
    #response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":output_text}})
    #status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)

def logg(message,symbol='-'):
    print '%s\n %s \n%s'%(symbol*10,message,symbol*10)

class MyChatBotView(generic.View):
    def get(self,request,*args,**kwargs):
        if self.request.GET['hub.verify_token']==VERIFY_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('oops invalid token')

    @method_decorator(csrf_exempt)
    def dispatch(self,request,*args,**kwargs):
        return generic.View.dispatch(self,request,*args,**kwargs)

    def post(self,request,*args,**kwargs):
        incoming_message=json.loads(self.request.body.decode('utf-8'))
        print incoming_message
        logg(incoming_message)

        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                try:
                    if 'postback' in message:
                        handle_postback(message['sender']['id'],message['postback']['payload'])
                    else:
                        pass
                except Exception as e:
                    logg(e,symbol='-160-')
                #print message
                try:
                    sender_id = message['sender']['id']
                    message_text = message['message']['text']
                    post_facebook_message(sender_id,message_text) 
                    
                except Exception as e:
                    logg(e,symbol='-168-')
                    pass

        return HttpResponse() 

#def index(request):
    #return HttpResponse('Hello')

