from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Render the cms user home page if the user is logged in
@login_required
def user(request):
    return render(request, 'cms/index.html', {'title': 'Users'})

# Handles retrieving a story object and returning it to the template
@login_required
def user_view(request, id):
    return HttpResponse('yo')