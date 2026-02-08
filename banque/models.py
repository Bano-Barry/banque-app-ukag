from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

"""
Models Django pour l'application bancaire
"""


class Agence(models.Model):
    """
    Modèle Agence
    """
    code = models.CharField(max_length=50, unique=True, verbose_name="Code")
    nom = models.CharField(max_length=100, verbose_name="Nom")
    adresse = models.TextField(verbose_name="Adresse")
    
    class Meta:
        verbose_name = "Agence"
        verbose_name_plural = "Agences"
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} ({self.code})"


class Client(models.Model):
    """
    Modèle Client
    """
    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]
    
    numero = models.CharField(max_length=50, unique=True, verbose_name="Numéro")
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES, verbose_name="Sexe")
    telephone = models.CharField(max_length=20, verbose_name="Téléphone")
    
    # Relation avec Agence (une agence gère plusieurs clients)
    agence = models.ForeignKey(Agence, on_delete=models.CASCADE, related_name='clients')
    
    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['nom', 'prenom']
    
    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.numero})"


class CompteBancaire(models.Model):
    """
    Modèle abstrait CompteBancaire
    
    En Django, on utilise abstract=True dans Meta pour créer une classe abstraite
    """
    TYPE_CHOICES = [
        ('EPARGNE', 'Compte Épargne'),
        ('COURANT', 'Compte Courant'),
        ('PAYANT', 'Compte Payant'),
    ]
    
    # Le code est auto-incrémenté via AutoField (équivalent du compteur static en Java)
    code = models.AutoField(primary_key=True, verbose_name="Code")
    solde = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Solde")
    type_compte = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name="Type de compte")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    # Relation avec Client (un client possède un seul compte)
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='compte')
    
    class Meta:
        abstract = True  # Classe abstraite, ne crée pas de table
        ordering = ['code']
    
    def __str__(self):
        return f"Compte n°{self.code} - Solde: {self.solde} GNF"
    
    def deposer(self, montant):
        """Effectue un dépôt"""
        if montant <= 0:
            raise ValidationError("Le montant doit être positif.")
        
        self.solde += montant
        self.save()
        
        # Enregistrer l'opération
        Operation.objects.create(
            compte=self,
            type_operation='DEPOT',
            montant=montant,
            solde_apres=self.solde
        )
        return True
    
    def retirer(self, montant):
        """Effectue un retrait"""
        if montant <= 0:
            raise ValidationError("Le montant doit être positif.")
        
        if montant > self.solde:
            raise ValidationError(f"Solde insuffisant. Solde actuel: {self.solde} GNF")
        
        self.solde -= montant
        self.save()
        
        # Enregistrer l'opération
        Operation.objects.create(
            compte=self,
            type_operation='RETRAIT',
            montant=montant,
            solde_apres=self.solde
        )
        return True
    
    def virement(self, montant, compte_destinataire):
        """Effectue un virement vers un autre compte"""
        if montant <= 0:
            raise ValidationError("Le montant doit être positif.")
        
        # Retirer du compte source
        self.retirer(montant)
        
        # Déposer dans le compte destinataire
        compte_destinataire.deposer(montant)
        
        # Enregistrer les virements
        Operation.objects.create(
            compte=self,
            type_operation='VIREMENT_ENVOYE',
            montant=montant,
            solde_apres=self.solde
        )
        Operation.objects.create(
            compte=compte_destinataire,
            type_operation='VIREMENT_RECU',
            montant=montant,
            solde_apres=compte_destinataire.solde
        )
        return True


class CompteEpargne(models.Model):
    """
    Modèle CompteEpargne
    Hérite de CompteBancaire via OneToOneField (composition plutôt qu'héritage)
    Django ne supporte pas bien l'héritage multiple, on utilise la composition
    """
    compte = models.OneToOneField('Compte', on_delete=models.CASCADE, primary_key=True, related_name='epargne_details')
    taux_interet = models.DecimalField(max_digits=5, decimal_places=2, default=5.0, verbose_name="Taux d'intérêt (%)")
    
    class Meta:
        verbose_name = "Détails Compte Épargne"
        verbose_name_plural = "Détails Comptes Épargne"
    
    def calculer_interet(self):
        """Calcule et ajoute les intérêts au solde"""
        compte = self.compte
        interet = compte.solde * self.taux_interet / 100
        compte.solde += interet
        compte.save()
        
        # Enregistrer l'opération
        Operation.objects.create(
            compte=compte,
            type_operation='CALCUL_INTERET',
            montant=interet,
            solde_apres=compte.solde
        )
        return interet


class CompteCourant(models.Model):
    """
    Modèle CompteCourant
    """
    compte = models.OneToOneField('Compte', on_delete=models.CASCADE, primary_key=True, related_name='courant_details')
    decouvert = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Découvert autorisé")
    
    class Meta:
        verbose_name = "Détails Compte Courant"
        verbose_name_plural = "Détails Comptes Courant"
    
    def retirer(self, montant):
        """Override retirer pour tenir compte du découvert"""
        compte = self.compte
        
        if montant <= 0:
            raise ValidationError("Le montant doit être positif.")
        
        if montant > compte.solde + self.decouvert:
            raise ValidationError(
                f"Montant dépasse le solde + découvert. "
                f"Solde: {compte.solde} GNF | Découvert: {self.decouvert} GNF"
            )
        
        compte.solde -= montant
        compte.save()
        
        Operation.objects.create(
            compte=compte,
            type_operation='RETRAIT',
            montant=montant,
            solde_apres=compte.solde
        )
        return True


class ComptePayant(models.Model):
    """
    Modèle ComptePayant
    """
    compte = models.OneToOneField('Compte', on_delete=models.CASCADE, primary_key=True, related_name='payant_details')
    FRAIS_OPERATION = 15.0  # Constante
    
    class Meta:
        verbose_name = "Détails Compte Payant"
        verbose_name_plural = "Détails Comptes Payant"
    
    def deposer(self, montant):
        """Override deposer pour ajouter les frais"""
        compte = self.compte
        compte.deposer(montant)
        
        # Prélever les frais
        compte.solde -= self.FRAIS_OPERATION
        compte.save()
        
        Operation.objects.create(
            compte=compte,
            type_operation='FRAIS',
            montant=self.FRAIS_OPERATION,
            solde_apres=compte.solde
        )
        return True
    
    def retirer(self, montant):
        """Override retirer pour ajouter les frais"""
        compte = self.compte
        compte.retirer(montant)
        
        # Prélever les frais
        compte.solde -= self.FRAIS_OPERATION
        compte.save()
        
        Operation.objects.create(
            compte=compte,
            type_operation='FRAIS',
            montant=self.FRAIS_OPERATION,
            solde_apres=compte.solde
        )
        return True


class Compte(models.Model):
    """
    Modèle Compte concret
    C'est le modèle principal qui sera utilisé dans la base de données
    """
    TYPE_CHOICES = [
        ('EPARGNE', 'Compte Épargne'),
        ('COURANT', 'Compte Courant'),
        ('PAYANT', 'Compte Payant'),
    ]
    
    code = models.AutoField(primary_key=True, verbose_name="Code")
    solde = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Solde")
    type_compte = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name="Type de compte")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='compte')
    
    class Meta:
        verbose_name = "Compte"
        verbose_name_plural = "Comptes"
        ordering = ['code']
    
    def __str__(self):
        return f"Compte n°{self.code} ({self.get_type_compte_display()}) - {self.client}"
    
    def deposer(self, montant):
        """Dépôt avec gestion des frais pour ComptePayant"""
        if self.type_compte == 'PAYANT' and hasattr(self, 'payant_details'):
            return self.payant_details.deposer(montant)
        
        if montant <= 0:
            raise ValidationError("Le montant doit être positif.")
        
        self.solde += montant
        self.save()
        
        Operation.objects.create(
            compte=self,
            type_operation='DEPOT',
            montant=montant,
            solde_apres=self.solde
        )
        return True
    
    def retirer(self, montant):
        """Retrait avec gestion du découvert et des frais"""
        if self.type_compte == 'PAYANT' and hasattr(self, 'payant_details'):
            return self.payant_details.retirer(montant)
        
        if self.type_compte == 'COURANT' and hasattr(self, 'courant_details'):
            return self.courant_details.retirer(montant)
        
        if montant <= 0:
            raise ValidationError("Le montant doit être positif.")
        
        if montant > self.solde:
            raise ValidationError(f"Solde insuffisant. Solde actuel: {self.solde} GNF")
        
        self.solde -= montant
        self.save()
        
        Operation.objects.create(
            compte=self,
            type_operation='RETRAIT',
            montant=montant,
            solde_apres=self.solde
        )
        return True
    
    def virement(self, montant, compte_destinataire):
        """Virement vers un autre compte"""
        if montant <= 0:
            raise ValidationError("Le montant doit être positif.")
        
        self.retirer(montant)
        compte_destinataire.deposer(montant)
        
        Operation.objects.create(
            compte=self,
            type_operation='VIREMENT_ENVOYE',
            montant=montant,
            solde_apres=self.solde
        )
        Operation.objects.create(
            compte=compte_destinataire,
            type_operation='VIREMENT_RECU',
            montant=montant,
            solde_apres=compte_destinataire.solde
        )
        return True


class Operation(models.Model):
    """
    Modèle Operation
    """
    TYPE_OPERATION_CHOICES = [
        ('DEPOT', 'Dépôt'),
        ('RETRAIT', 'Retrait'),
        ('VIREMENT_ENVOYE', 'Virement envoyé'),
        ('VIREMENT_RECU', 'Virement reçu'),
        ('CALCUL_INTERET', 'Calcul intérêt'),
        ('FRAIS', 'Frais'),
    ]
    
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE, related_name='operations')
    type_operation = models.CharField(max_length=20, choices=TYPE_OPERATION_CHOICES, verbose_name="Type")
    montant = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Montant")
    solde_apres = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Solde après")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Date")
    
    class Meta:
        verbose_name = "Opération"
        verbose_name_plural = "Opérations"
        ordering = ['-date']  # Plus récentes en premier
    
    def __str__(self):
        return f"[{self.date.strftime('%d/%m/%Y %H:%M')}] {self.get_type_operation_display()} - {self.montant} GNF"