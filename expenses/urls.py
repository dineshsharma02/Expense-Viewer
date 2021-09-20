from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt
urlpatterns = [
    path('', views.index,name = 'index'),
    path('expenses/', views.expenses,name = 'expenses'),
    path('add-expense/', views.add_expense,name = 'add_expense'),
    path('edit-expense/<int:id>', views.edit_expense,name = 'edit_expense'),
    path('delete-expense/<int:id>', views.delete_expense,name = 'delete_expense'),
    path('search-expenses', csrf_exempt(views.search_expenses),
         name="search_expenses"),
    path('add-category/', views.add_category,name = 'add_category'),
    path('expense_category_summary',views.expense_category_summary,name="expense_category_summary"),
    path('expense_stats',views.expense_stats,name="expense_stats"),
    path('expense-export-csv',views.expense_export_csv,name="expense_export_csv"),
    path('expense-export-excel',views.expense_export_excel,name="expense_export_excel"),
    path('expense-export-pdf',views.expense_export_pdf,name="expense_export_pdf"),

]
