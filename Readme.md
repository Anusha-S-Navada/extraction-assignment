# Coding Assignment: Fullstack Python Engineer / Swiss Army Knife

## About script
script is located here assignment/api/extraction.py
I  did a lot of R&D to extract the contents from PDFs / Images I found out AWS Textract Form API is giving better results (Note it costs 1 cent per page)
I could have gone for alternatives like pytesseract and other libraries, but I found out form api gives more flexibility than third party libraries 


To run the script navigate to the above location before running the script u need to set aws access and secret key in .env file and also install requirements.txt otherwise it will fail 
just modify the input file path and output csv path and run the script the output will be written to CSV file

## To Run the web server
The complete web application is written in Django to run the application navigate to assignment path and run command 
**python manage.py runserver** your server will be running in port 8000
go to post man  and upload a file to /upload route it will analyse the file and send the key value pairs in API response
sample curl of req
```commandline
curl --location 'http://localhost:8000/upload/' \
--form 'file=@"/home/keshav/Desktop/sample files/sample1.pdf"'

```
Note I have done API Input validations like
1. If file size is more than 1MB I am not processing it.
2. If the file has more than 5 pages i am not processing it.
3. If the Given file format is not supported then also i am not processing it.