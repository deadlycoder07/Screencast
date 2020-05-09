from django.shortcuts import render
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, throttle_classes,permission_classes,authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import LeaderboardSerializer,AnswerSerializer
from quiz.models import UserScore,config

# Create your views here.



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def leaderboard(request):
    players=UserScore.leaderboard(UserScore)
    serializer=LeaderboardSerializer(players,many=True)
    return Response(serializer.data)

class Answer(APIView):
    permission_classes=(IsAuthenticated,)
    serializer_class=AnswerSerializer
    
    def post(self,request):
        player=UserScore.objects.filter(user=request.user)
        context={"player":player}
        serializer = self.serializer_class(data=request.data,context=context)
        serializer.is_valid(raise_exception=True)
        response={
            'status_code':status.HTTP_200_OK,
            'result':serializer.data['result'],
        }
        return Response(response)
class GoogleLogin(APIView):
    def post(self, request):
        payload = {'access_token': request.data.get("token")}  # validate the token
        r = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', params=payload)
        data = json.loads(r.text)

        if 'error' in data:
            content = {'message': 'wrong google token / this google token is already expired.'}
            return Response(content)

        # create user if not exist
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            user = User()
            user.username = data['name']
            # provider random default password
            user.password = make_password(BaseUserManager().make_random_password())
            user.email = data['email']
            user.save()

        token = RefreshToken.for_user(user)  # generate token without username & password
        response = {}
        response['username'] = user.username
        response['access_token'] = str(token.access_token)
        response['refresh_token'] = str(token)
        return Response(response
