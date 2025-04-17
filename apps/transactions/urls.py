from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('transactions/', views.transaction_list_view, name='transaction_list'),
    path('transactions/add/', views.transaction_create_view, name='transaction_add'),
    path('transactions/edit/<int:pk>/', views.transaction_edit_view, name='transaction_edit'),
    path('transactions/delete/<int:pk>/', views.transaction_delete_view, name='transaction_delete'),
    path('report/', views.report_view, name='report'),
    path('budgeting/', views.budgeting_view, name='budgeting'),
]
