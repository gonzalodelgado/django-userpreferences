from django.db import models
from django.contrib.auth import models as auth_models
from django.utils.translation import ugettext as _
from picklefield.fields import PickledObjectField
import fields

from django.conf import settings
from preferences import app_settings


PREFERENCES={}
for app in settings.INSTALLED_APPS:
    try:
        _temp = __import__(app,globals(),locals(),['preferences'],-1)
        prefs = _temp.preferences.PREFERENCES
        PREFERENCES.update({app:prefs})
    except:
        pass

class UserPreferences(models.Model):
    user = fields.AutoOneToOneField(
            auth_models.User,
            verbose_name=_(u'User'),
            related_name='preferences',
            null=True)
    preferences = PickledObjectField(verbose_name=_(u'Preferences'), default={})

    class Meta(object):
        verbose_name=_(u'User Preferences')
        verbose_name_plural=_(u'User Preferences')

    def __unicode__(self):
        return _(u'Preferences for user %s') % self.user.username

    def __setitem__(self,key,item):
        self.preferences[key] = item

    def __getitem__(self,key):
        return self.get(key)

    def get(self,app_label):
        app_prefs = PREFERENCES.get(app_label)
        prefs={}
        for key in app_prefs:
            #0 because it's the default choice
            #1 because we want to take the key not the value
            prefs[key]=app_prefs[key][0][1]
        if not prefs:
            return {}
        user_prefs = self.preferences.get(app_label)
        if user_prefs:
            for key in user_prefs:
                if app_prefs.has_key(key):
                    #If settings not in available values don't change default
                    # if user settings contain old preferences
                    if app_settings.STRICT_CHOICES:
                        if user_prefs[key] in map(lambda x:x[1],app_prefs.get(key)):
                            prefs[key]=user_prefs[key]
                    else:
                        prefs[key] = user_prefs[key]
        return prefs

    def all(self):
        #reorders preferences to put current user preferences as first item
        preferences = PREFERENCES
        for app_label in PREFERENCES:
            user_prefs = self.preferences.get(app_label)
            if not user_prefs:
                continue
            for pref,user_value in user_prefs.items():
                if preferences[app_label].has_key(pref):
                    #Happens if old info is left in user settings
                    # FIXME: Consider app_settings.STRICT_CHOICES == False here
                    possibilities = list(preferences[app_label][pref])
                    for index,item in enumerate(possibilities):
                        if item[1] == user_value:
                            user_item = possibilities.pop(index)
                            possibilities.insert(0,user_item)
                            break
                    preferences[app_label][pref]=tuple(possibilities)
        return preferences




