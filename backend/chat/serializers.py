from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email"]

class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = [
            "id",
            "type",
            "created_at",
        ]

class GroupSerializer(serializers.Serializer):
    group_name = serializers.CharField(max_length=255)
    member_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )

    def validate_member_ids(self, value):
        request = self.context["request"]

        if request.user.id in value:
            raise serializers.ValidationError("Creator cannot be inside member_ids.")

        if len(set(value)) != len(value):
            raise serializers.ValidationError("Duplicate member ids found.")

        users_count = User.objects.filter(id__in=value).count()
        if users_count != len(value):
            raise serializers.ValidationError("One or more users do not exist.")

        return value

class PrivateSerializer(serializers.Serializer):
    member_id = serializers.IntegerField()

    def validate_member_id(self, value):
        request = self.context["request"]

        if value == request.user.id:
            raise serializers.ValidationError("You cannot create chat with yourself.")

        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User does not exist.")

        return value