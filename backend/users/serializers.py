from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = 
    class Meta:
        model = User
        fields = ('avatar',)