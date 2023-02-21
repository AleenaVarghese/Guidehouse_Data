from django.shortcuts import render
from django.http import HttpResponse
from .forms import UserRegisterForm
from datetime import date 
from .models import User, User_Category_Groups, User_log
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView
from django.conf import settings
""" LDAP Authentication Module"""
from ldap3 import Server, Connection, ALL, SUBTREE, NTLM
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login

# Create your views here.
def user_login(request): 
    #messages.info(request, "") 
    if request.method == 'POST' and 'submit_login' in request.POST:
        server = Server('uszu3adcpwv004.internal.cloudapp.net', get_info=ALL)#chi1ads04.nciwin.local
        try:
            username=request.POST['username'].replace('nciwin\\','')
            conn = Connection(server, user="nciwin\\"+username, password=request.POST['password'], authentication=NTLM)
            if conn.bind():  
                try:
                    if User.objects.filter(username=request.POST['username']).first() :
                        #update log table
                        user_id = User.objects.filter(username=request.POST['username']).first().user_id
                        messages.success(request, f"Loggin Success!- Registred User")
                        #print(request.user.is_authenticated)
                        
                        account = User.objects.filter(username=request.POST['username']).first()
                        print("1-request.user=",request.user,request.session.get('user'))
                        request.session.user = account.username                         
                        #request.session['value'] = account.username
                        print("2-request.user=",request.user,request.session.get('user'),request.session.user)
                        print(request.user.is_authenticated) 
                        #print("-------------------------->",request.session.user)                       
                            
                        print("Loggin Success!- Registred User",user_id,"request.user=",request.user)
                        #return HttpResponseRedirect('../register')
                    else:  
                        print("Loggin Success!- But Non-Registred User")
                        messages.error(request, f"Loggin Success!- But Non-Registred User")
                        return HttpResponseRedirect('../login')
                except Exception as e:
                    print("Credentials  matching for Non-Registred User!-",e)
                    messages.error(request, f"Loggin Success!- But Non-Registred User")
                    return HttpResponseRedirect('../login')
            else:
                print(request.POST['password'],"Loggin Failed!",conn.bind())
                messages.error(request, f'Loggin Failed!') 
                return HttpResponseRedirect('../login')
        except: 
            #log e as well
            #send a server error page?
            messages.error(request, f'Cannot authenticate at this moment. Try again Later.') 
            return HttpResponseRedirect('../login')
    return render(request,'Login\login.html') 

#@login_required()
def register(request): 
    '''
    To truncate records in User table, you have to delete log table first
    '''
    category_data = User_Category_Groups.objects.all()
    if request.method == 'POST' and 'submit_new_user' in request.POST:         
        user_form = UserRegisterForm(data=request.POST)
        if user_form.is_valid() :
            user = User()
            user.user_category_id = User_Category_Groups.objects.get(user_category_id=request.POST.get('user_category_group'))
            user.username = request.POST['username']
            user.first_name = request.POST['first_name']
            user.middle_name = request.POST['middle_name']
            user.last_name = request.POST['last_name']
            user.role = request.POST['role']
            user.is_active = user_form.cleaned_data['is_active'] = 1
            user.created_date  = user_form.cleaned_data['created_date'] = date.today() 
            user.created_by = user_form.cleaned_data['created_by']= "Test User"
            user.updated_date = user_form.cleaned_data['updated_date'] = date.today() 
            user.Updated_by = user_form.cleaned_data['Updated_by'] = "Test User"
            user.save()
            #create log record 
            print("************************>>>>>>",user.user_id)
            log = User_log()
            log.user_id = User.objects.get(user_id= user.user_id)
            log.login_time = user.created_date
            log.save()
            
            messages.success(request, f'New Account has been created! The user is now able to Log In !')
            return HttpResponseRedirect('../register')
        else:
            print("---------------------------------------------->",user_form.errors)
    else:
        user_form = UserRegisterForm()
        print("############################>")        
    # Render the template depending on the context.
    return render(request,'User/register.html',{'user_form': user_form, 'category_group':category_data},)

@login_required()
def update_user(request):
    pass 

@login_required()
def List_user(request):
    pass