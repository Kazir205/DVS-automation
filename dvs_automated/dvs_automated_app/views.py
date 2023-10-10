import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.shortcuts import render, redirect
import io
# from .forms import CSVFileForm
# from .models import CSVFile

# Create your views here.
def index(request):
    return render(request, 'index.html')   

def header(request):
     return render(request, 'header.html')


#Uploading files and displaying
def upload_csv(request):
    context = {
        "df": None,
        "show_table": False,
        "rows_column_info": "",
        "dup_message": "",
        "null_message": "",
        "updated_rows_column_info": "",
    }

    if request.method == 'POST':
        #remove duplicate
        # Check if a file is included in the request
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']

            # Read the file content into a variable
            file_content = uploaded_file.read().decode('utf-8')

            # Create a Pandas DataFrame from the file content
            df = pd.read_csv(io.StringIO(file_content), index_col=[0])
            context['df'] = df.head(50)

            #printing number of rows and columns
            rows, columns = df.shape
            print(f"data shape = {rows}, {columns}")
            context['rows_column_info'] = f"Current data has {rows} rows and {columns} columns"

            #Data cleaning------------------------------
            #handling duplicate data
            if df.duplicated().sum() == 0:
                dup_message = f"No duplicates found in the data"
            else:
                dup_message = f"Total {df.duplicated().sum()}  duplicate rows were existed. These were removed"
            
            context['dup_message'] = dup_message

            #handling null values
            sum_of_null_data = 0
            for i in df.isna().sum():
                sum_of_null_data = i + sum_of_null_data

            if sum_of_null_data == 0:
                context['null_message'] = f"No rows with empty data found"
            else:
                df = df.dropna()

                context['df'] = df.head(50)
                context['null_message'] = f"{sum_of_null_data} rows with empty data found and removed"

            #printing updated number of rows and columns
            rows, columns = df.shape
            print(f"data shape = {rows}, {columns}")
            context['update_rows_column_info'] = f"Afer cleaning, the  dataset has {rows} rows and {columns} columns"

            context['show_table'] = True

    return render(request, 'upload_csv.html', context)


#data filter
#for giving commas between data
def concatenate_with_seperator(series, sep=', '):
            return sep.join(map(str, series))   

df = pd.read_csv('merged_listed.csv')

#Data filter
def filter_data(request):
     

     context = {
          'df': df,
          'filter_title': '',
     }
     
     #here i want to read a csv file and store it in database
     if request.method == 'POST':
          if 'unfiltered' in request.POST:
               context['df'] = df
          if 'industry_filter' in request.POST:
               industry_wise = df.groupby('Business Industry')[["Company Name", "Firm Name"]].agg(concatenate_with_seperator)
               company_name = industry_wise['Company Name'].apply(lambda x: ', '.join(set(x.split(', '))))
               firm_name = industry_wise['Firm Name'].apply(lambda x: ', '.join(set(x.split(', '))))

               industry_wise['Company Name'] = company_name
               industry_wise['Firm Name'] = firm_name
               context['df'] = industry_wise
               context['filter_title'] = 'Filtered by Industry Wise'

          if 'sector_filter' in request.POST:
               sector_wise = df.groupby('business Sector')[["Company Name", "Firm Name"]].agg(concatenate_with_seperator)
               company_name = sector_wise['Company Name'].apply(lambda x: ', '.join(set(x.split(', '))))
               firm_name = sector_wise['Firm Name'].apply(lambda x: ', '.join(set(x.split(', '))))

               sector_wise['Company Name'] = company_name
               sector_wise['Firm Name'] = firm_name
               context['df'] = sector_wise
               context['filter_title'] = 'Filtered by Sector Wise'

          if 'legal_status_filter' in request.POST:
               legal_wise = df.groupby('Legal status')[["Company Name", "Firm Name"]].agg(concatenate_with_seperator)
               company_name = legal_wise['Company Name'].apply(lambda x: ', '.join(set(x.split(', '))))
               firm_name = legal_wise['Firm Name'].apply(lambda x: ', '.join(set(x.split(', '))))

               legal_wise['Company Name'] = company_name
               legal_wise['Firm Name'] = firm_name
               context['df'] = legal_wise
               context['filter_title'] = 'Filtered by Legal Wise'      
               
            
     return render(request, 'filter_data.html', context)

def chart_image_converter(chart, chart_filter):
    chart_data = chart[chart_filter].value_counts()
    plt.figure(figsize=(12, 10))  # Adjust the figure size as needed
    # Create a color palette (you can customize these colors)
    colors = ['lightblue', 'skyblue', 'deepskyblue', 'dodgerblue', 'royalblue']

    chart_data.plot(kind='barh', color=colors, edgecolor='black')
# Convert the plot to an image
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode() 

    return image_base64
   
def visualize_data(request):
     context = {}
     if request.method == "POST":
        if 'industry_chart' in request.POST:
            context = {'image_base64': chart_image_converter(df, 'Business Industry')}
        if 'sector_chart' in request.POST:
             context = {'image_base64': chart_image_converter(df, 'business Sector')}
        if 'legal_status_chart' in request.POST:
             context = {'image_base64': chart_image_converter(df, 'Legal status')}
        
     return render(request, 'visualize_data.html', context)