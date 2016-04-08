# Create your views here.
import facebook
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from account.models import UserProfile
from account.models import UserToken
from account.serializers import UserProfileSerializer, LoginSerializer


class AccountViewSet(viewsets.GenericViewSet):
    serializer_class = LoginSerializer

    @list_route(methods=['POST'])
    def login(self, request):
        """
        Logs in the user.
        ---
        request_serializer: LoginSerializer
        """
        serialized_data = LoginSerializer(data=request.data)
        if serialized_data.is_valid():
            access_token = serialized_data.validated_data['access_token']

            graph = facebook.GraphAPI(access_token=access_token, version='2.5')

            try:
                fb_user = graph.get_object('me?fields=id,first_name,last_name,picture,email')
            except facebook.GraphAPIError:
                return Response({'success': False, 'message': 'Invalid token'}, status=HTTP_400_BAD_REQUEST)

            user, created = User.objects.get_or_create(username=fb_user['id'])
            user_profile, profile_created = UserProfile.objects.get_or_create(user=user)

            if created:
                user.set_unusable_password()

            user.first_name = fb_user['first_name']
            user.last_name = fb_user['last_name']

            if 'picture' in fb_user:
                user_profile.picture = fb_user['picture']['data']['url']

            if 'email' in fb_user:
                user.email = fb_user['email']

            user.save()
            user_profile.save()

            user_token = UserToken.objects.create(user=user)
            return Response(
                    {
                        'success': True,
                        'token': user_token.token.hex,
                        'uid': User.objects.get(email=user.email).pk,
                    }
            )

        return Response(serialized_data.errors, status=HTTP_400_BAD_REQUEST)
