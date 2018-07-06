import copy, json, datetime
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from bot import answer 
from bot import train
from bot import run_fb_webhook

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
        print(jsondata)
    
#       data = json.loads(jsondata, )
    
#       print(data["sender_id"])
#       print(data["message"])
    
#       result = answer(data["message"], data["sender_id"])
#       print("Bot says: {}".format(result))
#       return HttpResponse(result, status=200)
        return HttpResponse('OK', status=200)
    
    return HttpResponse("Unknown method {}".format(request.method), status=500)

def train_bot(request):
    train()
    
    return HttpResponse(status=200)
    
    
