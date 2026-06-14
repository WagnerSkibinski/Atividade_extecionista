from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class TimestampedModel(models.Model):
	criado_em = models.DateTimeField(auto_now_add=True)
	atualizado_em = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True


class PerfilUsuario(TimestampedModel):
	TIPO_DOADOR = "doador"
	TIPO_EMPRESA = "empresa"

# Diferenciar tipo de usuario e telas mostradas 
	TIPOS = [
		(TIPO_DOADOR, "Doador"),
		(TIPO_EMPRESA, "Empresa"),
	]

	usuario = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="perfil_usuario",
	)
	tipo = models.CharField(max_length=10, choices=TIPOS)

	class Meta:
		verbose_name = "Perfil de Usuario"
		verbose_name_plural = "Perfis de Usuario"

	def __str__(self):
		return f"{self.usuario.username} ({self.tipo})"

# Editar no admin o banner da pagina principal
class BannerPropaganda(TimestampedModel):
	titulo = models.CharField(max_length=120)
	imagem = models.ImageField(upload_to="banners/")
#  link (possivel uso futuro)
	link = models.URLField(blank=True)
	ativo = models.BooleanField(default=True)
	ordem = models.PositiveIntegerField(default=0)

	class Meta:
		verbose_name = "Banner de Propaganda"
		verbose_name_plural = "Banners de Propaganda"
		ordering = ["ordem", "-criado_em"]

	def __str__(self):
		return self.titulo

# usuario tipo doador
class Doador(TimestampedModel):
	
 	# tipos de sangue para doadores (mudar para editar no admin futuramente)
	TIPOS_SANGUINEOS = [
		("A+", "A+"),
		("A-", "A-"),
		("B+", "B+"),
		("B-", "B-"),
		("AB+", "AB+"),
		("AB-", "AB-"),
		("O+", "O+"),
		("O-", "O-"),
	]

	usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	cpf = models.CharField(max_length=14, unique=True)
	telefone = models.CharField(max_length=20)
	data_nascimento = models.DateField()
	tipo_sanguineo = models.CharField(max_length=3, choices=TIPOS_SANGUINEOS)
	ativo = models.BooleanField(default=True)

	class Meta:
		verbose_name = "Doador"
		verbose_name_plural = "Doadores"

	def __str__(self):
		return f"{self.usuario.get_full_name() or self.usuario.username} - {self.cpf}"

	@property
	def total_doacoes_validadas(self):
		return self.doacoes.filter(status=Doacao.STATUS_VALIDADA).count()


# usuario tipo empresa (cadastro diferente de doador)
class EmpresaParceira(TimestampedModel):
	usuario = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="empresa_perfil",
	)
	nome = models.CharField(max_length=120)
	cnpj = models.CharField(max_length=18, unique=True)
	contato = models.CharField(max_length=120)
	descricao = models.TextField(blank=True)
	foto = models.ImageField(upload_to="empresas/", blank=True, null=True)
	ativa = models.BooleanField(default=True)

	class Meta:
		verbose_name = "Empresa Parceira"
		verbose_name_plural = "Empresas Parceiras"   

	def __str__(self):
		return self.nome


class Beneficio(TimestampedModel):
	empresa = models.ForeignKey(EmpresaParceira, on_delete=models.CASCADE, related_name="beneficios")
	titulo = models.CharField(max_length=120)
	descricao = models.TextField()
	codigo_cupom = models.CharField(max_length=60, blank=True)
	foto = models.ImageField(upload_to="beneficios/", blank=True, null=True)
	minimo_doacoes_validadas = models.PositiveIntegerField(
		default=1,
		validators=[MinValueValidator(1)],
		help_text="Mantido para compatibilidade; a regra ativa considera 1 doacao validada.",
	)
	ativo = models.BooleanField(default=True)

	class Meta:
		verbose_name = "Beneficio"
		verbose_name_plural = "Beneficios"

	def __str__(self):
		return f"{self.titulo} ({self.empresa.nome})"

# validação de doador para o usuario 
class Doacao(TimestampedModel):
	STATUS_PENDENTE = "pendente"
 
	STATUS_VALIDADA = "validada"
	STATUS_REJEITADA = "rejeitada"

	STATUS_CHOICES = [
		(STATUS_PENDENTE, "Pendente"),
		(STATUS_VALIDADA, "Validada"),
		(STATUS_REJEITADA, "Rejeitada"),
	]

	doador = models.ForeignKey(Doador, on_delete=models.CASCADE, related_name="doacoes")
	data_doacao = models.DateField(default=timezone.localdate)
	local = models.CharField(max_length=120, default="Hemepar Curitiba")
	volume_ml = models.PositiveIntegerField(default=450)
	status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDENTE)
	observacao = models.TextField(blank=True)
	comprovante = models.FileField(upload_to="comprovantes/", blank=True, null=True)
	validada_por = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="doacoes_validadas",
	)
	data_validacao = models.DateTimeField(null=True, blank=True)

	class Meta:
		verbose_name = "Doacao"
		verbose_name_plural = "Doacoes"
		ordering = ["-data_doacao", "-criado_em"]

	def __str__(self):
		return f"Doacao #{self.pk} - {self.doador}"

	def validar(self, profissional):
		self.status = self.STATUS_VALIDADA
		self.validada_por = profissional
		self.data_validacao = timezone.now()
		self.save(update_fields=["status", "validada_por", "data_validacao", "atualizado_em"])

# Resgate de beneficios
class ResgateBeneficio(TimestampedModel):
	doador = models.ForeignKey(Doador, on_delete=models.CASCADE, related_name="resgates")
	beneficio = models.ForeignKey(Beneficio, on_delete=models.CASCADE, related_name="resgates")
	doacao_origem = models.ForeignKey(Doacao, on_delete=models.SET_NULL, null=True, blank=True)
	concedido_por = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="resgates_concedidos",
	)
	data_concessao = models.DateTimeField(default=timezone.now)

	class Meta:
		verbose_name = "Resgate de Beneficio"
		verbose_name_plural = "Resgates de Beneficios"
		ordering = ["-data_concessao"]

	def __str__(self):
		return f"{self.doador} - {self.beneficio}"
