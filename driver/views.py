from django.http import HttpResponse
from django.template import loader
import mlchat.views
from mlchat.views import getBotResponse
import json
import logging

msg_list = []
tag_list = []
domain = ''

logging.basicConfig(level=logging.ERROR)

def init(request):
    m =request.GET.get('msg')
    domain = request.GET.get('domain')
    tag_list = []
    if m is not None:
        msg_list.append('You>' + m)
        res_json = getBotResponse(request).json()
        msg_list.append('Bot>'+ res_json['text'])
        if res_json['tags']:
            for t in res_json['tags']:
                tag_list.append(t)
        
    template = loader.get_template('index.html')
    context = {
        'msg_list' : msg_list,
        'tag_list' : tag_list,
        'domain':domain
    }
    return HttpResponse(template.render(context, request))

def manage_answers(request):
    d = request.GET.get('domain')
    q = request.GET.get('question')
    a = request.GET.get('answer')
    c = request.GET.get('tag_count');
    l = [];
    s = [];
    if c:
        for x in range(1,int(c)+1):   # tag index starts at 1
            ll = request.GET.get('tag_label_{}'.format(x))
            ss = request.GET.get('search_term_{}'.format(x))
            if ll and ss:
                l.append(ll);
                s.append(ss);

    if a is not None and q is not None:
        if mlchat.views.trainStatement(d,q,a,l,s) is None:
            return HttpResponse("Error")
    
    template = loader.get_template('manage_answers.html')
    statement_list = mlchat.views.getAllStatements(d)
    
    context = {
        'statement_list': statement_list,
        'domain' : d
    }
    return HttpResponse(template.render(context,request))

def list_statements(request):
    d = request.GET.get('domain')
    statement_list = mlchat.views.getAllStatements(d)
    
    #for s in statement_list:
    #    t = s.extra_data
    #    logging.info('statement details: {}:{}:{}'.format(s.in_response_to, s.text, t))
            
        
    template = loader.get_template('list_statements.html')
    context = {
        'statement_list' : statement_list,
        'domain': d
    }
    return HttpResponse(template.render(context, request))


#this is just for dev - as the driver and bot are in the same django. use REST call in production instead
def getBotResponse (request):
    return mlchat.views.answer_json(request)
    
        