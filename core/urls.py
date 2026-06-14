from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("brindes/<int:beneficio_id>/", views.beneficio_detalhe, name="beneficio-detalhe"),
    path("brindes/<int:beneficio_id>/resgatar/", views.resgatar_beneficio, name="beneficio-resgatar"),
    path("cadastro/", views.cadastro, name="cadastro"),
    path("cadastro-empresa/", views.cadastro_empresa, name="cadastro-empresa"),
    path("gerenciar-empresa/", views.gerenciar_empresa, name="gerenciar-empresa"),
    path("cadastro-empresa/brinde/", views.cadastro_brinde, name="cadastro-brinde"),
    path("meu-perfil/", views.meu_perfil, name="meu-perfil"),
    path("meus-beneficios/", views.meus_beneficios, name="meus-beneficios"),
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
