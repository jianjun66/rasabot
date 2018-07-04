from django.http import HttpResponse
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot.trainers import ListTrainer
import re
import xmltodict
#from HTMLParser import HTMLParser
from datetime import datetime
from .list_trainer_tags import ListTrainerWithTags
import logging
import json
from django.http import JsonResponse 
import os

try:
    mongo_url = os.environ['MONGO_URL']
except:
    mongo_url = "mongodb://localhost:27017"

logging.basicConfig(level=logging.ERROR)

def trainDemo(bot):
    bot.set_trainer(ListTrainer)

    bot.train([
        'How can I help you?',
        'I need to reset my password',
        'I can certainly help you with that. For verification, could you please give me your student ID and your zip code please? ',
        'My student ID is 123456 and my zip code is 200011',
        'Thank you. You are all set. You will be receiving an email with a link to enter your new password shortly.  Is there anything else I can help you with today?',
        'No, that would be all, thanks again',
        'You are welcome. Have a good day'
        ])
    
    
#TODO: pull from DB
domains = ['monument2']
bots = {}

def initialDomainBot(domain):
    print("initial bot for domain : " + domain)
    bot = ChatBot("SmartView bot",
        storage_adapter= {
            'import_path':'mlchat.DomainMongoDatabaseAdapter',
            'database_uri': mongo_url
        },
        read_only='True',
        trainer = 'chatterbot.trainers.ChatterBotCorpusTrainer',
        logic_adapters=[
            {"import_path": "mlchat.BestMatchWithTags",
                "statement_comparison_function": "chatterbot.comparisons.levenshtein_distance",
                #"statement_comparison_function": "chatterbot.comparisons.jaccard_similarity",  #this is slow
                #"response_selection_method": "chatterbot.response_selection.get_first_response"
                "response_selection_method": "chatterbot.response_selection.get_most_frequent_response"
            },
            {'import_path': 'chatterbot.logic.LowConfidenceAdapter',
                'threshold': 0.65,
                'default_response': 'I got nothing... '
            },
            {'import_path': 'chatterbot.logic.SpecificResponseAdapter',
                'input_text': 'Help me!',
                'output_text': 'Ok, here is your help! http://www.google.com'
            }
          ],
          database="simsChat",
          domain= domain
          )
    bots[domain] =  bot
    #bot.train("chatterbot.corpus.english")
    #bot.train("chatterbot.corpus.english.greetings")
    #bot.train("chatterbot.corpus.english.conversations")
    print("Bot initialized for domain :" + domain)
    return bot

def getDomainBot(domain):
    logging.debug("get Domain Bot:" + domain)
    try:
        bot = bots[domain] #When dict has no key, will throw KeyError
        if bot is None:
            print("initial Bot:" + domain)
            bot = initialDomainBot(domain)
        return bot
    except KeyError as e:
        return initialDomainBot(domain)

for d in domains:
    bot = getDomainBot(d)

#    bot.set_trainer(ChatterBotCorpusTrainer)
    # Train based on the english corpus
#    bot.train("chatterbot.corpus.english")
#    bot.train("chatterbot.corpus.chinese")
#    bot.train("chatterbot.corpus.english.greetings")
#    bot.train("chatterbot.corpus.english.conversations")
    #print("Bot initialized for domain :" + d)
    trainDemo(bot)
#    bots[d] =  bot

#change to return a json with text and tags (list)
def answer_json(request):
    #return HttpResponse("Hello, world. You're at the polls index.")
    # Print an example of getting one math based response
    msg = request.GET['msg']
    d = request.GET['domain']
    resp = getBotResponse(d, msg)
    
    #get_class_members(resp)
    
    json_data = {}
    try:
        json_data['text'] = resp.text
    except:
        json_data['text'] = resp
    
    try: #not all statements have tags
        json_data['tags'] = resp.extra_data['tags']
    except:
        json_data['tags'] = None
    irt = []

        
    try: #not all statements have in response to, 
        if resp.in_response_to:
            for r in resp.in_response_to:
                s = {}
                s['text'] = r.text
                s['occurrence'] = r.occurrence
                irt.append(s)
        json_data['in_response_to'] = irt
    except:
        json_data['in_response_to'] = None
    

    try: #not all statements have tags
        json_data['occurrence'] = resp.get_response_count()
    except:
        json_data['occurrence'] = '-1'

    return JsonResponse(json_data, safe=False) #not to return dict

def answer(request):
    #return HttpResponse("Hello, world. You're at the polls index.")
    # Print an example of getting one math based response
    msg = request.GET['msg']
    d = request.GET['domain']
    resp = getBotResponse(d, msg)

    return HttpResponse(resp) 

def getBotResponse(d,q):
    bot = getDomainBot(d)
    #if the msg is in the format of "bot:??? ans:: ????" , then this is a training questions
    m = re.match(r'bot::(.*) ans::(.*) label::(.*) search_term::(.*)', q , re.M|re.I)
    if bot is None:
        print("Error getting bot for domain : " + d)
        return HttpResponse("Error getting bot for domain : " + d)
    
    if m:
        bot.set_trainer(ListTrainerWithTags)
        a = m.group(1)
        b = m.group(2)
        c = m.group(3)
        d = m.group(4)
        print('Training: ' + a + " : " + b +":" + c + ":" + d)
        bot.train([a, b, c, d])
        resp = "ok Master, i got it " + m.group(0)
    else:
        n = re.match(r'bot::(.*) ans::(.*)', q , re.M|re.I)
        if n:
            bot.set_trainer(ListTrainerWithTags)
            a = n.group(1)
            b = n.group(2)
            print('Training: ' + a + " : " + b )
            bot.train([a,b])
            resp = "ok Master, i got it " + n.group(0)
        else:
            resp = bot.get_response(q)
            
    return resp

#Train statement with question, answer , label[], search_term[] - one question/answer pair can have multiple tags (label and search term)
def trainStatement(d,q,a,l,s):
    bot = getDomainBot(d)
    if bot is None or q is None or a is None:
        logging.error("Error in training domain: {}, question: {} , answer: {}".format(d,q,a))
        return None
    
    bot.set_trainer(ListTrainerWithTags)
    ll = None;
    ss = None;
    if l and s: 
        logging.debug("Number of tags :{}".format(l))
        for x in range(0, len(l)):
            logging.debug("Start training with tags- {}: {}".format(q, a))
            if l[x] and s[x]:
                ll = l[x]
                ss = s[x]
            bot.train([q,a,ll,ss])
            logging.debug("training successful: {}: {} : {} : {}".format(q,a,ll,ss))
    else:
        logging.debug("Start training - {}: {}".format(q, a))
        bot.train([q,a,None, None])
        
            
    return 'OK'

def getAllStatements(d):
    bot = getDomainBot(d)
    if bot is None:
        logging.error("Error getting bot for domain {}".format(d))
        return None
    
    return bot.storage.get_response_statements()
    
    
    
#requst should have question and answer pair as post data
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def trainPair(request):
    q = request.POST['question']
    a = request.POST['answer']
    d = request.POST['domain']
    bot = getDomainBot(d)
    if bot is None:
        print("Error getting bot for domain : " + d)
        return HttpResponse("Error getting bot for domain : " + d)

    trainStatement(d,q,a,None, None);
    
    return HttpResponse("Trained from questions and answer")

#requst should have question and answer pair as post data
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def trainPairWithTag(request):
    q = request.POST['question']
    a = request.POST['answer']
    d = request.POST['domain']
    l = request.POST['label']
    s = request.POST['search_term']
    bot = getDomainBot(d)
    if bot is None:
        print("Error getting bot for domain : " + d)
        return HttpResponse("Error getting bot for domain : " + d)

    #trainStatement expect multiple labels an search terms.
    ll = [];
    ll.append(l);
    ss = [];
    ss.append(s);
    
    trainStatement(d,q,a,ll,ss);
    
    return HttpResponse("Trained from questions and answer with tags")

def trainEnglish(request):
    d = request.GET['domain']
    bot = getDomainBot(d)
    if bot is None:
        print("Error getting bot for domain : " + d)
        return HttpResponse("Error getting bot for domain : " + d)
    
    bot.set_trainer(ChatterBotCorpusTrainer)

    # Train based on the english corpus
    bot.train("chatterbot.corpus.english")
    return HttpResponse("Trained English")


def remove_tags(text):
    #replace double quote with single quote
    text = text.replace('"', '')
    text  = re.sub("<.*?>", " ", text)
    return text



def trainList(request):
    d = request.GET['domain']
    bot = getDomainBot(d)
    if bot is None:
        print("Error getting bot for domain : " + d)
        return HttpResponse("Error getting bot for domain : " + d)
    
    bot.set_trainer(ListTrainer)
    
    
    #bot.train(["FA", "You get free money from the government",])
    #bot.train(["SA", "Do you have any money left?",])
    #bot.train(["You are fired!", "Ok, Craig.",])
    #bot.train(["fired!", "Ok, Craig.",])

    with open("kb.csv", "r") as filestream:
        for line in filestream:
            currentline = line.split(",")
            print("training " + currentline[0])
            print("ANS:" + remove_tags(currentline[1]))
            bot.train([currentline[0], remove_tags(currentline[1])])
    return HttpResponse("Trained List")

# class ChatDataParser(HTMLParser):
#     def handle_data(self, data):
#         self.data = data
# 
# 
# def trainFromLPXML(request):
#     d = request.GET['domain']
#     bot = getDomainBot(d)
#     if bot is None:
#         print("Error getting bot for domain : " + d)
#         return
#     
#     bot.set_trainer(ListTrainer)
#     parser = ChatDataParser()
#     result = ''
#     lineResult = ''
#     count = 0;
#     with open('sessions_multiple.xml') as fd:
#         doc = xmltodict.parse(fd.read())
#         sessions = doc['Report']['Session']
#         for sess in sessions:
#             count += 1;
#             line = sess['Chat']['line'];
#             author = ''
#             tmpResult = ''
#             tmpAuthor = ''
#             lineResult = ''
#             result = []
#              
#             for elem in line:
#                 # if the autho is the same person, merge the lines
#                 tmpAuthor = elem['@by']
#                 if 'Text' in elem:
#                     tmpResult = elem['Text']
#                 if 'HTML' in elem:
#                     try:
#                         parser.feed(elem['HTML'])
#                         tmpResult = parser.data
#                     except TypeError:
#                         tmpResult = ''
#                         print(" ========== type error ")
#                  
#                 # print ( author + ":::" + tmpAuthor)
#                 if author == '':
#                     lineResult = tmpResult
#                     author = tmpAuthor
#                 elif tmpAuthor == author:
#                     if tmpResult is not None: 
#                         lineResult += "." + tmpResult
#                 else:
#                     result.append(lineResult)
#                     author = tmpAuthor
#                     lineResult = tmpResult
#             
#             result.append(tmpResult)
#             print(result)
#             try:
#                 bot.train(result)
#             except :
#                 print('error')                
#          
#         return HttpResponse("Session trained" + str(count))
         
def printTimestampedMessage(msg):
    print(str(datetime.now()) + msg)
    
    
## util class to print out the attriute names    
def get_class_members(klass):
    ret = dir(klass)
    if hasattr(klass,'__bases__'):
        for base in klass.__bases__:
            ret = ret + get_class_members(base)
    print("------- attibute {}".format(ret))
    return ret

