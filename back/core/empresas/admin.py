from django.contrib import admin
from .models import AreaAtuacao, Empresa


@admin.register(AreaAtuacao)
class AreaAtuacaoAdmin(admin.ModelAdmin):
    list_display = ("id", "nome")
    search_fields = ("nome",)
    ordering = ("nome",)


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("razao_social", "cnpj", "cidade", "status")
    search_fields = ("razao_social", "cnpj")
    list_filter = ("status", "cidade")
    filter_horizontal = ("areas",)