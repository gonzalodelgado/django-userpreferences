from django.shortcuts import render_to_response
from django.template import RequestContext
#from models import PREFERENCES
from django.contrib.auth.decorators import login_required
import os
import django.views.static
import app_settings
from django.http import HttpResponseRedirect # Http404
#from django.core.urlresolvers import reverse

@login_required
def index(request):
    if request.method=="POST":
        post = request.POST
        for key,value in post.items():
            toks = key.split(app_settings.SEPARATOR)
            if len(toks)!=2:
                continue
            app,pref = toks[0],toks[1]
            # User choice is always in first place [0].
            # Value of preference is always in second place [1]
            preferences=request.user.preferences.all()
            if preferences[app][pref][0][1] != value:
                user_preferences = request.user.preferences.preferences
                #app_pref = user_preferences.get(app)
                if not user_preferences.has_key(app):
                    user_preferences[app]={}
                if not user_preferences[app].has_key(pref):
                    user_preferences[app][pref]={}
                user_preferences[app][pref]=value
                request.user.preferences.save()
    preferences=request.user.preferences.all()
    #TODO if django version is older
    #STATIC_URL = reverse('preferences.views.media', args=[''])
    extra={
            'preferences':preferences ,
            #'STATIC_URL':STATIC_URL,
            "SEPARATOR": app_settings.SEPARATOR}
    return render_to_response('preferences.html', extra, RequestContext(request))

def media(request, path):
    """
    Serve media file directly.
    Useful only for django pre 1.3 which does not use
    django.collectstatic
    """
    parent = os.path.abspath(os.path.dirname(__file__))
    root = os.path.join(parent, 'media')
    return django.views.static.serve(request, path, root)

@login_required
def change(request,app,pref,new_value):
    return_url=request.path
    if request.method=='GET':
        if request.GET.get('return_url'):
            return_url=request.GET.get('return_url')
    preferences = request.user.preferences.preferences
    if not preferences.has_key(app):
        preferences[app]={pref:new_value}
    request.user.preferences.preferences[app][pref]=new_value
    request.user.preferences.save()
    return HttpResponseRedirect(return_url)

