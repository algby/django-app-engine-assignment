from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as logout_user
from django.contrib import messages

from api.models import Media
from api.models import MediaForm

# Render the CMS home page if the user is logged in
@login_required
def index(request):
    return render(request, 'cms/index.html', {'title': 'Welcome'})

# Log out the user and redirect to them to /
def logout(request):
    # Logout the user
    logout_user(request)

    # Redirect them to the home page
    return redirect('/')

# Render the cms media home page if the user is logged in
@login_required
def media(request):
    media = Media.objects.all()

    return render(request, 'cms/index.html', {'title': 'Media', 'media': media})

# Render the manage media form or handle saving it
@login_required
def media_add(request):
    # Is it a POST request, i.e is the form being submitted
    if request.method == 'POST':
        # Pass the form all the HTTP POST data
        form = MediaForm(request.POST)

        # Run through any validation rules we have
        if form.is_valid():
            # Save the form data to the db
            form.save()

            # Show a success message to the user
            messages.success(request, 'Media succesfully added!')

            return redirect('media-home')

    # If not then just get an instance of a blank form to render
    else:
        form = MediaForm()

    return render(request, 'cms/form.html', {'form': form, 'title': 'Add Media'})

@login_required
def media_edit(request, id):
    media = Media.objects.get(id=id)
    return HttpResponse('Media ID: ' + str(media.id) + ', Title: ' + media.title)

# Render the cms story home page if the user is logged in
@login_required
def story(request):
    return render(request, 'cms/index.html', {'title': 'Stories'})

# Render the cms user home page if the user is logged in
@login_required
def user(request):
    return render(request, 'cms/index.html', {'title': 'Users'})
