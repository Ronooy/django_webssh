#!/usr/bin/env python
from django import forms
import paramiko

class LoginForm(forms.Form):
    host = forms.CharField(label='主机', widget=forms.TextInput(attrs={"class": "form-control"}))
    port = forms.CharField(label='端口', widget=forms.NumberInput(attrs={"class": "form-control",
                                                                       "min": "1", "max": "65535",
                                                                       "value": "22"}))
    username=forms.CharField(label='用户名',widget=forms.TextInput(attrs={"class":"form-control"}))
    password=forms.CharField(label='密码',widget=forms.PasswordInput(attrs={"class":"form-control"}))

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.cache=None

    def _post_clean(self):
        host=self.cleaned_data.get('host')
        port=self.cleaned_data.get('port')
        username=self.cleaned_data.get('username')
        password=self.cleaned_data.get('password')
        sshclient = paramiko.SSHClient()
        sshclient.load_system_host_keys()
        sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            sshclient.connect(host, int(port), username, password)
        except paramiko.AuthenticationException:
            self.add_error('host','账号或密码有误')
        except Exception:
            self.add_error('host', '主机地址或端口有误')
        else:
            sshclient.close()
            self.cache=(host,int(port),username,password)
        return super()._post_clean()

    def get_post(self):
        return self.cache
