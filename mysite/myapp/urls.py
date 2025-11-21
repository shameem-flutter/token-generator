from django.urls import path
from . import views

urlpatterns =[
    path("generate/<str:org_id>/",views.generate_token,),
    path("track/<uuid:token_id>/",views.track_token),

    path("dashboard/<str:org_id>/",views.dashboard),
    path("next/<str:org_id>/",views.next_token),
    path("skip/<str:org_id>/<uuid:token_id>/",views.skip_token)
]