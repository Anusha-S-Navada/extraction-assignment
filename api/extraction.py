# install this sudo apt-get install poppler-utils
import boto3
from trp import Document
from PIL import Image
import os
from pdf2image import convert_from_path
import csv
from django.conf import settings


class SynchronousExtarct(object):
    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key
        self.textract_client = boto3.client('textract', aws_access_key_id=self.access_key,
                                            aws_secret_access_key=self.secret_key, region_name='us-east-1')

    def check_file_type(self, file_path):
        """
        Converts a given file to an image file.
        Supports file formats: PDF, TIFF, PNG, JPEG.
        If the input file is a multi-page PDF, it will convert all pages to individual image files.
        Returns the file path of the generated image file(s).
        """
        # Check the file extension
        file_name, ext = os.path.splitext(file_path)
        if ext.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
            return [file_path]

        elif ext.lower() == '.pdf':
            images_list = []
            images = convert_from_path(file_path, 300)
            for i, image in enumerate(images, start=1):
                image_name = f"{file_name}_{i}.png"
                image.save(image_name)
                images_list.append(image_name)
            return images_list

        elif ext.lower() in ['.tiff', '.tif']:
            # If the file is a TIFF, use PIL to open and convert it
            img = Image.open(file_path).convert('RGB')
            output_path = f"{file_name}.png"
            img.save(output_path, 'PNG')
            return [output_path]

        else:
            # Unsupported file type
            return []

    def analyze_document(self, file_path):
        with open(file_path, 'rb') as file:
            file_bytes = file.read()
        response = self.textract_client.analyze_document(
            Document={
                'Bytes': file_bytes
            },
            FeatureTypes=['FORMS']
        )
        # Create a Document object from the Textract response
        doc = Document(response)
        return doc

    def get_key_values(self, doc):
        fields_list = []
        for page in doc.pages:
            for field in page.form.fields:
                try:
                    if hasattr(field, 'key') and hasattr(field, 'value'):
                        fields_list.append({'Key': str(field.key), 'Value': str(field.value)})
                except Exception as e:
                    print(f"Exception in getting key values {field.key} value {field.value} {repr(e)}")

        return {'fields_list': fields_list}

    def array_of_dicts_to_csv(self,array_of_dicts, filename):
        keys = array_of_dicts[0].keys()
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys)
            writer.writeheader()
            writer.writerows(array_of_dicts)



# if __name__ == "__main__":
#     extractor = SynchronousExtarct(settings.AWS_ACCESS_KEY_ID,settings.AWS_SECRET_ACCESS_KEY)
#     file_path = "/home/keshav/PycharmProjects/assignment/img.png"
#     doc_output = extractor.analyze_document(file_path)
#     field_result = extractor.get_key_values(doc_output)
#     print(f"Field result is : {field_result['fields_list']}")
#     out_file_name = "out.csv"
#     extractor.array_of_dicts_to_csv(field_result['fields_list'],out_file_name)

