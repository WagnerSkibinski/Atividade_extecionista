from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, ListView

from .forms import DoacaoForm
from .models import Beneficio, Doacao, Doador, EmpresaParceira, ResgateBeneficio


@login_required
def home(request):
	context = {
		"total_doadores": Doador.objects.count(),
		"total_doacoes": Doacao.objects.count(),
		"total_doacoes_validadas": Doacao.objects.filter(status=Doacao.STATUS_VALIDADA).count(),
		"total_empresas": EmpresaParceira.objects.filter(ativa=True).count(),
		"ultimas_doacoes": Doacao.objects.select_related("doador", "doador__usuario")[:5],
		"top_doadores": Doador.objects.annotate(
			qtd_validadas=Count("doacoes", filter=Q(doacoes__status=Doacao.STATUS_VALIDADA))
		).order_by("-qtd_validadas")[:5],
	}
	return render(request, "core/home.html", context)


class DoadorListView(LoginRequiredMixin, ListView):
	model = Doador
	template_name = "core/doador_list.html"
	context_object_name = "doadores"
	queryset = Doador.objects.select_related("usuario").order_by("usuario__first_name", "usuario__username")


class DoacaoListView(LoginRequiredMixin, ListView):
	model = Doacao
	template_name = "core/doacao_list.html"
	context_object_name = "doacoes"
	queryset = Doacao.objects.select_related("doador", "doador__usuario", "validada_por")


class DoacaoCreateView(LoginRequiredMixin, CreateView):
	model = Doacao
	form_class = DoacaoForm
	template_name = "core/doacao_form.html"
	success_url = "/doacoes/"

	def form_valid(self, form):
		messages.success(self.request, "Doacao registrada com sucesso.")
		return super().form_valid(form)


@login_required
def validar_doacao(request, doacao_id):
	if not request.user.is_staff:
		return HttpResponseForbidden("Apenas profissionais autorizados podem validar doacoes.")

	doacao = get_object_or_404(Doacao, pk=doacao_id)
	if doacao.status != Doacao.STATUS_PENDENTE:
		messages.warning(request, "Essa doacao ja foi processada.")
		return redirect("doacao-list")

	doacao.validar(request.user)
	messages.success(request, "Doacao validada com sucesso.")
	return redirect("doacao-list")


@login_required
def beneficios_disponiveis(request, doador_id):
	doador = get_object_or_404(Doador, pk=doador_id)
	total_validadas = doador.total_doacoes_validadas

	beneficios = Beneficio.objects.filter(ativo=True, empresa__ativa=True).select_related("empresa")
	beneficios_elegiveis = [
		beneficio for beneficio in beneficios if total_validadas >= beneficio.minimo_doacoes_validadas
	]

	context = {
		"doador": doador,
		"total_validadas": total_validadas,
		"beneficios_elegiveis": beneficios_elegiveis,
		"beneficios_indisponiveis": [
			beneficio for beneficio in beneficios if total_validadas < beneficio.minimo_doacoes_validadas
		],
	}
	return render(request, "core/beneficios_disponiveis.html", context)


@login_required
def conceder_beneficio(request, doador_id, beneficio_id):
	if request.method != "POST":
		return HttpResponseForbidden("Metodo nao permitido.")

	if not request.user.is_staff:
		return HttpResponseForbidden("Apenas profissionais autorizados podem conceder beneficios.")

	doador = get_object_or_404(Doador, pk=doador_id)
	beneficio = get_object_or_404(Beneficio, pk=beneficio_id, ativo=True, empresa__ativa=True)

	if doador.total_doacoes_validadas < beneficio.minimo_doacoes_validadas:
		messages.error(request, "Doador ainda nao elegivel para este beneficio.")
		return redirect("beneficios-disponiveis", doador_id=doador.pk)

	ultima_doacao_validada = doador.doacoes.filter(status=Doacao.STATUS_VALIDADA).first()
	ResgateBeneficio.objects.create(
		doador=doador,
		beneficio=beneficio,
		doacao_origem=ultima_doacao_validada,
		concedido_por=request.user,
	)
	messages.success(request, "Beneficio concedido com sucesso.")
	return redirect("beneficios-disponiveis", doador_id=doador.pk)
