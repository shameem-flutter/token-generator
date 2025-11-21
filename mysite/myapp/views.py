from django.http import JsonResponse
from .models import Token, CompanyInfo
from django.shortcuts import get_object_or_404
from django.utils.timezone import localdate
# Create your views here.



def generate_token(request,org_id):
    org=get_object_or_404(CompanyInfo, id=org_id)
    settings=org.settings
    

    # daily reset
    if settings.daily_reset:
        
        today=localdate()
        last_token=Token.objects.filter(organisation=org,created_at__date=today).order_by("-number").first()

        if last_token:
            next_number=last_token.number+1
        else:
            next_number=1


    else:
        last= Token.objects.filter(organisation=org).order_by("-number").first()
        next_number= last.number+1 if last else 1


    token=Token.objects.create(organisation=org,number=next_number)


    return JsonResponse({
        "message":"Token generated",
        "token":f"{settings.token_prefix}{token.number}",
        "id":token.id,
    })


def track_token(request, token_id):
    token=get_object_or_404(Token,id=token_id)
    current=Token.objects.filter(organisation=token.organisation,is_served=False,is_skipped=False).order_by("number").first()


    return JsonResponse({
        "your_token":token.number,
        "current_token":current.number if current else None,
        "waiting":token.number - (current.number if current else 0),
        "prefix":token.organisation.settings.token_prefix
    })


def dashboard(request,org_id):
    org=get_object_or_404(CompanyInfo, id=org_id)
    tokens= Token.objects.filter(organisation=org).order_by("number")
    current=tokens.filter(is_served=False,is_skipped=False).first()

    return JsonResponse({
        "organisation":org.name,
        "prefix":org.settings.token_prefix,
        "current_token":current.number if current else None,
        "queue":list(tokens.values())})


def next_token(request,org_id):
    org= get_object_or_404(CompanyInfo, id=org_id)
    current=Token.objects.filter(organisation=org,is_served=False,is_skipped=False).order_by("number").first()
    if current:
        current.is_served=True
        current.save()

 
        return JsonResponse({"message":"Moved to next token"})
    return JsonResponse({"message":"No more active tokens"},status=400)
    



def skip_token(request,org_id, token_id):
    token=get_object_or_404(Token,id=token_id,organisation__id=org_id)
    token.is_skipped=True
    token.save()


    return JsonResponse({"message":"Token skipped"})

