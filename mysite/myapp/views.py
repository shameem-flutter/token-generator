from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import localdate
from .models import Token, CompanyInfo, Branch
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime



def make_aware_time(t):
    """
    t = naive Python time (from settings.open_time / close_time)
    Convert it into aware datetime → then extract time
    """
    dt = datetime.combine(timezone.localdate(), t)  # naive datetime
    aware_dt = timezone.make_aware(dt)              # aware datetime
    return timezone.localtime(aware_dt).time()      # aware time


@csrf_exempt
def generate_token(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    org_id = request.GET.get("org_id")
    name = (request.POST.get("name") or "").strip()
    phone = (request.POST.get("phone") or "").strip().replace(" ", "")
    branch_id = request.POST.get("branch_id")

    if not org_id:
        return JsonResponse({"error": "org_id is required"}, status=400)

    if not branch_id:
        return JsonResponse({"error": "branch_id is required"}, status=400)

    if not name or not phone:
        return JsonResponse({"error": "name and phone are required"}, status=400)

    org = get_object_or_404(CompanyInfo, id=org_id)
    branch = get_object_or_404(Branch, id=branch_id, organisation=org)
    settings = org.settings

    # Always timezone-aware
    now = timezone.localtime(timezone.now()).time()
    print("DEBUG SERVER TIME =", now)

    # ------- WORKING HOURS CHECK FIXED -------
    if settings.open_time and settings.close_time:

        open_time = make_aware_time(settings.open_time)
        close_time = make_aware_time(settings.close_time)

        if not (open_time <= now <= close_time):
            return JsonResponse({
                "message": "Clinic is closed",
                "open_time": str(settings.open_time),
                "close_time": str(settings.close_time)
            }, status=403)

    # Daily limit check
    today = localdate()

    phone_count = Token.objects.filter(
        organisation=org,
        branches=branch,
        phone=phone,
        created_at__date=today
    ).count()

    if phone_count >= 2:
        return JsonResponse({
            "message": "Limit reached: only 2 tokens per day",
            "phone": phone
        }, status=403)
    
    MAX_TOKENS_PER_DAY = 10

    today_tokens = Token.objects.filter(
    organisation=org,
    branches=branch,
    created_at__date=today
).count()
    

    if today_tokens >= MAX_TOKENS_PER_DAY:
        return JsonResponse({
        "message": f"Daily limit of {MAX_TOKENS_PER_DAY} tokens reached",
        "branch": branch.name
    }, status=403)


    # Generate next token
    last_token = Token.objects.filter(
        organisation=org,
        branches=branch,
        created_at__date=today
    ).order_by("-number").first()

    next_number = last_token.number + 1 if last_token else 1

    token = Token.objects.create(
        organisation=org,
        branches=branch,
        number=next_number,
        name=name,
        phone=phone
    )

    return JsonResponse({
        "message": "Token generated",
        "branch": branch.name,
        "token": f"{branch.prefix}{token.number}",
        "id": token.id,
        "name": token.name,
        "phone": token.phone
    })


def track_token(request, token_id):
    token = get_object_or_404(Token, id=token_id)

    current = Token.objects.filter(
        organisation=token.organisation,
        branches=token.branches,
        is_served=False,
        is_skipped=False
    ).order_by("number").first()

    waiting = max(0, token.number - (current.number if current else 0))

    return JsonResponse({
        "your_token": token.number,
        "current_token": current.number if current else None,
        "waiting": waiting,
        "prefix": token.branches.prefix,
        "branch": token.branches.name
    })


def dashboard(request):
    org_id = request.GET.get("org_id")
    branch_id = request.GET.get("branch_id")

    if not org_id or not branch_id:
        return JsonResponse({"error": "org_id and branch_id are required"}, status=400)

    org = get_object_or_404(CompanyInfo, id=org_id)
    branch = get_object_or_404(Branch, id=branch_id, organisation=org)

    tokens = Token.objects.filter(
        organisation=org,
        branches=branch
    ).order_by("number")

    current = tokens.filter(is_served=False, is_skipped=False).first()

    return JsonResponse({
        "organisation": org.name,
        "branch": branch.name,
        "prefix": branch.prefix,
        "current_token": current.number if current else None,
        "queue": list(tokens.values())
    })


def next_token(request):
    org_id = request.GET.get("org_id")
    branch_id = request.GET.get("branch_id")

    if not org_id or not branch_id:
        return JsonResponse({"error": "org_id and branch_id are required"}, status=400)

    org = get_object_or_404(CompanyInfo, id=org_id)
    branch = get_object_or_404(Branch, id=branch_id, organisation=org)

    current = Token.objects.filter(
        organisation=org,
        branches=branch,
        is_served=False,
        is_skipped=False
    ).order_by("number").first()

    if not current:
        return JsonResponse({"message": "No more active tokens"}, status=400)

    current.is_served = True
    current.save()

    return JsonResponse({"message": "Moved to next token"})


def skip_token(request, token_id):
    org_id = request.GET.get("org_id")
    branch_id = request.GET.get("branch_id")

    token = get_object_or_404(Token, id=token_id)

    if str(token.organisation.id) != str(org_id) or str(token.branches.id) != str(branch_id):
        return JsonResponse({"error": "Token does not belong to this organisation/branch"}, status=403)

    token.is_skipped = True
    token.save()

    return JsonResponse({"message": "Token skipped"})
