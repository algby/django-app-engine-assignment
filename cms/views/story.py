from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from api.models import Story, StoryForm

# Render the cms story home page if the user is logged in
@login_required
def story(request):
    story = Story.objects.all()

    return render(request, 'cms/story/index.html', {'title': 'Stories', 'story': story})

# Render the add/edit media form or handle saving it
@login_required
def story_add_or_edit(request, id=False):
    # Is it a POST request, i.e is the form being submitted
    if request.method == 'POST':
        # If the id is not false then we are editing, so we need to
        # get an instance of that story first
        if id is not False:
            story = Story.objects.get(id=id)
            story_form = StoryForm(request.POST, instance=story)

        # Otherwise we can just pass the form data straight to the form
        else:
            story_form = StoryForm(request.POST)

        # Run through any validation rules we have
        if story_form.is_valid():
            # Save the form data to the db
            form = story_form.save(commit=False)
            form.author = request.user
            form.save()

            # Show a success message to the user
            message_suffix = 'added!' if id is False else 'edited'
            messages.success(request, 'Story succesfully %s' % message_suffix)

            # Redirect them back to the story home page
            return redirect('story-home')

    # Were we passed the id? i.e are we editing an object, if so get it to pass to the template
    if id is not False:
        story = Story.objects.get(id=id)
        story_form = story_form if request.method == 'POST' else StoryForm(instance=story)
        template_data = {'form': story_form, 'title': story.title}

    # If not we must be adding new story as we have no id in the URL
    else:
        story_form = story_form if request.method == 'POST' else StoryForm()
        template_data = {'form': story_form, 'title': 'Add Story'}

    return render(request, 'cms/form.html', template_data)

# Handles retrieving a story object and returning it to the template
@login_required
def story_view(request, id):
    story = Story.objects.get(id=id)

    return render(request, 'cms/story/view.html', {'story': story, 'title': story.title})


# Handles deleting a piece of story if the user is logged in
@login_required
def story_delete(request, id):
    # Look up the story object
    story = Story.objects.get(id=id)

    # Delete it from the database
    story.delete()

    # Show a success message to the user
    messages.success(request, 'Story succesfully deleted!')

    # Redirect them back to the story home page
    return redirect('story-home')
