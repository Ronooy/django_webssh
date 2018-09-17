from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

import paramiko
import threading

from channels.layers import get_channel_layer
channel_layer = get_channel_layer()

class WebSSHThread(threading.Thread):
    def __init__(self, chan,channel_name):
        threading.Thread.__init__(self)
        self.chan = chan
        self.channel_name=channel_name

    def run(self):
        while not self.chan.shell.exit_status_ready():
            try:
                data = self.chan.shell.recv(1024)
                async_to_sync(self.chan.channel_layer.send)(self.channel_name,
                                                            {
                                                                "type": "ssh.message",
                                                                "text": data.decode()
                                                            },
                                                            )
            except Exception as ex:
                print(str(ex))
        self.chan.sshclient.close()
        return False

class EchoConsumer(WebsocketConsumer):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    def connect(self):
        if self.scope['session'].get('ssh'):
            self.sshclient = paramiko.SSHClient()
            self.sshclient.load_system_host_keys()
            self.sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.sshclient.connect(*self.scope['session']['ssh'])
            self.shell = self.sshclient.invoke_shell(term='xterm')
            t1 = WebSSHThread(self,self.channel_name)
            t1.setDaemon(True)
            t1.start()
        else:
            async_to_sync(self.channel_layer.send)(self.channel_name,
                                                   {"type": "ssh.message","text": '本次连接已失效'},)
        self.accept()

    def receive(self, text_data=None, bytes_data=None):
        try:
            self.shell.send(text_data)
        except Exception as ex:
            print(str(ex),'____EX')

    def ssh_message(self, event):
        self.send(text_data=event["text"])

    def disconnect(self, close_code):
        try:
            del self.scope['session']['ssh']
            self.scope['session'].save()
        except Exception:
            pass
        print('关闭')