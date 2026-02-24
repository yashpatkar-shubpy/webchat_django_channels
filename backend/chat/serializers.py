from rest_framework import serializers

class ConversationCreateSerializer(serializers.Serializer):
    TYPE_CHOICES = (
        ("private", "private"),
        ("group", "group"),
    )

    type = serializers.ChoiceField(choices=TYPE_CHOICES)
    member_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )

    def validate(self, attrs):
        conversation_type = attrs.get("type")
        member_ids = attrs.get("member_ids")

        if conversation_type == "private" and len(member_ids) != 1:
            raise serializers.ValidationError(
                "Private chat requires exactly one member."
            )

        if conversation_type == "group" and len(member_ids) < 2:
            raise serializers.ValidationError(
                "Group chat requires at least two members."
            )

        return attrs