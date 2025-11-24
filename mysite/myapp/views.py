from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import localdate, localtime
from .models import Token, CompanyInfo, Branch


def generate_token(request):
    org_id = request.GET.get("org_id")
    branch_id = request.GET.get("branch_id")

    if not org_id or not branch_id:
        return JsonResponse({"error": "org_id and branch_id are required"}, status=400)

    org = get_object_or_404(CompanyInfo, id=org_id)
    branch = get_object_or_404(Branch, id=branch_id, organisation=org)
    settings = org.settings

    now = localtime().time()

    # Working hours check
    if settings.open_time and settings.close_time:
        if not (settings.open_time <= now <= settings.close_time):
            return JsonResponse({
                "message": "Clinic is closed",
                "open_time": str(settings.open_time),
                "close_time": str(settings.close_time)
            }, status=403)

    # Daily reset (per branch)
    today = localdate()
    last_token = Token.objects.filter(
        organisation=org,
        branches=branch,
        created_at__date=today
    ).order_by("-number").first()

    next_number = last_token.number + 1 if last_token else 1

    token = Token.objects.create(
        organisation=org,
        branches=branch,
        number=next_number
    )

    return JsonResponse({
        "message": "Token generated",
        "branch": branch.name,
        "token": f"{branch.prefix}{token.number}",
        "id": token.id
    })



def track_token(request, token_id):
    token = get_object_or_404(Token, id=token_id)

    current = Token.objects.filter(
        organisation=token.organisation,
        branches=token.branches,
        is_served=False,
        is_skipped=False
    ).order_by("number").first()

    return JsonResponse({
        "your_token": token.number,
        "current_token": current.number if current else None,
        "waiting": token.number - (current.number if current else 0),
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
