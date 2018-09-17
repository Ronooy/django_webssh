from django.shortcuts import render,redirect,reverse
from django.http import JsonResponse
from cssh.forms import LoginForm


def index(request):
    if request.method=='POST':
        result={'status':101,'url':None,'error':None}
        forms=LoginForm(request.POST)
        if forms.is_valid():
            request.session['ssh']=forms.get_post()
            host,*args=forms.get_post()
            result['url']=reverse('ssh:content',args=[host,])
            return  JsonResponse(result)
        result['status']=102
        result['error']=forms.errors.as_json()
        return JsonResponse(result)
    else:
        forms=LoginForm()
    return render(request,'cssh/index.html',locals())

def ssh_content(request,host_name):
    if request.session.get('ssh'):
        host, port, username, pwd=request.session.get('ssh')
        if host == host_name:
            return render(request,'cssh/ssh.html',locals())
    return redirect(reverse('ssh:index'))
