from django.db import models
from django.utils import timezone
import uuid


class CompanyInfo(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)
    name=models.CharField(max_length=200)
    address=models.TextField(null=True,blank=True)


    def __str__(self):
        return self.name
    

class CompanySettings(models.Model):
    organization = models.OneToOneField(CompanyInfo, on_delete=models.CASCADE,related_name='settings')


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
        return f"Settings for {self.organization.name}"



class Token(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)


    organisation = models.ForeignKey(CompanyInfo,on_delete=models.CASCADE,related_name="tokens")   
    number = models.IntegerField()
    name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_served = models.BooleanField(default=False)
    is_skipped = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.organisation.settings.token_prefix}({self.number})"
