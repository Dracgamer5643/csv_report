from django.shortcuts import render
import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from django.core.mail import send_mail
from django.conf import settings


@csrf_exempt
def Home(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('file', None)

        if csv_file:
            try:
                if csv_file.name.endswith('.csv'):
                    df = pd.read_csv(csv_file)
                elif csv_file.name.endswith('.xls') or csv_file.name.endswith('.xlsx'):
                    df = pd.read_excel(csv_file)
                else:
                    return JsonResponse({'error': 'Unsupported file type'}, status=400)

                summary = {
                    'num_rows': df.shape[0],
                    'num_cols': df.shape[1],
                    'columns': df.columns.tolist(),
                    'sample_data': df.head(5).to_dict(orient='records')
                }
                
                file_name = csv_file.name.split('.')[0]
                save_summary_to_file(summary, file_name)
                
                send_summary_email(file_name)

                
                response_data = {
                    'message': 'File uploaded successfully',
                    'summary': summary
                }
                
                
                return JsonResponse(response_data)

            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
        else:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
    
    return render(request, 'home.html')


def save_summary_to_file(summary, file_name):
    file_path = os.path.join(settings.MEDIA_ROOT, f"{file_name}.txt")
    
    with open(file_path, 'w') as txt_file:
        txt_file.write("Summary of uploaded data:\n\n")
        
        txt_file.write(f"Number of rows: {summary['num_rows']}\n")
        
        txt_file.write(f"Number of columns: {summary['num_cols']}\n")
        
        txt_file.write("Columns:\n")
        for column in summary['columns']:
            txt_file.write(f"- {column}\n")
        
        txt_file.write("\nSample data:\n")
        for row in summary['sample_data']:
            txt_file.write("- " + " | ".join(str(value) for value in row.values()) + "\n")

def send_summary_email(file_name):
    subject = 'Python Assignment - {Aditya Patil}'
    message = 'Please find attached the summary of uploaded data.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = ['tech@themedius.ai']

    file_path = os.path.join(settings.MEDIA_ROOT, f"{file_name}.txt")

    try:
        # Ensure the file exists
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            return

        # Read the file content
        with open(file_path, 'r') as txt_file:
            file_content = txt_file.read()

        email_message = message + "\n\n" + file_content

        # Send the email
        send_mail(subject, email_message, from_email, recipient_list, fail_silently=False)
        print("Email sent successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
