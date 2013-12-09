from api.models import WinaUser

# Basic middleware to patch the users avatar into the requset.user object
class UserAvatarMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated():
            # Not optimal but we need to look up the user again so we have access
            # to the get_avatar function
            user = WinaUser.objects.get(id=request.user.id)

            # Add it to the requset.user object
            request.user.avatar = user.get_avatar()
