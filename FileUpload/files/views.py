import os
from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import File
from .serializers import FileSerializer
from .helpers import parse_excel, parse_pdf
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
import pandas as pd
from rest_framework.decorators import action


class FileUploadView(APIView):
    # Throttle Scope
    throttle_scope = "low"

    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Check file type and parse accordingly
        file_type = None
        # extracted_data = None
        if file.name.endswith('.xlsx') or file.name.endswith('.xls'):
            file_type = 'excel'
            # extracted_data = parse_excel(file)
        elif file.name.endswith('.pdf'):
            file_type = 'pdf'
            # extracted_data = parse_pdf(file)
        else:
            return Response({"error": "Unsupported file type. Only Excel and PDF files are allowed."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Save file and data to the database
        file_instance = File.objects.create(
            file=file,
            file_type=file_type,
            # extracted_data=extracted_data
        )
        serializer = FileSerializer(file_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FileListView(generics.ListAPIView):
    # Throttle Scope
    throttle_scope = "high"

    queryset = File.objects.all()
    serializer_class = FileSerializer


class FileDetailView(generics.RetrieveUpdateDestroyAPIView):
    # Throttle Scope
    throttle_scope = "low"

    queryset = File.objects.all()
    serializer_class = FileSerializer


class FilePreviewView(APIView):
    # Throttle Scope
    throttle_scope = "high"

    def get(self, request, pk):
        try:
            # Retrieve file instance by id
            file_instance = File.objects.get(pk=pk)

            # Check file type and parse accordingly
            if file_instance.file_type == 'excel':
                parsed_data = parse_excel(file_instance.file)
            elif file_instance.file_type == 'pdf':
                parsed_data = parse_pdf(file_instance.file)
            else:
                return Response({"error": "Unsupported file type."}, status=status.HTTP_400_BAD_REQUEST)

            # Return parsed data in JSON format
            return Response(parsed_data, status=status.HTTP_200_OK)

        except File.DoesNotExist:
            return Response({"error": "File not found."}, status=status.HTTP_404_NOT_FOUND)


class ColumnDataView(APIView):
    # Throttle Scope
    throttle_scope = "low"

    def get(self, request, pk):
        # Get file ID and column name from the request data

        file_instance = File.objects.get(pk=pk)
        df = pd.read_excel(file_instance.file)
        column_names = df.columns.to_list()
        file_name = os.path.basename(file_instance.file.name)

        return Response({"file_id": f'{file_instance.id}', "file name": f'{file_name}', "available_columns": column_names}, status=status.HTTP_201_CREATED)
    

class RowsDataView(APIView):
    # Throttle Scope
    throttle_scope = "high"

    def get(self, request, pk=None):
        # Extract the file ID and requested columns from the request data
        requested_columns = request.data.get('available_columns')
        if not requested_columns:
            return Response({"error": "No columns specified"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Fetch the file instance
        file_instance = get_object_or_404(File, pk=pk)
        
        # Load the file into a DataFrame
        df = pd.read_excel(file_instance.file)
        
        # Check if requested columns are available in the DataFrame
        missing_columns = [col for col in requested_columns if col not in df.columns]
        if missing_columns:
            return Response({
                "error": f"The following columns are not available in the file: {missing_columns}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Filter the DataFrame based on the requested columns
        filtered_df = df[requested_columns]
        
        # Convert the filtered data to a list of dictionaries (records)
        rows = filtered_df.to_dict(orient='records')
        
        return Response({
            "file_id": f"{file_instance.id}",
            "file name": os.path.basename(file_instance.file.name),
            "filtered_data": rows
        }, status=status.HTTP_200_OK)
