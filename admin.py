from django.contrib import admin
from django.utils.html import format_html
from .models import Material, Movimento, ONT

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('sap', 'descricao', 'quantidade_atual', 'data_atualizacao')
    search_fields = ('sap', 'descricao')
    ordering = ('sap',)
    list_per_page = 20

@admin.register(Movimento)
class MovimentoAdmin(admin.ModelAdmin):
    list_display = ('material', 'tipo', 'quantidade', 'data', 'get_tecnico', 'rc', 'data_registro')
    list_filter = ('tipo', 'data', 'data_registro')
    search_fields = ('material__sap', 'material__descricao', 'rc', 'observacao')
    ordering = ('-data_registro',)
    list_per_page = 20
    
    def get_tecnico(self, obj):
        if obj.tipo == 'saida' and obj.observacao:
            # Tenta extrair o nome do técnico da observação
            linhas = obj.observacao.split('\n')
            for linha in linhas:
                if linha.startswith('Técnico:'):
                    tecnico = linha.replace('Técnico:', '').strip()
                    return format_html('<span style="color: #666;">{}</span>', tecnico)
        return '-'
    
    get_tecnico.short_description = 'Técnico'  # Nome da coluna no admin
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Se estiver editando um registro existente
            return ('material', 'tipo', 'quantidade', 'data', 'rc', 'data_registro')
        return ()

    fieldsets = (
        ('Informações do Material', {
            'fields': ('material', 'tipo', 'quantidade')
        }),
        ('Detalhes da Movimentação', {
            'fields': ('data', 'rc', 'observacao')
        }),
        ('Informações do Sistema', {
            'fields': ('data_registro',),
            'classes': ('collapse',)
        }),
    )

@admin.register(ONT)
class ONTAdmin(admin.ModelAdmin):
    list_display = ('sap', 'n_doc', 'carga', 'nome_equipamento', 'serial', 'data_cadastro')
    search_fields = ('sap', 'n_doc', 'serial', 'nome_equipamento')
    list_filter = ('nome_equipamento', 'carga')
    ordering = ('-data_cadastro',)
    list_per_page = 20 