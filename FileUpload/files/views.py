from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import File
from .serializers import FileSerializer
from .helpers import parse_excel,parse_pdf
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status


class FileUploadView(APIView):
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
    queryset = File.objects.all()
    serializer_class = FileSerializer


class FileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer


class FilePreviewView(APIView):
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
