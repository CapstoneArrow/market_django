from rest_framework import serializers
from .models import Post, Attachment


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file', 'post']


class PostSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, read_only=True)
    class Meta:
        model = Post
        fields = ['id', 'firebase_id', 'title', 'content', 'author', 'attachments']


