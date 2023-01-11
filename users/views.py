from .serializers import LogInSerializer,SignUpSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView,GenericAPIView
from rest_framework.permissions import AllowAny
# Create your views here.

class LoginAPIView(GenericAPIView):
    serializer_class = LogInSerializer
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']  # type: ignore
        token, created = Token.objects.get_or_create(user=user)
        return Response({'success':True,'token': token.key},status=status.HTTP_200_OK)

class SignUpAPIView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = SignUpSerializer
