import copy, json, datetime
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from bot import answer 
from bot import train
from bot import run_fb_webhook

@csrf_exempt
@require_POST
def webhook(request):
    jsondata = request.body
    data = json.loads(jsondata, )
    
    print(data["sender_id"])
    print(data["message"])
    
    result = answer(data["message"], data["sender_id"])
    print("Bot says: {}".format(result))
    return HttpResponse(result, status=200)


@csrf_exempt
@require_POST
def fb_webhook(request):
    jsondata = request.body
    data = json.loads(jsondata, )
    
    print(data["sender_id"])
    print(data["message"])
    
    result = run_fb_webhook()
    print("Bot says: {}".format(result))
    return HttpResponse(result, status=200)

def train_bot(request):
    train()
    
    return HttpResponse(status=200)
    
    