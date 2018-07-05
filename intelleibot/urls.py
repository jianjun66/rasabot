from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'webhook$', views.webhook, name='webhook'),
    url(r'train$', views.train_bot, name='train'),
]