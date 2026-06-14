from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Beneficio, Doador, Doacao, EmpresaParceira, PerfilUsuario

#Forms para utilidades nas paginas de registro (diferenciar por nomenclatura) 



class DoacaoForm(forms.ModelForm):
    class Meta:
        model = Doacao
        fields = ["doador", "data_doacao", "local", "volume_ml", "observacao"]
        widgets = {
            "data_doacao": forms.DateInput(attrs={"type": "date"}),
            "observacao": forms.Textarea(attrs={"rows": 3}),
        }


class CadastroDoadorForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, label="Nome")
    last_name = forms.CharField(max_length=150, label="Sobrenome")
    email = forms.EmailField(label="E-mail")
    cpf = forms.CharField(max_length=14, label="CPF")
    telefone = forms.CharField(max_length=20, label="Telefone")
    data_nascimento = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), label="Data de nascimento")
    tipo_sanguineo = forms.ChoiceField(choices=Doador.TIPOS_SANGUINEOS, label="Tipo sanguineo")

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "cpf",
            "telefone",
            "data_nascimento",
            "tipo_sanguineo",
            "password1",
            "password2",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()
            Doador.objects.create(
                usuario=user,
                cpf=self.cleaned_data["cpf"],
                telefone=self.cleaned_data["telefone"],
                data_nascimento=self.cleaned_data["data_nascimento"],
                tipo_sanguineo=self.cleaned_data["tipo_sanguineo"],
            )
            PerfilUsuario.objects.update_or_create(
                usuario=user,
                defaults={"tipo": PerfilUsuario.TIPO_DOADOR},
            )
        return user


class CadastroEmpresaForm(forms.Form):
    username = forms.CharField(max_length=150, label="Usuario da empresa")
    email = forms.EmailField(label="E-mail")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Senha")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar senha")
    nome_empresa = forms.CharField(max_length=120, label="Nome da empresa")
    cnpj = forms.CharField(max_length=18, label="CNPJ")
    contato = forms.CharField(max_length=120, label="Contato")

    def clean_username(self):
        username = self.cleaned_data["username"]
        if get_user_model().objects.filter(username=username).exists():
            raise forms.ValidationError("Este usuario ja esta em uso.")
        return username

    def clean_cnpj(self):
        cnpj = self.cleaned_data["cnpj"]
        empresa = EmpresaParceira.objects.filter(cnpj=cnpj).first()
        if empresa and empresa.usuario:
            raise forms.ValidationError("Este CNPJ ja possui uma conta vinculada.")
        return cnpj

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("As senhas nao conferem.")
        return cleaned_data

    def save(self):
        user = get_user_model().objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password1"],
        )

        empresa, criada = EmpresaParceira.objects.get_or_create(
            cnpj=self.cleaned_data["cnpj"],
            defaults={
                "usuario": user,
                "nome": self.cleaned_data["nome_empresa"],
                "contato": self.cleaned_data["contato"],
                "ativa": True,
            },
        )

        if not criada:
            empresa.usuario = user
            empresa.nome = self.cleaned_data["nome_empresa"]
            empresa.contato = self.cleaned_data["contato"]
            empresa.ativa = True
            empresa.save(update_fields=["usuario", "nome", "contato", "ativa", "atualizado_em"])

        PerfilUsuario.objects.update_or_create(
            usuario=user,
            defaults={"tipo": PerfilUsuario.TIPO_EMPRESA},
        )

        return empresa


class GerenciarEmpresaForm(forms.ModelForm):
    class Meta:
        model = EmpresaParceira
        fields = ["nome", "contato", "descricao", "foto"]
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 4}),
        }


class CadastroBrindeForm(forms.Form):
    titulo_brinde = forms.CharField(max_length=120, label="Titulo do brinde")
    descricao_brinde = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), label="Descricao do brinde")
    codigo_cupom = forms.CharField(max_length=60, required=False, label="Codigo do cupom")
    foto = forms.ImageField(required=False, label="Foto do brinde")

    def save(self, empresa):
        beneficio = Beneficio.objects.create(
            empresa=empresa,
            titulo=self.cleaned_data["titulo_brinde"],
            descricao=self.cleaned_data["descricao_brinde"],
            codigo_cupom=self.cleaned_data["codigo_cupom"],
            minimo_doacoes_validadas=1,
            ativo=True,
        )

        foto = self.cleaned_data.get("foto")
        if foto:
            beneficio.foto = foto
            beneficio.save(update_fields=["foto", "atualizado_em"])

        return beneficio


class ComprovacaoDoacaoForm(forms.ModelForm):
    class Meta:
        model = Doacao
        fields = ["data_doacao", "local", "volume_ml", "observacao", "comprovante"]
        widgets = {
            "data_doacao": forms.DateInput(attrs={"type": "date"}),
            "observacao": forms.Textarea(attrs={"rows": 3}),
        }
