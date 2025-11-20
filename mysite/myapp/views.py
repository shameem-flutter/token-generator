from django.http import JsonResponse
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


def dashboard(request):
    tokens= Token.objects.all().order_by("number")
    current=Token.objects.filter(is_served=False,is_skipped=False).order_by("number").first()

    return JsonResponse({
        "current_token":current.number if current else None,
        "queue":list(tokens.values())})


def next_page(request):
    current=Token.objects.filter(is_served=False,is_skipped=False).order_by("number").first()
    if current:
        current.is_served=True
        current.save()


        return JsonResponse({"message":"Moved to next token"})
    


def skip_token(request, token_id):
    token=Token.objects.get(id=token_id)
    token.is_skipped=True
    token.save()


    return JsonResponse({"message":"Token skipped"})

