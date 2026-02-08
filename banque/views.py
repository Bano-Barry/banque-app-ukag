from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Agence, Client, Compte, Operation

"""
Views de l'application bancaire
"""


def home(request):
    """Page d'accueil avec statistiques"""
    stats = {
        'nb_agences': Agence.objects.count(),
        'nb_clients': Client.objects.count(),
        'nb_comptes': Compte.objects.count(),
        'nb_operations': Operation.objects.count(),
    }
    
    return render(request, 'banque/home.html', {'stats': stats})


def agences_list(request):
    """Liste de toutes les agences"""
    agences = Agence.objects.all()
    return render(request, 'banque/agences_list.html', {'agences': agences})


def clients_list(request):
    """Liste de tous les clients"""
    clients = Client.objects.select_related('agence').all()
    return render(request, 'banque/clients_list.html', {'clients': clients})


def comptes_list(request):
    """Liste de tous les comptes"""
    comptes = Compte.objects.select_related('client', 'client__agence').all()
    return render(request, 'banque/comptes_list.html', {'comptes': comptes})


def compte_detail(request, code):
    """Détails d'un compte avec historique"""
    compte = get_object_or_404(Compte, code=code)
    operations = compte.operations.all()[:20]
    
    context = {
        'compte': compte,
        'operations': operations,
    }
    
    return render(request, 'banque/compte_detail.html', context)


def operations_view(request):
    """Page principale des opérations bancaires"""
    comptes = Compte.objects.select_related('client').all()
    
    context = {
        'comptes': comptes,
    }
    
    return render(request, 'banque/operations.html', context)


def depot(request):
    """Effectuer un dépôt"""
    if request.method == 'POST':
        compte_code = request.POST.get('compte')
        montant = float(request.POST.get('montant'))
        
        try:
            compte = Compte.objects.get(code=compte_code)
            compte.deposer(montant)
            messages.success(request, f'Dépôt de {montant} GNF effectué avec succès sur le compte n°{compte.code}')
        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')
        
        return redirect('operations')
    
    comptes = Compte.objects.all()
    return render(request, 'banque/depot.html', {'comptes': comptes})


def retrait(request):
    """Effectuer un retrait"""
    if request.method == 'POST':
        compte_code = request.POST.get('compte')
        montant = float(request.POST.get('montant'))
        
        try:
            compte = Compte.objects.get(code=compte_code)
            compte.retirer(montant)
            messages.success(request, f'Retrait de {montant} GNF effectué avec succès sur le compte n°{compte.code}')
        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')
        
        return redirect('operations')
    
    comptes = Compte.objects.all()
    return render(request, 'banque/retrait.html', {'comptes': comptes})


def virement(request):
    """Effectuer un virement"""
    if request.method == 'POST':
        compte_source_code = request.POST.get('compte_source')
        compte_dest_code = request.POST.get('compte_dest')
        montant = float(request.POST.get('montant'))
        
        try:
            compte_source = Compte.objects.get(code=compte_source_code)
            compte_dest = Compte.objects.get(code=compte_dest_code)
            
            if compte_source.code == compte_dest.code:
                messages.error(request, 'Impossible de faire un virement vers le même compte')
            else:
                compte_source.virement(montant, compte_dest)
                messages.success(request, f'Virement de {montant} GNF effectué du compte n°{compte_source.code} vers le compte n°{compte_dest.code}')
        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')
        
        return redirect('operations')
    
    comptes = Compte.objects.all()
    return render(request, 'banque/virement.html', {'comptes': comptes})