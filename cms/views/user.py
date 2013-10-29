from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from api.models import CustomUser, CustomUserForm, CustomGroup

# Render the cms user home page if the user is logged in
@login_required
def user(request):
    users = CustomUser.objects.all()

    return render(request, 'cms/user/index.html', {'title': 'Users', 'users': users})

# Render the add/edit user form or handle saving it
@login_required
def user_add_or_edit(request, id=False):
    current_user = request.user

    # Is it a POST request, i.e is the form being submitted
    if request.method == 'POST':
        # If the id is not false then we are editing, so we need to
        # get an instance of that user first
        if id is not False:
            user = CustomUser.objects.get(id=id)

            # Check the has valid permissions to edit this user
            if current_user.has_perm('auth.wina_edit_any_user') or (current_user.id == user.id and current_user.has_perm('auth.wina_edit_own_user')):
                user_form = CustomUserForm(request.POST, instance=user)

            else:
                raise PermissionDenied

        # Otherwise we can just pass the form data straight to the form, this is
        # a POST request for adding user
        else:
            # Check the user has valid permissions to add user
            if current_user.has_perm('auth.wina_add_user'):
                user_form = CustomUserForm(request.POST)

            else:
                raise PermissionDenied

        # Run through any validation rules we have
        if user_form.is_valid():
            # Save the form data to the db
            user = user_form.save()

            # Was a group set for the user?
            group_ids = request.POST.getlist('groups', False)

            # Clear the users existing group memberships, this isn't optimal
            # but it works well enough
            user.groups.clear()

            # If so add the user to that group
            if group_ids:
                for group_id in group_ids:
                    user.groups.add(CustomGroup.objects.get(id=group_id))

            # Show a success message to the user
            message_suffix = 'added!' if id is False else 'edited'
            messages.success(request, 'User succesfully %s' % message_suffix)

            # Redirect them back to the user home page
            return redirect('user-home')

    # Were we passed the id? i.e are we editing an object, if so get it to pass to the template
    if id is not False:
        user = CustomUser.objects.get(id=id)

        # Check the user has valid permissions to edit this user
        if current_user.has_perm('auth.wina_edit_any_user') or (current_user.id == user.id and current_user.has_perm('auth.wina_edit_own_user')):
            user_form = user_form if request.method == 'POST' else CustomUserForm(instance=user)
            template_data = {'form': user_form, 'title': user.first_name + ' ' + user.last_name}

        else:
            raise PermissionDenied

    # If not we must be adding new user as we have no id in the URL
    else:
        # Check the user has valid permissions to add a user
        if current_user.has_perm('auth.wina_add_user'):
            user_form = user_form if request.method == 'POST' else CustomUserForm()
            template_data = {'form': user_form, 'title': 'Add User'}

        else:
            raise PermissionDenied

    return render(request, 'cms/form.html', template_data)

# Handles retrieving a user object and returning it to the template
@login_required
def user_view(request, id):
    user = CustomUser.objects.get(id=id)

    return render(request, 'cms/user/view.html', {'user': user, 'title': user.first_name + ' ' + user.last_name})

# Handles activating another user if the current user is logged in
@login_required
def user_activate(request, id):
    # Look up the user object and get the current user
    user = CustomUser.objects.get(id=id)
    current_user = request.user

    # Check the user has valid permissions to delete this story
    if current_user.has_perm('auth.wina_activate_any_user'):
        # Activate the user
        user.is_active = True
        user.save()

        # Show a success message to the user
        messages.success(request, 'User succesfully activated!')

        # Redirect them back to the user home page
        return redirect('user-home')

    else:
        raise PermissionDenied

# Handles deactivating another user if the current user is logged in
@login_required
def user_deactivate(request, id):
    # Look up the user object and get the current user
    user = CustomUser.objects.get(id=id)
    current_user = request.user

    # Check the user has valid permissions to delete this story
    if current_user.has_perm('auth.wina_activate_any_user'):
        # Deactive the user
        user.is_active = False
        user.save()

        # Show a success message to the user
        messages.success(request, 'User succesfully deactivated!')

        # Redirect them back to the user home page
        return redirect('user-home')

    else:
        raise PermissionDenied
