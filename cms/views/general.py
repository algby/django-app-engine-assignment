from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as logout_user

# Render the CMS home page if the user is logged in
@login_required
def index(request):
    return render(request, 'cms/index.html', {'title': 'Welcome, %s' % request.user.first_name})

# Log out the user and redirect to them to /
def logout(request):
    # Logout the user
    logout_user(request)

    # Redirect them to the home page
    return redirect('/')
