from rest_framework.permissions import BasePermission

ANALISTA = "Analista"
GESTOR = "Gestor"


def tem_perfil(user, *perfis):
    if not user or not user.is_authenticated:
        return False
    return user.is_superuser or user.groups.filter(name__in=perfis).exists()


class IsAnalistaOuGestor(BasePermission):
    message = "Acesso restrito à equipe interna."

    def has_permission(self, request, view):
        return tem_perfil(request.user, ANALISTA, GESTOR)


class IsGestor(BasePermission):
    message = "Apenas gestores podem realizar esta ação."

    def has_permission(self, request, view):
        return tem_perfil(request.user, GESTOR)