from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm
from django.http import HttpResponse
from django.views import View
from tasks import create_users, send_mail_to_all_users
from forms import UserForm, EmailForm

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'templates/signup.html', {'form': form})

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error_msg = "Invalid login credentials"
            return render(request, 'templates/signin.html', {'error_msg': error_msg})
    else:
        return render(request, 'templates/signin.html')

@login_required
def signout(request):
    logout(request)
    return redirect('home')
    
@login_required
def home(request):
    return render(request, 'templates/home.html')



class CreateUsersView(View):
    """Create Users View"""

    template = 'templates/userform.html'

    def get(self, request, *args, **kwargs):
        user_form = UserForm()
        return render(request, self.template, {'user_form': user_form })

    def post(self, request, *args, **kwargs):
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            number_of_users = request.POST.get('number_of_users')
            create_users.delay(number_of_users)
            return HttpResponse("Request for creating users has been accepted")
        else:
            return HttpResponse("Please enter a valid integer")




class SendEmailView(View):
    """Send Emails View"""

    template = 'templates/sendmail.html'

    def get(self, request, *args, **kwargs):
        email_form = EmailForm()
        return render(request, self.template, {'email_form': email_form })

    def post(self, request, *args, **kwargs):
        email_form = EmailForm(request.POST)
        if email_form.is_valid():
            email_data = {
                "mail_subject":  request.POST.get("mail_subject"),
                "message": request.POST.get('message')
            }
            send_mail_to_all_users.delay(email_data)
            return HttpResponse("Request for sending mail has been accepted")
        else:
            return HttpResponse("Please enter valid input")


class HomeView(View):
    """Home page view"""

    template = 'templates/home.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template)

