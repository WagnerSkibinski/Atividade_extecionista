from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, ListView

from .forms import CadastroBrindeForm, CadastroDoadorForm, CadastroEmpresaForm, ComprovacaoDoacaoForm, DoacaoForm, GerenciarEmpresaForm
from .models import BannerPropaganda, Beneficio, Doacao, Doador, EmpresaParceira, ResgateBeneficio


class StaffRequiredMixin(UserPassesTestMixin):
	raise_exception = True

	def test_func(self):
		return self.request.user.is_staff



# def home,
def home(request):
	if request.user.is_authenticated and not request.session.get("empresa_cadastro_id"):
		empresa_usuario = EmpresaParceira.objects.filter(usuario=request.user).first()
		if empresa_usuario:
			request.session["empresa_cadastro_id"] = empresa_usuario.pk

	doador_logado = Doador.objects.filter(usuario=request.user).first() if request.user.is_authenticated else None
	banner_topo = BannerPropaganda.objects.filter(ativo=True).first()
	beneficios = Beneficio.objects.filter(ativo=True, empresa__ativa=True).select_related("empresa")

	beneficios_publicos = []
	for beneficio in beneficios:
		elegivel = bool(
			doador_logado and doador_logado.total_doacoes_validadas >= 1
		)
		beneficios_publicos.append(
			{
				"beneficio": beneficio,
				"elegivel": elegivel,
			}
		)

	context = {
        # veificar <>
		"banner_topo": banner_topo,
		"empresas": EmpresaParceira.objects.filter(ativa=True),
		"beneficios_publicos": beneficios_publicos,
		"doador_logado": doador_logado,
	}
	return render(request, "core/home.html", context)


# view de cadastro (forms)
def cadastro(request):
	if request.user.is_authenticated:
		return redirect("home")

	if request.method == "POST":
		cadastro_form = CadastroDoadorForm(request.POST)
		if cadastro_form.is_valid():
			user = cadastro_form.save()
			login(request, user)
			messages.success(request, "Cadastro realizado com sucesso. Agora voce ja pode acompanhar seus beneficios.")
			return redirect("home")
	else:
		cadastro_form = CadastroDoadorForm()

	return render(request, "core/cadastro.html", {"cadastro_form": cadastro_form})

#  view de cadastro de empresa (forms) (testar att.2.0)
def cadastro_empresa(request):
	if request.user.is_authenticated:
		empresa_usuario = EmpresaParceira.objects.filter(usuario=request.user).first()
		if empresa_usuario:
			request.session["empresa_cadastro_id"] = empresa_usuario.pk
			return redirect("gerenciar-empresa")

	if request.method == "POST":
		empresa_form = CadastroEmpresaForm(request.POST)
		if empresa_form.is_valid():
			empresa = empresa_form.save()
			login(request, empresa.usuario)
			request.session["empresa_cadastro_id"] = empresa.pk
			messages.success(
				request,
				f"Conta da empresa {empresa.nome} criada com sucesso. Agora adicione seu primeiro brinde.",
			)
			return redirect("gerenciar-empresa")
	else:
		empresa_form = CadastroEmpresaForm()

    # verificar request do endpoit<>
	return render(request, "core/cadastro_empresa.html", {"empresa_form": empresa_form})


def gerenciar_empresa(request):
	empresa_id = request.session.get("empresa_cadastro_id")
	if not empresa_id:
		messages.warning(request, "Cadastre sua empresa antes de gerenciar o perfil.")
		return redirect("cadastro-empresa")

	empresa = get_object_or_404(EmpresaParceira, pk=empresa_id)

	if request.method == "POST":
		perfil_form = GerenciarEmpresaForm(request.POST, request.FILES, instance=empresa)
		if perfil_form.is_valid():
			perfil_form.save()
			messages.success(request, "Perfil da empresa atualizado com sucesso.")
			return redirect("gerenciar-empresa")
	else:
		perfil_form = GerenciarEmpresaForm(instance=empresa)

	beneficios = empresa.beneficios.filter(ativo=True)
	return render(
		request,
		"core/gerenciar_empresa.html",
		{"empresa": empresa, "perfil_form": perfil_form, "beneficios": beneficios},
	)

# View cadastro de produtos como brinde 
def cadastro_brinde(request):
	empresa_id = request.session.get("empresa_cadastro_id")
	if not empresa_id:
		messages.warning(request, "Cadastre sua empresa antes de adicionar brindes.")
		return redirect("cadastro-empresa")
    # revisar<>
	empresa = get_object_or_404(EmpresaParceira, pk=empresa_id)

	if request.method == "POST":
		brinde_form = CadastroBrindeForm(request.POST, request.FILES)
		if brinde_form.is_valid():
			beneficio = brinde_form.save(empresa)
			messages.success(
				request,
				f"Brinde '{beneficio.titulo}' anunciado com sucesso para {empresa.nome}.",
			)
			return redirect("home")
	else:
		brinde_form = CadastroBrindeForm()

	return render(
		request,
		"core/cadastro_brinde.html",
		{"empresa": empresa, "brinde_form": brinde_form},
	)


def beneficio_detalhe(request, beneficio_id):
	beneficio = get_object_or_404(Beneficio, pk=beneficio_id, ativo=True, empresa__ativa=True)
	doador_logado = Doador.objects.filter(usuario=request.user).first() if request.user.is_authenticated else None
	elegivel = bool(doador_logado and doador_logado.total_doacoes_validadas >= 1)
	ja_resgatado = bool(
		doador_logado
		and ResgateBeneficio.objects.filter(doador=doador_logado, beneficio=beneficio).exists()
	)

	context = {
		"beneficio": beneficio,
		"doador_logado": doador_logado,
		"elegivel": elegivel,
		"ja_resgatado": ja_resgatado,
	}
	return render(request, "core/beneficio_detalhe.html", context)


@login_required
def resgatar_beneficio(request, beneficio_id):
	if request.method != "POST":
		return HttpResponseForbidden("Metodo nao permitido.")

	doador = Doador.objects.filter(usuario=request.user).first()
	if not doador:
		messages.warning(request, "Apenas doadores cadastrados podem resgatar brindes.")
		return redirect("beneficio-detalhe", beneficio_id=beneficio_id)

	beneficio = get_object_or_404(Beneficio, pk=beneficio_id, ativo=True, empresa__ativa=True)

	if doador.total_doacoes_validadas < 1:
		messages.error(request, "Voce precisa de ao menos 1 doacao validada para resgatar este brinde.")
		return redirect("beneficio-detalhe", beneficio_id=beneficio_id)

	if ResgateBeneficio.objects.filter(doador=doador, beneficio=beneficio).exists():
		messages.warning(request, "Este brinde ja foi resgatado por voce.")
		return redirect("beneficio-detalhe", beneficio_id=beneficio_id)

	ultima_doacao_validada = doador.doacoes.filter(status=Doacao.STATUS_VALIDADA).first()
	ResgateBeneficio.objects.create(
		doador=doador,
		beneficio=beneficio,
		doacao_origem=ultima_doacao_validada,
	)
	messages.success(request, "Brinde resgatado com sucesso.")
	return redirect("beneficio-detalhe", beneficio_id=beneficio.pk)


class DoadorListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
	model = Doador
	template_name = "core/doador_list.html"
	context_object_name = "doadores"
	queryset = Doador.objects.select_related("usuario").order_by("usuario__first_name", "usuario__username")


class DoacaoListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
	model = Doacao
	template_name = "core/doacao_list.html"
	context_object_name = "doacoes"
	queryset = Doacao.objects.select_related("doador", "doador__usuario", "validada_por")


class DoacaoCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
	model = Doacao
	form_class = DoacaoForm
	template_name = "core/doacao_form.html"
	success_url = "/doacoes/"

	def form_valid(self, form):
		messages.success(self.request, "Doacao registrada com sucesso.")
		return super().form_valid(form)


@login_required
def meu_perfil(request):
	doador = Doador.objects.filter(usuario=request.user).first()
	if not doador:
		messages.warning(request, "Apenas doadores cadastrados possuem perfil de comprovacao.")
		return redirect("home")

	if request.method == "POST":
		comprovacao_form = ComprovacaoDoacaoForm(request.POST, request.FILES)
		if comprovacao_form.is_valid():
			doacao = comprovacao_form.save(commit=False)
			doacao.doador = doador
			doacao.status = Doacao.STATUS_PENDENTE
			doacao.save()
			messages.success(request, "Comprovacao enviada. Sua doacao sera validada pela equipe do Hemepar.")
			return redirect("meu-perfil")
	else:
		comprovacao_form = ComprovacaoDoacaoForm()

	doacoes = doador.doacoes.select_related("validada_por").all()
	resgates = doador.resgates.select_related("beneficio", "beneficio__empresa")[:5]
	context = {
		"doador": doador,
		"comprovacao_form": comprovacao_form,
		"doacoes": doacoes,
		"resgates": resgates,
	}
	return render(request, "core/meu_perfil.html", context)


@login_required
def meus_beneficios(request):
	doador = Doador.objects.filter(usuario=request.user).first()
	if not doador:
		messages.warning(request, "Seu perfil de doador ainda nao foi encontrado.")
		return redirect("home")
	return redirect("beneficios-disponiveis", doador_id=doador.pk)


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
	if not request.user.is_staff and doador.usuario != request.user:
		return HttpResponseForbidden("Voce nao pode visualizar os beneficios de outro doador.")

	total_validadas = doador.total_doacoes_validadas

	beneficios = Beneficio.objects.filter(ativo=True, empresa__ativa=True).select_related("empresa")
	beneficios_elegiveis = [
		beneficio for beneficio in beneficios if total_validadas >= 1
	]

	context = {
		"doador": doador,
		"total_validadas": total_validadas,
		"beneficios_elegiveis": beneficios_elegiveis,
		"beneficios_indisponiveis": [
			beneficio for beneficio in beneficios if total_validadas < 1
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

	if doador.total_doacoes_validadas < 1:
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
