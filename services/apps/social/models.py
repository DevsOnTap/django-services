from django.db import models
from django.conf import settings
import sys
from django.db.models.base import ModelBase
from services import encryption
from services.utils import isDirty

class SocialNetwork(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=512)
    display_name = models.CharField(max_length=512)
    base_url = models.CharField(max_length=512)
    request_token_path = models.CharField(max_length=512, null=True)
    access_token_path = models.CharField(max_length=512, null=True)
    auth_path = models.CharField(max_length=512, null=True)
    scope_string = models.CharField(max_length=512, default='publish_stream, offline_access', blank=True)
    api_key = models.CharField(max_length=1028, null=True, help_text='This field is encrypted')
    app_secret = models.CharField(max_length=1028, null=True, help_text='This field is encrypted')
    app_id = models.CharField(max_length=1028, null=True, help_text='This field is encrypted', blank=True)
    post_url = models.CharField(max_length=1028, blank=True)
    friends_url = models.CharField(max_length=1028, blank=True)
    message_url = models.CharField(max_length=1028, blank=True)

    def request_token_url(self):
        return 'https://%s/%s?scope=%s' % (self.base_url, self.request_token_path, self.scope_string)

    def access_token_url(self):
        return 'https://%s/%s' % (self.base_url, self.access_token_path)

    def get_auth_url(self):
        return 'https://%s/%s' % (self.base_url, self.auth_path)

    def get_message_url(self):
        return 'https://%s/%s' % (self.base_url, self.message_url)

    def callback_url(self, request):
        if hasattr(settings, 'SOCIAL_PATH'):
            path = settings.SOCIAL_PATH % self.name
        else:
            path = 'social/callback/%s' % self.name

        scheme = request.META.get('HTTP_X_FORWARDED_PORT') == '443' and 'https' or 'http'
        return '%s://%s/%s/%s/' % (scheme, request.META['HTTP_HOST'], settings.URL_BASE, path)

    def get_credentials(self):
        return (self.getKey(), self.getSecret())

    def getKey(self):
        return encryption.decryptData(self.api_key)

    def getSecret(self):
        return encryption.decryptData(self.app_secret)

    def getAppId(self):
        return encryption.decryptData(self.app_id)

    def dict(self):
        return {'name': self.name,
                'display_name': self.name,
                'id': self.id}

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'socialnetwork'
        verbose_name = 'Social Network'
        verbose_name_plural = 'Social Networks'

    def save(self, *args, **kwargs):
        if not self.id:
            self.api_key = encryption.encryptData(self.api_key)
            self.app_secret = encryption.encryptData(self.app_secret)
            self.app_id = encryption.encryptData(self.app_id)
        else:
            if isDirty(self, 'api_key'):
                self.api_key = encryption.encryptData(self.api_key)

            if isDirty(self, 'app_secret'):
                self.app_secret = encryption.encryptData(self.app_secret)

            if isDirty(self, 'app_id'):
                self.app_id = encryption.encryptData(self.app_id)

        super(SocialNetwork, self).save(*args, **kwargs)



class UserNetworkCredentials(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.CharField(max_length=512, db_index=True)
    access_token = models.CharField(max_length=1028, help_text="This field is encrypted")
    profile = models.ForeignKey(settings.AUTH_PROFILE_MODULE)
    network = models.ForeignKey(SocialNetwork)
    name_in_network = models.CharField(max_length=512, default='', blank=True)
    result = models.CharField(max_length=2048, default='', blank=True)
    refresh_token = models.CharField(max_length=1028, default='')
    token_expiration = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'usernetworkcredentials'
        verbose_name = 'User Network Credentials'
        verbose_name_plural = 'User Network Credentials'

    def save(self, *args, **kwargs):
        if not self.id or isDirty(self, 'access_token'):
            self.access_token = encryption.encryptData(self.access_token)

        super(UserNetworkCredentials, self).save(*args, **kwargs)

    @property
    def token(self):
        return encryption.decryptData(self.access_token)


#ALL DEFINITION EOF
module_name = globals().get('__name__')
models = sys.modules[module_name]
models._all_ = []
for model_name in dir():
    m = getattr(models, model_name)
    if isinstance(m, ModelBase) and not m._meta.abstract:
        models._all_.append(model_name)

