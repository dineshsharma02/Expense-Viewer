from decimal import Context
from userpreferences.models import UserPreference
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
import json
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage, message
from django.contrib import auth
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from .utils import token_generator
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core import mail
import threading


# Create your views here.
class EmailThread(threading.Thread):
    def __init__(self,email):
        self.email = email
        threading.Thread.__init__(self)
    def run(self):
        self.email.send(fail_silently=False)     


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({'username_error': 'username should only contain alphanumeric characters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'Sorry this username already exits,try something different!'}, status=409)
        return JsonResponse({'username_valid': True})


class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse({'email_error': 'Please enter correct email!!'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'Sorry this email already exits,please login with this email.'}, status=409)
        return JsonResponse({'email_valid': True})


class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')

    def post(self, request):
        # get user data
        # validate
        # create user
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = {
            'fieldValues': request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, "Password too short")
                    return render(request, 'authentication/register.html', context)
            user = User.objects.create_user(username=username, email=email)
            user.set_password(password)
            user.is_active = False
            user.save()
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            domain = get_current_site(request).domain
            link = reverse('activate', kwargs={
                           'uidb64': uidb64, 'token': token_generator.make_token(user)})
            activate_url = 'http://'+domain+link
            email_subject = "Activate your account"
            email_body = "Hello "+user.username + \
                " Please activate your account using this link:\n"+activate_url

            email = EmailMessage(
                email_subject,
                email_body,
                'noreply@semicolon.com',

                [email],

            )
            EmailThread(email).start()


            messages.success(request, "Account created successfully!")
            messages.success(request, "Check your email and click on the link to activate your account.")
            return render(request, 'authentication/register.html')

        return render(request, 'authentication/register.html')


class VerifivationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)
            if not token_generator.check_token(user, token):
                return redirect('login'+'?messge='+'User already activated')
            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()
            messages.success(request, 'Account activated successfully')
            return redirect('login')
        except Exception as ex:
            pass
        return redirect('login')


class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        if username and password:
            user = auth.authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    auth.login(request, user)
                    if UserPreference.DoesNotExist():
                        return redirect('general')
                    messages.success(request, "Welcome " +
                                     user.username+", Now you are logged in")
                    return redirect('expenses')
                messages.error(
                    request, "Please activate your account from your email.")
                return render(request, 'authentication/login.html')
            messages.error(request, "Invalid credentials!please try again.")
            return render(request, 'authentication/login.html')
        messages.error(request, "Please fill details!")
        return render(request, 'authentication/login.html')

class LogoutView(View):
    def post(self,request):
        auth.logout(request)
        messages.success(request,"You have successfully logged out!")
        return redirect('login')


class RequestPasswordResetEmail(View):
    def get(self,request):
        return render(request,'authentication/reset-password.html')

    def post(self,request):
        
        email = request.POST['email']
        
        context = {
            'values': request.POST
        }
        if not validate_email(email):
            messages.error("Please enter a correct email")
            return render(request,'authentication/reset-password.html',context)
        domain = get_current_site(request).domain
        user = User.objects.filter(email=email)
        if user.exists():
            
            email_contents = {
                'user': user[0],
                'domain': domain,
                'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token': PasswordResetTokenGenerator().make_token(user[0])

            }
            print(user[0])
            
            link = reverse('reset-user-password', kwargs={
                            'uidb64': email_contents['uid'], 'token': email_contents['token']})
            
            email_subject = "Password reset link"
            reset_url = 'http://'+domain+link

            email = EmailMessage(
                email_subject,
                'Hi there, Please click the link below to reset your password \n'+reset_url,
                'noreply@semicolon.com',

                [email],

            )
            
            EmailThread(email).start()
            
            messages.success(request,"We have sent you an email to reset your password")
        else:
            messages.error(request,"This email is not registered.Please register your account first!")
            return render(request,'authentication/reset-password.html',context)    
        return render(request,'authentication/reset-password.html')               

class CompletePasswordReset(View):
    def get(self,request,uidb64,token):
        context = {
            'uidb64':uidb64,
            'token':token
        }
        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            if not PasswordResetTokenGenerator().check_token(user,token):
                messages.info(request,"Link is invalid,Please request for new link!") 
                return render(request,'authentication/reset-password.html')               

        except Exception as identifier:
            pass
        return render(request,'authentication/set_new_password.html',context)

    def post(self,request,uidb64,token):
        context = {
            'uidb64':uidb64,
            'token':token
        }
        password = request.POST['password']
        password2 = request.POST['password2']
        if password != password2:
            messages.error(request,"Passwords do not match.Please try again")
            return render(request,'authentication/set_new_password.html',context)
        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()  
            messages.success(request,"Password successfully changed,Now you can login with new password.")
            return redirect('login')

        except Exception as identifier:
            messages.info(request,"Something went wrong, please try again")
            return render(request,'authentication/set_new_password.html',context)

