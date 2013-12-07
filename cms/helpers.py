from django.contrib import messages

def can_access_cms(user):
    # if not user.is_staff
        # messages.success(request, 'derp')

    return user.is_staff
