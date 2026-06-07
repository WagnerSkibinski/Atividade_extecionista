from django.contrib import admin

from .models import Beneficio, Doacao, Doador, EmpresaParceira, ResgateBeneficio


@admin.register(Doador)
class DoadorAdmin(admin.ModelAdmin):
	list_display = ("usuario", "cpf", "tipo_sanguineo", "ativo")
	search_fields = ("usuario__username", "usuario__first_name", "cpf")
	list_filter = ("tipo_sanguineo", "ativo")


@admin.register(EmpresaParceira)
class EmpresaParceiraAdmin(admin.ModelAdmin):
	list_display = ("nome", "cnpj", "contato", "ativa")
	search_fields = ("nome", "cnpj")
	list_filter = ("ativa",)


@admin.register(Beneficio)
class BeneficioAdmin(admin.ModelAdmin):
	list_display = ("titulo", "empresa", "minimo_doacoes_validadas", "ativo")
	search_fields = ("titulo", "empresa__nome")
	list_filter = ("ativo", "empresa")


@admin.register(Doacao)
class DoacaoAdmin(admin.ModelAdmin):
	list_display = ("id", "doador", "data_doacao", "status", "validada_por")
	search_fields = ("doador__usuario__username", "doador__cpf")
	list_filter = ("status", "data_doacao")


@admin.register(ResgateBeneficio)
class ResgateBeneficioAdmin(admin.ModelAdmin):
	list_display = ("doador", "beneficio", "concedido_por", "data_concessao")
	search_fields = ("doador__usuario__username", "beneficio__titulo")
	list_filter = ("beneficio", "data_concessao")
