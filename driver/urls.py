from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'index$', views.init, name='init'),
    url(r'manage_answers$', views.manage_answers, name='manage_answers'),
    url(r'list_statements$', views.list_statements, name='list_statements'),
]