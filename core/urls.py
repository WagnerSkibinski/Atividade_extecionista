from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("doadores/", views.DoadorListView.as_view(), name="doador-list"),
    path("doacoes/", views.DoacaoListView.as_view(), name="doacao-list"),
    path("doacoes/nova/", views.DoacaoCreateView.as_view(), name="doacao-create"),
    path("doacoes/<int:doacao_id>/validar/", views.validar_doacao, name="doacao-validar"),
    path(
        "doadores/<int:doador_id>/beneficios/",
        views.beneficios_disponiveis,
        name="beneficios-disponiveis",
    ),
    path(
        "doadores/<int:doador_id>/beneficios/<int:beneficio_id>/conceder/",
        views.conceder_beneficio,
        name="beneficio-conceder",
    ),
]
