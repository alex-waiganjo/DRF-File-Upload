# serializers.py
from rest_framework import serializers
from .models import File

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'file', 'file_type']
        # read_only_fields = ['extracted_data', ]
