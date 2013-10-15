from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as logout_user

@login_required
def index(request):
    # Render the page
    return render(request, 'cms/index.html')

def logout(request):
    # Logout the user
    logout_user(request)

    # Redirect them to the home page
    return redirect('/')
