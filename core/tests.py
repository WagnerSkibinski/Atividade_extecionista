from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Beneficio, Doacao, Doador, EmpresaParceira


class ElegibilidadeBeneficioTestCase(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(
			username="doador_teste",
			password="senha-forte-123",
			first_name="Doador",
			last_name="Teste",
		)
		self.doador = Doador.objects.create(
			usuario=self.user,
			cpf="123.456.789-00",
			telefone="(41) 99999-0000",
			data_nascimento="1995-01-01",
			tipo_sanguineo="O+",
		)
		empresa = EmpresaParceira.objects.create(
			nome="Farmacia Solidaria",
			cnpj="12.345.678/0001-00",
			contato="contato@farmacia.com",
			ativa=True,
		)
		self.beneficio = Beneficio.objects.create(
			empresa=empresa,
			titulo="Desconto em medicamentos",
			descricao="10% de desconto para doadores elegiveis",
			minimo_doacoes_validadas=1,
			ativo=True,
		)

	def test_doador_fica_elegivel_apos_uma_doacao_validada(self):
		Doacao.objects.create(doador=self.doador, status=Doacao.STATUS_VALIDADA)

		self.assertGreaterEqual(
			self.doador.total_doacoes_validadas,
			self.beneficio.minimo_doacoes_validadas,
		)
