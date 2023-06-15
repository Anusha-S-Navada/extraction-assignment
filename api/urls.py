from django.urls import path
from .views import homepage,FileUploadView

urlpatterns = [
    path('',homepage),
    path('upload/', FileUploadView.as_view(), name='upload_file'),
]