from django.contrib import admin
from .models import Token,CompanyInfo,CompanySettings

# Register your models here.
@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display=('id','name','address')
    search_fields=('name',)


@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    list_display=('organisation','token_prefix','daily_reset','send_sms','send_whatsapp','send_push')
    list_filter=('daily_reset','send_sms','send_whatsapp','send_push')



@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display=('id','organisation','number','name','phone','created_at','is_served','is_skipped')
    list_filter=('organisation','is_served','is_skipped','created_at')
    search_fields=('name','phone')

