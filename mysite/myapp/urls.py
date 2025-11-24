from django.urls import path
from . import views

urlpatterns =[
    path("generate/",views.generate_token,),
    path("dashboard/",views.dashboard),
    path("next/",views.next_token),
    path("track/<uuid:token_id>/",views.track_token),
    path("skip/<uuid:token_id>/",views.skip_token)
]