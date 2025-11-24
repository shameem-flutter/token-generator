from django.contrib import admin
from .models import Token,CompanyInfo,CompanySettings, Branch

# Register your models here.
@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display=('id','name','address')
    search_fields=('name','id')
    ordering=('name',)


@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    list_display=('organisation','token_prefix','daily_reset','send_sms','send_whatsapp','send_push','open_time','close_time')
    list_filter=('daily_reset','send_sms','send_whatsapp','send_push')
    search_fields=('organisation__name','organisation__id')


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display=('name','organisation','prefix')
    list_filter=('organisation',)
    search_fields=('name','organisation__name','organisation__id')  
    ordering = ('organisation__name','name',)

    
 




@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display=('id','organisation','branches','number','name','phone','created_at','is_served','is_skipped')
    list_filter=('organisation','is_served','is_skipped','created_at','branches')
    search_fields=('name','phone','organisation__id','branches__name')
    ordering=('created_at',)

