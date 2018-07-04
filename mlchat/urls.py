from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'answer$', views.answer, name='answer'),
    url(r'answer_json$', views.answer_json, name='answer_json'),
    url(r'trainEnglish$', views.trainEnglish, name='trainEnglish'),
    url(r'trainList$', views.trainList, name='trainList'),
#    url(r'trainLP$', views.trainFromLPXML, name='trainLP'),
    url(r'trainPair$', views.trainPair, name='trainPair'),
    url(r'trainPairWithTag$', views.trainPairWithTag, name='trainPairWithTag'),
]