from rest_framework import serializers

class FileSerializer(serializers.Serializer):
    Key = serializers.CharField()
    Value = serializers.CharField()
