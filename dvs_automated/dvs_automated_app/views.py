import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.shortcuts import render, redirect
import io
import sqlite3
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
     return sep.join(set(map(str, series)))

df = pd.read_csv('refined.csv')
df = df.drop_duplicates()
df = df.head(100)

#==============database testing =========================
def database_test():
     try:
          tt = pd.read_csv('refined.csv')
          print("reading direct csv")
          tt.head(5)

          cnn = sqlite3.connect('db.sqlite3')
          print('connection successful')

          tt.to_sql('myProject', cnn, if_exists='replace')
          sql = 'Select * From myProject;'
          df_read = pd.read_sql(sql, cnn)
          print(df_read.head(10))
     except Exception as e:
          print(e)
     finally:
          if cnn:
               cnn.close()
     print('done')
          

#Data filter
def filter_data(request):
     context = {
          'df': df,
          'filter_title': '',
          'listing_status': set(df['Listed']),
          'names': set(df['User Name']),
          'firms': set(df['Firm Name']),
         'years': set(df['Year']),
         'months': set(df['Month']),
         'records_found': '',
     }
     #here i want to read a csv file and store it in database
     td = df
     if request.method == 'POST':
          if 'unfiltered' in request.POST:
               context['df'] = df
          if 'listed' in request.POST:
               td1 = td[td['Listed'] == 'Y']
               context['df'] = td1
          if 'not-listed' in request.POST:
               td2 = td[td['Listed'] == 'N']
               context['df'] = td2
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

          #filtering name, firm etc.
          if 'selected_name' in request.POST:
               listing_status = request.POST['listing_status']
               name = request.POST['selected_name']
               firm = request.POST['selected_firm']
               year = request.POST['selected_year']
               month = request.POST['selected_month']

               ndf = context['df']

               if listing_status:
                    ndf = ndf[(ndf['Listed'] == listing_status)]
                    context['df'] = ndf
               if name:
                    ndf = ndf[(ndf['User Name'] == name)]
                    context['df'] = ndf
               if firm:
                    ndf = ndf[ndf['Firm Name'] == firm]
               if year:
                    year = int(year)
                    ndf = ndf[(ndf['Year'] == year)]
                    context['df'] = ndf
               if month:
                    ndf = ndf[(ndf['Month'] == month)]
                    context['df'] = ndf
               if name and year:
                    year = int(year)
                    ndf = ndf[(ndf['User Name'] == name) & (ndf['Year'] == year)]
                    context['df'] = ndf
               if name and year and month:
                    year = int(year)
                    ndf = ndf[(ndf['User Name'] == name) & (ndf['Year'] == year) & (ndf['Month'] == month)]
                    context['df'] = ndf
               if listing_status and name and year and month and firm:
                    year = int(year)
                    ndf = ndf[(ndf['Listed'] == listing_status) & (ndf['User Name'] == name) & (ndf['Year'] == year) & (ndf['Month'] == month) & (ndf['Firm Name'])]
                    context['df'] = ndf
               else:
                    context['df'] = ndf

               #for showing number of rows of filtered  data
               rows, columns = context['df'].shape
               record_spelling = ''
               if rows == 1 or rows == 0:
                    record_spelling = 'record'
               else: 
                    record_spelling = 'records'
               context['records_found'] = f'{rows} {record_spelling} found'

               #final data filtration with comma seperation, adding column to show numb of comp 
               #first-grouping the columns
               grouped_data = ndf.groupby(['User Key', 'User Name','Year', 'Month'])[['Firm Name', 'Company Name']].agg(concatenate_with_seperator)

               grouped_data = grouped_data.reset_index()

               #function for counting any cell value passed as series
               cell_value = 0
               def count_cell_values(df_column):
                    return df_column.str.count(', ')+1
               
               
               num_of_companies = count_cell_values(grouped_data['Company Name'])
               grouped_data['num_of_companies'] = num_of_companies


               context['df'] = grouped_data
               print(grouped_data)

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

def admin(request):
     grouped_data = df.groupby(['User Key', 'User Name','Year', 'Month'])[['Firm Name', 'Company Name', 'DVC Date']].agg(concatenate_with_seperator)

     grouped_data = grouped_data.reset_index()
     latest_date = grouped_data.sort_values(by='DVC Date', ascending=False)
     context = {
          'df': latest_date.head(5)
     }
     return render(request, 'admin.html', context)