from django.urls import path
from . import views

app_name = 'materiais'

urlpatterns = [
    path('upload/', views.upload_xlsx, name='upload'),
    path('buscar/', views.buscar_material, name='buscar'),
    path('cadastro-movimento/', views.cadastro_movimento, name='cadastro_movimento'),
    path('buscar-material-ajax/', views.buscar_material_ajax, name='buscar_material_ajax'),
    path('saida-material/', views.saida_material, name='saida_material'),
    path('cadastro-ont/', views.cadastro_ont, name='cadastro_ont'),
    path('buscar-ont/', views.buscar_ont, name='buscar_ont'),
] 