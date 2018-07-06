import copy, json, datetime
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from bot import answer 
from bot import train
from bot import run_fb_webhook
import requests


def webhook(request):
    if request.method == 'GET':
        # for fb webhook validation
        hub_mode = request.GET["hub.mode"] # "sbscribe
        hub_chanllenge = request.GET["hub.challenge"] # reutnr this value 
        hub_verify_token = request.GET["hub.verify_token"] # this should match the value in fb_credential.yaml

        if not hub_verify_tokne == 'intelleibot':
         return HttpResponse("I don't recognize you", status=400)
    elif request.method == 'POST':
    
        jsondata = json.loads(request.body)
        print(" the request body ----- {}".format(jsondata['entry']))
         
        messaging = jsondata['entry'][0]['messaging'][0]
        msg = messaging['message']['text']
        sender = messaging['sender']['id']
        result = answer(msg, sender)
        
        # TODO: iterate through the list
        resp = {}
        resp['message'] = {} 
        resp['recipient'] = result[0]['recipient_id']
        resp['message']['text'] = result[0]['text']
             
        sendMessageBacktoFB(resp)
        # FB message response is a json with the following attrivutes
        # recipient.id
        # message.text
        # message.quick_replies ( coutnent_type, title, payload, image_rl)  - content type "text", "location", "phone number", "email"
        
        return HttpResponse(status=200)
             
            
#       data = json.loads(jsondata, )
    
#       print(data["sender_id"])
#       print(data["message"])
    
#       result = answer(data["message"], data["sender_id"])
#       print("Bot says: {}".format(result))
#       return HttpResponse(result, status=200)
#        return HttpResponse('OK', status=200)
    
    return HttpResponse("Unknown method {}".format(request.method), status=500)


def sendMessageBacktoFB (message_json):
#      request({
#    uri: 'https://graph.facebook.com/v2.6/me/messages',
#    qs: { access_token: PAGE_ACCESS_TOKEN },
#    method: 'POST',
#    json: messageData
    url = 'https://graph.facebook.com/v2.6/me/messages'
    payload = message_json['access_token'] = 'EAAFDolR6SBcBAOTdzAvEDP1VjDIRhaxCc7G6T1GTmIWRmr9vPSKERgiIxeGZBfqx7BRySQ9CVZCQ09BC8SdAXOEpGOnek5I1U2zCeJOUrj7AN2ZBjaxLutVVHJg9OWfVut4uZCL90etmWrAOscr0PjU71mJKImfpgw8wRrEw6wZDZD'
 
    requests.post(url, data=json.dumps(payload))
    
    
def train_bot(request):
    train()
    
    return HttpResponse(status=200)
    
    
