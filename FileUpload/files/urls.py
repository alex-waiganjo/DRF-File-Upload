from django.urls import path
from .views import FileUploadView, FileListView, FileDetailView, FilePreviewView

urlpatterns = [
    path('files/upload/', FileUploadView.as_view(), name='file-upload'),
    path('files/', FileListView.as_view(), name='file-list'),
    path('file/<int:pk>/', FileDetailView.as_view(), name='file-detail'),
    path('file/<int:pk>/preview/', FilePreviewView.as_view(), name='file-preview'),
]
