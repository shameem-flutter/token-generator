from django.urls import path
from . import views

urlpatterns =[
    path("generate/",views.generate_token,),
    path("track/<int:token_id>/",views.track_token),

    path("dashboard/",views.dashboard),
    path("next/",views.next_page),
    path("skip/<int:token_id>/",views.skip_token)
]