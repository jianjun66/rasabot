import copy, json, datetime
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from bot import answer 
from bot import train
from bot import run_fb_webhook
import requests

message_hash = {}

def webhook(request):
    if request.method == 'GET':
        # for fb webhook validation
        hub_mode = request.GET["hub.mode"] # "sbscribe
        hub_chanllenge = request.GET["hub.challenge"] # reutnr this value 
        hub_verify_token = request.GET["hub.verify_token"] # this should match the value in fb_credential.yaml

        if not hub_verify_tokne == 'intelleibot':
            return HttpResponse("I don't recognize you", status=400)
        else:
            return HttpResponse(hub_challenge, status=200)

    elif request.method == 'POST':
        jsondata = json.loads(request.body)
        print('=------------------- {}'.format(jsondata))

        #TODO : iterate through messaging
        entry = jsondata['entry'][0]
        if 'messaging' in entry:
            messaging = entry['messaging'][0]
            if 'delivery' in messaging:
                print('delivery received, do nothing for now')
            elif 'read' in messaging:
                print('read received, do nothing for now')
            elif 'message' in messaging or 'postback' in messaging :
                is_postback = False
                is_echo = False
                mid = "-1"
                if 'postback' in messaging:
                    is_postback = True

                if is_postback:
                    msg = messaging['postback']['payload']
                else:
                    msg = messaging['message']['text']
                    mid = messaging['message']['mid']
                    if 'is_echo' in messaging['message']:
                        is_echo = messaging['message']['is_echo']

                sid = messaging['sender']['id']


                if not is_echo:
                    
                    #this is a hack to eliminate the duplicated message sent from FB
                    #TODO: find a better way to deal with it
                    if sid in message_hash and not is_postback and message_hash[sid] == mid : 
                       #don't do anythin
                       print("message already processed, do nothing ")
                    else :
                        #call rasabot for answer
                        print("call bot for answer for {} and message : {}".format(sid, msg))
                        result = answer(msg, sid)
                        print('response from answer {}'.format(json.dumps(result)))
                        if mid != "-1" : #postback doesn't have mid 
                            message_hash[sid] = mid
                        if result and len(result) > 0:
                            if 'data' in result[0] and len(result[0]['data']) > 0:
                                payload_data = result[0]['data'] 
                                buttons = []
                                for p in payload_data: #payload_data already contains "payload" and "title"
                                    p["type"] = "postback"
                                    buttons.append(p)
                                
                                data = {
                                    "recipient": {"id": sid},
                                    "message": {"attachment" : {"type": "template",
                                                                "payload" : { "template_type": "button", 
                                                                              "text": result[0]['text'],
                                                                              "buttons" : buttons 
                                                                            }
                                                                }
                                               }
                                                                                
                                       }
                            else:
                                data = {
                                "recipient" : { "id" : sid},
                                "message" : {"text": result[0]['text']}
                                }
                            
                            sendMessageBacktoFB(json.dumps(data))
        else:
            print('No messaging in request body')


        # FB message response is a json with the following attrivutes
        # recipient.id
        # message.text
        # message.quick_replies ( coutnent_type, title, payload, image_rl)  - content type "text", "location", "phone number", "email"
        
        return HttpResponse(status=200)
             
    return HttpResponse("Unknown method {}".format(request.method), status=500)


def sendMessageBacktoFB (message_json):

    url = 'https://graph.facebook.com/v2.6/me/messages?access_token=EAAFDolR6SBcBAOTdzAvEDP1VjDIRhaxCc7G6T1GTmIWRmr9vPSKERgiIxeGZBfqx7BRySQ9CVZCQ09BC8SdAXOEpGOnek5I1U2zCeJOUrj7AN2ZBjaxLutVVHJg9OWfVut4uZCL90etmWrAOscr0PjU71mJKImfpgw8wRrEw6wZDZD'
 
    #without this header, FB will not parse the data correctly
    headers = {'Content-Type': 'application/json'}
    
    post_response = requests.post(url, data=message_json, headers=headers)
    print(" the post response from FB is {}".format(post_response.text))
    
    
def train_bot(request):
    train()
    
    return HttpResponse(status=200)
    
    
