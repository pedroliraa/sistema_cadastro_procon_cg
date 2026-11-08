from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema

from .permissions import IsAnalistaOuGestor, IsGestor
from .serializers import UsuarioSerializer


class UsuarioViewSet(ModelViewSet):
    """CRUD de usuários internos: só o gestor acessa."""
    queryset = User.objects.all().order_by("username")
    serializer_class = UsuarioSerializer
    permission_classes = [IsGestor]


class MeView(APIView):
    """O Angular usa isso pra saber o perfil e esconder/mostrar telas."""
    permission_classes = [IsAnalistaOuGestor]

    @extend_schema(responses=UsuarioSerializer)
    def get(self, request):
        return Response(UsuarioSerializer(request.user).data)