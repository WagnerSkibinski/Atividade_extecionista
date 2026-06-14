from .models import Doador, EmpresaParceira


def tipo_usuario_context(request):
    is_doador = False
    is_empresa = False

    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        perfil = getattr(user, "perfil_usuario", None)
        if perfil:
            is_doador = perfil.tipo == "doador"
            is_empresa = perfil.tipo == "empresa"
        else:
            # Fallback para contas antigas sem PerfilUsuario cadastrado.
            is_doador = Doador.objects.filter(usuario=user).exists()
            is_empresa = EmpresaParceira.objects.filter(usuario=user).exists()

    return {
        "is_doador": is_doador,
        "is_empresa": is_empresa,
    }
