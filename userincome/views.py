from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import Source, UserIncome
from django.core.paginator import Paginator
import json
from django.http import JsonResponse,HttpResponse
from userpreferences.models import UserPreference
import datetime
import csv
import xlwt
from weasyprint import HTML
import tempfile
from django.db.models import Sum
from django.template.loader import render_to_string
# Create your views here.


@login_required(login_url='/authentication/login')
def index(request):
    currency = UserPreference.objects.get(user=request.user).currency
    income = UserIncome.objects.filter(owner=request.user)
    paginator = Paginator(income, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    context = {
        'income': income,
        'page_obj': page_obj,
        'currency': currency
    }
    return render(request, 'income/index.html', context)


def add_income(request):
    source = Source.objects.filter(owner=request.user)
    context = {
        'sources': source,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']
        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/add_income.html', context)
        description = request.POST['description']
        doi = request.POST['date']
        source = request.POST['source']
        # if 'category' in request.POST:
        #     category = request.POST['category']
        # else:
        #     category = False
        UserIncome.objects.create(owner=request.user, amount=amount,
                                  description=description, source=source, date=doi)
        messages.success(request, 'Income added')

        return redirect('income')


def edit_income(request, id):
    income = UserIncome.objects.get(pk=id)
    source = Source.objects.filter(owner=request.user)
    context = {
        'income': income,
        'values': income,
        'source': source
    }
    if request.method == 'GET':
        return render(request, 'income/edit_income.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']
        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/edit_income.html', context)
        description = request.POST['description']
        doi = request.POST['date']
        source = request.POST['source']
        # if 'category' in request.POST:
        #     category = request.POST['category']
        # else:
        #     category = False
        income.owner = request.user
        income.amount = amount
        income.description = description
        income.source = source
        income.date = doi
        income.save()
        messages.success(request, 'Income updated successfully')
        return redirect('income')


def delete_income(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, "Income removed")
    return redirect('income')


def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        income = UserIncome.objects.filter(
            amount__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            date__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            description__icontains=search_str, owner=request.user) | UserIncome.objects.filter(
            source__icontains=search_str, owner=request.user)

        data = income.values()
        return JsonResponse(list(data), safe=False)

def add_source(request):
    if request.method == 'GET':
        return render(request,'income/add_source.html')

    else:
        name = request.POST['source_name']
        Source.objects.create(name=name,owner=request.user)
        messages.success(request, "Source created successfully")
        return redirect('add_source')


def income_source_summary(request):
    todays_date = datetime.date.today()
    six_month_ago = todays_date-datetime.timedelta(days=30*6)
    incomes = UserIncome.objects.filter(owner=request.user,date__gte=six_month_ago,date__lte=todays_date)
    finalrep = {}

    def get_source(income):
        return income.source
    source_list = list(set(map(get_source, incomes)))     
    def get_income_source_amount(source):
        amount=0
        filtered_by_source = incomes.filter(source = source)
        for item in  filtered_by_source:
            amount += item.amount
        return amount  

    for x in incomes:
        for y in source_list:
            finalrep[y]=get_income_source_amount(y)      

    return JsonResponse({'income_source_data':finalrep},safe=False)

       
def income_stats(request):
    return render(request,'income/income_stats.html')

def income_export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Income' + \
        str(datetime.datetime.now())+'.csv'
    writer = csv.writer(response)
    writer.writerow(['Amount','Description','Source','Date'])
    income = UserIncome.objects.filter(owner=request.user)
    for income in income:
        writer.writerow([income.amount,income.description,income.category,income.date])

    return response  

def income_export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Income' + \
        str(datetime.datetime.now())+'.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Income')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['Amount','Description','Source','Date']
    for col_num in range(len(columns)):
        ws.write(row_num,col_num,columns[col_num],font_style)
    font_style = xlwt.XFStyle()
    rows = UserIncome.objects.filter(owner=request.user).values_list('amount','description','source','date')        

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num,col_num,str(row[col_num]),font_style)
    wb.save(response)
    return response        

def income_export_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; attachment; filename=Income' + \
        str(datetime.datetime.now())+'.pdf'
    response['Content-Transfer-Encoding'] = 'binary'    
    income = UserIncome.objects.filter(owner=request.user)
    sum = income.aggregate(Sum('amount'))

    html_string = render_to_string(
        'income/pdf_output.html',{'income':income,'total':sum['amount__sum']})
    html = HTML(string=html_string)
    result = html.write_pdf()
    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output = open(output.name,'rb')
        response.write(output.read())

    return response            