from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import uuid
import random
import string


def generate_company_id(name):
    """Generates ID like CLIN1234 or DENTAL9321"""
    prefix = ''.join(e for e in name.upper() if e.isalnum())[:5]  
    random_digits = ''.join(random.choices(string.digits, k=4))   
    return f"{prefix}{random_digits}"


class CompanyInfo(models.Model):
    id=models.CharField(primary_key=True, max_length=20,editable=False)
    name=models.CharField(max_length=200)
    address=models.TextField(null=True,blank=True)

    def save(self,*args,**kwargs):
        if not self.id:
            base_id = generate_company_id(self.name)
            while CompanyInfo.objects.filter(id=base_id).exists():
                base_id=generate_company_id(self.name)
            self.id = base_id

        super().save(*args,**kwargs)


    def __str__(self):
        return f"{self.name}({self.id})"
    

class CompanySettings(models.Model):
    organisation = models.OneToOneField(CompanyInfo, on_delete=models.CASCADE,related_name='settings')


    # working hours
    open_time = models.TimeField(null=True,blank=True)
    close_time = models.TimeField(null=True,blank=True)

    #  token prefix 
    token_prefix=models.CharField(max_length=10,default="",blank=True)

    # daily reset 
    daily_reset = models.BooleanField(default=True)


    # notification preferences
    send_sms=models.BooleanField(default=False)
    send_whatsapp =models.BooleanField(default=False)
    send_push= models.BooleanField(default=False)


    def __str__(self):
        return f"Settings for {self.organisation.name}"

class Branch(models.Model):
    organisation = models.ForeignKey(CompanyInfo, on_delete=models.CASCADE, related_name="branches")
    name = models.CharField(max_length=200)
    prefix= models.CharField(max_length=10,default="",blank=True)

    def __str__(self):
        return f"{self.name}({self.organisation.id})"


class Token(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)


    organisation = models.ForeignKey(CompanyInfo,on_delete=models.CASCADE,related_name="tokens")   
    branches= models.ForeignKey(Branch,on_delete=models.CASCADE,related_name="tokens")
    number = models.IntegerField()
    name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_served = models.BooleanField(default=False)
    is_skipped = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.branches.prefix}{self.number}"
    


    


@receiver(post_save, sender=CompanyInfo)
def create_company_settings(sender, instance, created, **kwargs):
    if created:
        CompanySettings.objects.create(organisation=instance)