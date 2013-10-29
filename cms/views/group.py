from django.shortcuts import redirect, render
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from api.models import GroupForm

# Render the cms group home page if the user is logged in
@login_required
def group(request):
    groups = Group.objects.all().order_by('id')

    return render(request, 'cms/group/index.html', {'title': 'Groups', 'groups': groups})

# Render the add/edit media form or handle saving it
@login_required
def group_add_or_edit(request, id=False):
    # Is it a POST request, i.e is the form being submitted
    if request.method == 'POST':
        # If the id is not false then we are editing, so we need to
        # get an instance of that group first
        if id is not False:
            group = Group.objects.get(id=id)
            group_form = GroupForm(request.POST, instance=group)

        # Otherwise we can just pass the form data straight to the form
        else:
            group_form = GroupForm(request.POST)

        # Run through any validation rules we have
        if group_form.is_valid():
            # Save the form data to the db
            group_form.save()

            # Show a success message to the group
            message_suffix = 'added!' if id is False else 'edited'
            messages.success(request, 'Group succesfully %s' % message_suffix)

            # Redirect them back to the group home page
            return redirect('group-home')

    # Were we passed the id? i.e are we editing an object, if so get it to pass to the template
    if id is not False:
        group = Group.objects.get(id=id)
        group_form = group_form if request.method == 'POST' else GroupForm(instance=group)
        template_data = {'form': group_form, 'title': group.name}

    # If not we must be adding new group as we have no id in the URL
    else:
        group_form = group_form if request.method == 'POST' else GroupForm()
        template_data = {'form': group_form, 'title': 'Add Group'}

    return render(request, 'cms/form.html', template_data)

# Handles retrieving a group object and returning it to the template
@login_required
def group_view(request, id):
    group = Group.objects.get(id=id)

    return render(request, 'cms/group/view.html', {'group': group, 'title': group.name})
