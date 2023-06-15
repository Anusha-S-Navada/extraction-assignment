from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .extraction import SynchronousExtarct
import logging
import os,uuid,fitz
from .utils import removeFile
from django.conf import settings
from .serializer import FileSerializer
# Create logger for your Django app
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Create your views here.



synchronous_extraction = SynchronousExtarct(settings.AWS_ACCESS_KEY_ID,settings.AWS_SECRET_ACCESS_KEY)

@api_view(['GET'])
def homepage(request):
    return Response({'success':True,'message':"This is home page"},status=status.HTTP_200_OK)


class FileUploadView(APIView):
    def post(self, request, format=None):
        removablefiles = []
        file_obj = request.FILES.get("file")
        

        if not file_obj:
            return Response({"error":1,'message':"File required"},status=status.HTTP_400_BAD_REQUEST)

        if file_obj.size > 1000000:
            return Response({'error':1,'message':"File size should be less than 1MB"},status=status.HTTP_400_BAD_REQUEST)


        file_name,file_extension = os.path.splitext(file_obj.name)

        file_name = f'{file_name}_{uuid.uuid4()}{file_extension}'
        tmp_file_path = os.path.join('/tmp', file_name)

        logger.info(f"For input file tmp path is {tmp_file_path}")
        # initially save file in tmp folder for processing
        with open(tmp_file_path, 'wb') as f:
            for chunk in file_obj.chunks():
                f.write(chunk)

        if file_extension.lower() == ".pdf":
            # Open the PDF file
            pdf_file = fitz.open(tmp_file_path)

            # Get the number of pages in the PDF file
            num_pages = pdf_file.page_count

            # Close the PDF file
            pdf_file.close()

            if num_pages > 5:
                removeFile(tmp_file_path,logger)
                return Response({'error':1,'message':"PDF pages should be less than 5 pages"},status=status.HTTP_400_BAD_REQUEST)


        # this method will convert given pdf to png....
        initial_file_result = synchronous_extraction.check_file_type(tmp_file_path)
        logger.info(f"Initial file inspection results is {initial_file_result}")
        if not initial_file_result:
            return Response({'error':1,'message':"Given file is not supported"},status=status.HTTP_400_BAD_REQUEST)
        

        removablefiles = [tmp_file_path] + initial_file_result
        
        # this will hold per page level data
        document_data_list = []

        for page,each_image in enumerate(initial_file_result,start=1):
            # this method will call textract to detect the documents...
            doc_output = synchronous_extraction.analyze_document(each_image)
            # this will return page level fields
            field_result = synchronous_extraction.get_key_values(doc_output).get('fields_list')
            document_data_list.append(field_result)
            # to get save CSV 
            # #TODO Just explain this in video
            # csv_file_name = f"/tmp/{uuid.uuid4()}.csv"
            # synchronous_extraction.array_of_dicts_to_csv(field_result,csv_file_name)

        for each_path in removablefiles:
            removeFile(each_path,logger)

        # use comprehension to sort the data
        final_result = [data for initial_data in document_data_list for data in initial_data]
        serializer = FileSerializer(data=final_result,many=True)
        serializer.is_valid(raise_exception=True)

        return Response({'error':0,'data':serializer.data},status=status.HTTP_200_OK) 
