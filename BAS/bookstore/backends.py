from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

# overide the authentication method...
class EmailOrUsernameAuthenticationBackend(ModelBackend):

    # authenticate user by email/username 
    # if super user then also verify the password
    def authenticate(self, request, username=None, password=None, email=None, **kwargs):
        User = get_user_model()
        if username is None:
            if email is None:
                return None
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return None
        else:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None

        if user.is_superuser:
            if user.check_password(password):
                    return user
            else:
                return None

        return user

    #get user by user id
    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
