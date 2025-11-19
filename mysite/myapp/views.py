from django.shortcuts import render
from .models import Token
# Create your views here.



def generate_token(request):
    """Generate next token  number"""
    last=Token.objects.order_by("-number").first()
    next_number=last.number+1 if last else 1

    token=Token.objects.create(number=next_number)


    return JsonResponse({
        "message":"Token generated",
        "token":token.number,
        "id":token.id,
    })


def track_token(request, token_id):
    token=Token.objects.get(id=token_id)
    current=Token.objects.filter(is_served=False,is_skipped=False).order_by("number").first()


    return JsonResponse({
        "your_token":token.number,
        "current_token":current.number if current else None,
        "waiting":token.number-(current.number if current else 0),
    })
