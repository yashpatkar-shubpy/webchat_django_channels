from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from chat.models import Conversation

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email"]

class ConversationSerializer(serializers.ModelSerializer):
    other_user_email = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ["id", "name", "created_at", "other_user_email"]

    def get_other_user_email(self, obj):
        request = self.context["request"]

        for member in obj.members.all():
            if member.id != request.user.id:
                return member.email

        return None

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(email=email, password=password)

        if user:
            attrs['user'] = user
            return attrs
        
        raise serializers.ValidationError("Invalid email or password")

class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=5, max_length=20, write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user
