from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import CustomUser
from .services import UserCredentials,update_credentials
from django.utils.translation import gettext_lazy as _

class LogInSerializer(serializers.Serializer):
    email = serializers.EmailField(label=_("Email"),
        write_only=True)
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label=_("Token"),
        read_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        user = update_credentials(user)
        attrs['user'] = user
        return attrs


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type':"password"},write_only=True)
    confirm_password = serializers.CharField(style={'input_type':"password"},write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id','email','password','confirm_password']
        # read_only_fields = ['credentials']
    #Validate attributes from the frontend such as password matching
    def validate(self,attrs):
        password = attrs.get('password')
        password2 = attrs.get('confirm_password')
        if password != password2:
            raise serializers.ValidationError("Password and confirm password doesn't match")
        return attrs

    def create(self, validated_data):
        del validated_data['confirm_password']
        creds = UserCredentials().fetch_initial_credentials().to_json()
        validated_data['credentials'] = creds

        return CustomUser.objects.create_user(**validated_data)

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['id','credentials','email']
        
