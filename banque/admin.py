from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Agence, Client, Compte, CompteEpargne, CompteCourant, ComptePayant, Operation

"""
Configuration de l'interface admin Django
"""


# ========== AGENCE ADMIN ==========

@admin.register(Agence)
class AgenceAdmin(admin.ModelAdmin):
    """
    Configuration de l'admin pour le modèle Agence
    """
    list_display = ['code', 'nom', 'adresse', 'nombre_clients']
    search_fields = ['code', 'nom', 'adresse']
    list_filter = ['nom']
    ordering = ['nom']
    
    fieldsets = (
        ('Informations de l\'agence', {
            'fields': ('code', 'nom', 'adresse')
        }),
    )
    
    def nombre_clients(self, obj):
        """Affiche le nombre de clients de l'agence"""
        count = obj.clients.count()
        return format_html('<b>{}</b> client(s)', count)
    
    nombre_clients.short_description = 'Nombre de clients'


# ========== CLIENT ADMIN ==========

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """
    Configuration de l'admin pour le modèle Client
    """
    list_display = ['numero', 'nom_complet', 'sexe', 'telephone', 'agence', 'a_compte', 'solde_compte']
    search_fields = ['numero', 'nom', 'prenom', 'telephone']
    list_filter = ['sexe', 'agence']
    ordering = ['nom', 'prenom']
    
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('numero', 'nom', 'prenom', 'sexe', 'telephone')
        }),
        ('Agence', {
            'fields': ('agence',)
        }),
    )
    
    def nom_complet(self, obj):
        """Affiche le nom complet du client"""
        return f"{obj.prenom} {obj.nom}"
    
    nom_complet.short_description = 'Nom complet'
    
    def a_compte(self, obj):
        """Indique si le client a un compte"""
        if hasattr(obj, 'compte'):
            return mark_safe('<span style="color: green;">✓ Oui</span>')
        return mark_safe('<span style="color: red;">✗ Non</span>')
    
    a_compte.short_description = 'Possède un compte'
    
    def solde_compte(self, obj):
        """Affiche le solde du compte s'il existe"""
        if hasattr(obj, 'compte'):
            solde = obj.compte.solde
            color = 'green' if solde >= 0 else 'red'
            return format_html('<b style="color: {};">{} GNF</b>', color, solde)
        return '-'
    
    solde_compte.short_description = 'Solde'


# ========== OPERATION INLINE (pour affichage dans Compte) ==========

class OperationInline(admin.TabularInline):
    """
    Affichage des opérations directement dans la page du compte
    """
    model = Operation
    extra = 0  # Pas de formulaire vide
    can_delete = False  # On ne peut pas supprimer les opérations
    readonly_fields = ['type_operation', 'montant', 'solde_apres', 'date']
    fields = ['date', 'type_operation', 'montant', 'solde_apres']
    ordering = ['-date']
    
    def has_add_permission(self, request, obj=None):
        """Désactive l'ajout manuel d'opérations"""
        return False


# ========== COMPTE ADMIN ==========

@admin.register(Compte)
class CompteAdmin(admin.ModelAdmin):
    """
    Configuration de l'admin pour le modèle Compte
    """
    list_display = ['code', 'client_info', 'type_compte', 'solde_colore', 'date_creation', 'nombre_operations']
    search_fields = ['code', 'client__nom', 'client__prenom', 'client__numero']
    list_filter = ['type_compte', 'date_creation']
    ordering = ['-date_creation']
    readonly_fields = ['code', 'date_creation', 'solde']
    
    inlines = [OperationInline]
    
    fieldsets = (
        ('Informations du compte', {
            'fields': ('code', 'type_compte', 'client', 'solde', 'date_creation')
        }),
    )
    
    def client_info(self, obj):
        """Affiche les infos du client"""
        return f"{obj.client.prenom} {obj.client.nom} ({obj.client.numero})"
    
    client_info.short_description = 'Client'
    
    def solde_colore(self, obj):
        """Affiche le solde avec couleur selon positif/négatif"""
        color = 'green' if obj.solde >= 0 else 'red'
        return format_html('<b style="color: {};">{} GNF</b>', color, obj.solde)
    
    solde_colore.short_description = 'Solde'
    
    def nombre_operations(self, obj):
        """Affiche le nombre d'opérations"""
        count = obj.operations.count()
        return format_html('<b>{}</b>', count)
    
    nombre_operations.short_description = 'Nb opérations'
    
    def has_delete_permission(self, request, obj=None):
        """Empêche la suppression des comptes avec opérations"""
        if obj and obj.operations.count() > 0:
            return False
        return super().has_delete_permission(request, obj)


# ========== COMPTE EPARGNE ADMIN ==========

@admin.register(CompteEpargne)
class CompteEpargneAdmin(admin.ModelAdmin):
    """
    Configuration de l'admin pour CompteEpargne
    """
    list_display = ['compte_code', 'client_nom', 'solde', 'taux_interet', 'interet_potentiel']
    search_fields = ['compte__client__nom', 'compte__client__prenom']
    readonly_fields = ['compte']
    
    fieldsets = (
        ('Compte lié', {
            'fields': ('compte',)
        }),
        ('Paramètres Épargne', {
            'fields': ('taux_interet',)
        }),
    )
    
    def compte_code(self, obj):
        return f"Compte n°{obj.compte.code}"
    
    compte_code.short_description = 'Code compte'
    
    def client_nom(self, obj):
        return f"{obj.compte.client.prenom} {obj.compte.client.nom}"
    
    client_nom.short_description = 'Client'
    
    def solde(self, obj):
        return format_html('<b>{} GNF</b>', obj.compte.solde)
    
    solde.short_description = 'Solde'
    
    def interet_potentiel(self, obj):
        """Calcule l'intérêt potentiel sans l'appliquer"""
        interet = obj.compte.solde * obj.taux_interet / 100
        return format_html('<b style="color: green;">+{} GNF</b>', interet)
    
    interet_potentiel.short_description = 'Intérêt potentiel'
    
    actions = ['calculer_interets']
    
    def calculer_interets(self, request, queryset):
        """Action pour calculer les intérêts sur les comptes sélectionnés"""
        count = 0
        for compte_epargne in queryset:
            compte_epargne.calculer_interet()
            count += 1
        
        self.message_user(request, f"Intérêts calculés pour {count} compte(s).")
    
    calculer_interets.short_description = "Calculer les intérêts"


# ========== COMPTE COURANT ADMIN ==========

@admin.register(CompteCourant)
class CompteCourantAdmin(admin.ModelAdmin):
    """
    Configuration de l'admin pour CompteCourant
    """
    list_display = ['compte_code', 'client_nom', 'solde', 'decouvert', 'disponible']
    search_fields = ['compte__client__nom', 'compte__client__prenom']
    readonly_fields = ['compte']
    
    fieldsets = (
        ('Compte lié', {
            'fields': ('compte',)
        }),
        ('Paramètres Compte Courant', {
            'fields': ('decouvert',)
        }),
    )
    
    def compte_code(self, obj):
        return f"Compte n°{obj.compte.code}"
    
    compte_code.short_description = 'Code compte'
    
    def client_nom(self, obj):
        return f"{obj.compte.client.prenom} {obj.compte.client.nom}"
    
    client_nom.short_description = 'Client'
    
    def solde(self, obj):
        color = 'green' if obj.compte.solde >= 0 else 'red'
        return format_html('<b style="color: {};">{} GNF</b>', color, obj.compte.solde)
    
    solde.short_description = 'Solde'
    
    def disponible(self, obj):
        """Affiche le montant disponible (solde + découvert)"""
        dispo = obj.compte.solde + obj.decouvert
        return format_html('<b>{} GNF</b>', dispo)
    
    disponible.short_description = 'Disponible'


# ========== COMPTE PAYANT ADMIN ==========

@admin.register(ComptePayant)
class ComptePayantAdmin(admin.ModelAdmin):
    """
    Configuration de l'admin pour ComptePayant
    """
    list_display = ['compte_code', 'client_nom', 'solde', 'frais_operation']
    search_fields = ['compte__client__nom', 'compte__client__prenom']
    readonly_fields = ['compte']
    
    fieldsets = (
        ('Compte lié', {
            'fields': ('compte',)
        }),
        ('Information', {
            'description': 'Chaque opération (dépôt/retrait) coûte 15 GNF de frais.',
            'fields': []
        }),
    )
    
    def compte_code(self, obj):
        return f"Compte n°{obj.compte.code}"
    
    compte_code.short_description = 'Code compte'
    
    def client_nom(self, obj):
        return f"{obj.compte.client.prenom} {obj.compte.client.nom}"
    
    client_nom.short_description = 'Client'
    
    def solde(self, obj):
        return format_html('<b>{} GNF</b>', obj.compte.solde)
    
    solde.short_description = 'Solde'
    
    def frais_operation(self, obj):
        return mark_safe('<b style="color: orange;">15 GNF</b>')
    
    frais_operation.short_description = 'Frais par opération'


# ========== OPERATION ADMIN ==========

@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    """
    Configuration de l'admin pour Operation
    """
    list_display = ['date_formatee', 'compte_info', 'type_operation', 'montant_colore', 'solde_apres']
    search_fields = ['compte__code', 'compte__client__nom', 'compte__client__prenom']
    list_filter = ['type_operation', 'date']
    ordering = ['-date']
    readonly_fields = ['compte', 'type_operation', 'montant', 'solde_apres', 'date']
    
    fieldsets = (
        ('Détails de l\'opération', {
            'fields': ('compte', 'type_operation', 'montant', 'solde_apres', 'date')
        }),
    )
    
    def date_formatee(self, obj):
        return obj.date.strftime('%d/%m/%Y %H:%M')
    
    date_formatee.short_description = 'Date'
    
    def compte_info(self, obj):
        return f"Compte n°{obj.compte.code} ({obj.compte.client})"
    
    compte_info.short_description = 'Compte'
    
    def montant_colore(self, obj):
        """Affiche le montant en vert pour DEPOT/VIREMENT_RECU, rouge pour les autres"""
        if obj.type_operation in ['DEPOT', 'VIREMENT_RECU', 'CALCUL_INTERET']:
            color = 'green'
            prefix = '+'
        else:
            color = 'red'
            prefix = '-'
        
        return format_html('<b style="color: {};">{}{} GNF</b>', color, prefix, obj.montant)
    
    montant_colore.short_description = 'Montant'
    
    def has_add_permission(self, request):
        """Désactive l'ajout manuel d'opérations"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Désactive la suppression d'opérations"""
        return False


# ========== PERSONNALISATION DU SITE ADMIN ==========

admin.site.site_header = "Administration Bancaire UKAG"
admin.site.site_title = "Banque UKAG Admin"
admin.site.index_title = "Gestion du système bancaire"