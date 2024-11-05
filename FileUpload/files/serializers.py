# serializers.py
from rest_framework import serializers
from .models import File

class FileSerializer(serializers.ModelSerializer):
    # Customize a field name
    file_name = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = ['id', 'file_name', 'file_type']

    # Extract the file name from the file path
    def get_file_name(self, obj):
        # Extract the file name from the file path
        return obj.file.name.split('/')[-1]
      
