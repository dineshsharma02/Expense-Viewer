import expenses
from os import write
from django.contrib import messages
from django.http.response import HttpResponse
from django.shortcuts import redirect, render, resolve_url
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from userpreferences.models import UserPreference
import datetime
import csv
import xlwt
from weasyprint import HTML
import tempfile
from django.db.models import Sum
from django.template.loader import render_to_string
from django.contrib.auth.models import User
 # Create your views here.
@login_required(login_url='/authentication/login')
def index(request):
    username = request.user.username
    username = username
    context = {
        'username':username,
    }
    return render(request,'index.html',context)


@login_required(login_url='/authentication/login')
def expenses(request):
    currency = UserPreference.objects.get(user=request.user).currency
    categories = Category.objects.filter(owner=request.user)
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        'currency':currency
    }
    return render(request, 'expenses/index.html', context)


def add_expense(request):
    categories = Category.objects.filter(owner=request.user)
    context = {
        'categories': categories,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'expenses/add_expense.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']
        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/add_expense.html', context)
        description = request.POST['description']
        doe = request.POST['date']
        category = request.POST['category']
        # if 'category' in request.POST:
        #     category = request.POST['category']
        # else:
        #     category = False
        Expense.objects.create(owner=request.user, amount=amount,
                               description=description, category=category, date=doe)
        messages.success(request, 'Expense added')

        return redirect('expenses')


def edit_expense(request, id):
    expense = Expense.objects.get(pk=id)
    category = Category.objects.filter(owner=request.user)
    context = {
        'expenses': expense,
        'values': expense,
        'categories': category
    }
    if request.method == 'GET':
        return render(request, 'expenses/edit_expense.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']
        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/edit_expense.html', context)
        description = request.POST['description']
        doe = request.POST['date']
        category = request.POST['category']
        # if 'category' in request.POST:
        #     category = request.POST['category']
        # else:
        #     category = False
        expense.owner = request.user
        expense.amount = amount
        expense.description = description
        expense.category = category
        expense.date = doe
        expense.save()
        messages.success(request, 'Expense updated successfully')
        return redirect('expenses')


def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, "Expense removed")
    return redirect('expenses')


def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)

        data = expenses.values()
        return JsonResponse(list(data),safe=False)


def add_category(request):
    if request.method == 'GET':
        return render(request,'expenses/add_category.html')

    else:
        name = request.POST['category_name']
        Category.objects.create(name=name,owner=request.user)
        messages.success(request, "Category created successfully")
        return redirect('add_expense')

def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_month_ago = todays_date-datetime.timedelta(days=30*6)
    expenses = Expense.objects.filter(owner=request.user,date__gte=six_month_ago,date__lte=todays_date)
    finalrep = {}

    def get_category(expenses):
        return expenses.category
    category_list = list(set(map(get_category,expenses)))     
    def get_expense_category_amount(category):
        amount=0
        filtered_by_category = expenses.filter(category = category)
        for item in  filtered_by_category:
            amount += item.amount
        return amount  

    for x in expenses:
        for y in category_list:
            finalrep[y]=get_expense_category_amount(y)      

    return JsonResponse({'expense_category_data':finalrep},safe=False)

       
def expense_stats(request):
    return render(request,'expenses/expense_stats.html')

def expense_export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Expenses' + \
        str(datetime.datetime.now())+'.csv'
    writer = csv.writer(response)
    writer.writerow(['Amount','Description','Category','Date'])
    expenses = Expense.objects.filter(owner=request.user)
    for expense in expenses:
        writer.writerow([expense.amount,expense.description,expense.category,expense.date])

    return response  

def expense_export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Expenses' + \
        str(datetime.datetime.now())+'.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expenses')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['Amount','Description','Category','Date']
    for col_num in range(len(columns)):
        ws.write(row_num,col_num,columns[col_num],font_style)
    font_style = xlwt.XFStyle()
    rows = Expense.objects.filter(owner=request.user).values_list('amount','description','category','date')        

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num,col_num,str(row[col_num]),font_style)
    wb.save(response)
    return response        

def expense_export_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; attachment; filename=Expenses' + \
        str(datetime.datetime.now())+'.pdf'
    response['Content-Transfer-Encoding'] = 'binary'    
    expenses = Expense.objects.filter(owner=request.user)
    sum = expenses.aggregate(Sum('amount'))

    html_string = render_to_string(
        'expenses/pdf_output.html',{'expenses':expenses,'total':sum['amount__sum']})
    html = HTML(string=html_string)
    result = html.write_pdf()
    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output = open(output.name,'rb')
        response.write(output.read())

    return response    



