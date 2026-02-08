from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('agences/', views.agences_list, name='agences_list'),
    path('clients/', views.clients_list, name='clients_list'),
    path('comptes/', views.comptes_list, name='comptes_list'),
    path('comptes/<int:code>/', views.compte_detail, name='compte_detail'),
    path('operations/', views.operations_view, name='operations'),
    path('operations/depot/', views.depot, name='depot'),
    path('operations/retrait/', views.retrait, name='retrait'),
    path('operations/virement/', views.virement, name='virement'),
]