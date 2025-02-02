from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from .models import Material, Movimento, ONT
from datetime import date
from django.db import models

@csrf_exempt
def upload_xlsx(request):
    if request.method == 'POST' and request.FILES.get('arquivo_xlsx'):
        arquivo = request.FILES['arquivo_xlsx']
        try:
            df = pd.read_excel(arquivo)
            print("Colunas encontradas no arquivo:", df.columns.tolist())
            
            # Mapeamento de possíveis nomes de colunas
            colunas = {
                'sap': ['sap', 'SAP', 'código', 'codigo', 'code', 'Código', 'CÓDIGO', 'COD', 'Cod'],
                'descricao': ['descricao', 'descrição', 'DESCRIÇÃO', 'desc', 'nome', 'material', 
                             'MATERIAL', 'Descrição', 'DESCRICAO', 'Material', 'NOME', 'Nome'],
            }
            
            # Identificar as colunas no arquivo
            colunas_encontradas = {}
            for campo, possiveis_nomes in colunas.items():
                for nome in possiveis_nomes:
                    if nome in df.columns:
                        colunas_encontradas[campo] = nome
                        break
                if campo not in colunas_encontradas:
                    raise ValueError(f'Coluna {campo} não encontrada no arquivo. Colunas disponíveis: {", ".join(df.columns)}')
            
            # Processar os dados
            for _, row in df.iterrows():
                Material.objects.update_or_create(
                    sap=str(row[colunas_encontradas['sap']]).strip(),
                    defaults={
                        'descricao': str(row[colunas_encontradas['descricao']]).strip(),
                    }
                )
            messages.success(request, 'Arquivo processado com sucesso!')
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Erro ao processar arquivo: {str(e)}')
    return render(request, 'materiais/upload.html')

def buscar_material(request):
    sap = request.GET.get('sap', '')
    material = None
    if sap:
        material = Material.objects.filter(sap=sap).first()
    return render(request, 'materiais/busca.html', {'material': material, 'sap': sap})

def cadastro_movimento(request):
    if request.method == 'POST':
        sap = request.POST.get('sap')
        tipo = request.POST.get('tipo')
        quantidade = int(request.POST.get('quantidade'))
        data = request.POST.get('data')
        rc = request.POST.get('rc')
        observacao = request.POST.get('observacao')

        try:
            material = Material.objects.get(sap=sap)
            
            movimento = Movimento(
                material=material,
                tipo=tipo,
                quantidade=quantidade,
                data=data,
                rc=rc if tipo == 'entrada' else None,
                observacao=observacao
            )
            
            movimento.save()
            messages.success(request, 'Movimento registrado com sucesso!')
            return redirect('materiais:cadastro_movimento')
            
        except Material.DoesNotExist:
            messages.error(request, 'Material não encontrado!')
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Erro ao registrar movimento: {str(e)}')
    
    return render(request, 'materiais/cadastro_movimento.html')

def buscar_material_ajax(request):
    sap = request.GET.get('sap', '')
    try:
        material = Material.objects.get(sap=sap)
        return JsonResponse({
            'success': True,
            'descricao': material.descricao,
            'quantidade_atual': material.quantidade_atual
        })
    except Material.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Material não encontrado'
        })

def saida_material(request):
    if request.method == 'POST':
        sap = request.POST.get('sap')
        quantidade = int(request.POST.get('quantidade'))
        data = request.POST.get('data')
        tecnico = request.POST.get('tecnico')
        observacao = request.POST.get('observacao')

        try:
            material = Material.objects.get(sap=sap)
            
            movimento = Movimento(
                material=material,
                tipo='saida',
                quantidade=quantidade,
                data=data,
                observacao=f"Técnico: {tecnico}\n{observacao}" if observacao else f"Técnico: {tecnico}"
            )
            
            movimento.save()
            messages.success(request, 'Saída registrada com sucesso!')
            return redirect('materiais:saida_material')
            
        except Material.DoesNotExist:
            messages.error(request, 'Material não encontrado!')
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Erro ao registrar saída: {str(e)}')
    
    return render(request, 'materiais/saida_material.html')

def cadastro_ont(request):
    if request.method == 'POST':
        sap = request.POST.get('sap')
        n_doc = request.POST.get('n_doc')
        carga = request.POST.get('carga')
        nome_equipamento = request.POST.get('nome_equipamento')
        seriais_text = request.POST.get('seriais', '').strip()

        # Processa os seriais (aceita vírgulas ou quebras de linha como separadores)
        seriais = [s.strip() for s in seriais_text.replace('\n', ',').split(',') if s.strip()]
        
        try:
            # Remove seriais duplicados mantendo a ordem
            seriais = list(dict.fromkeys(seriais))
            
            # Verifica se já existem seriais cadastrados
            seriais_existentes = ONT.objects.filter(serial__in=seriais).values_list('serial', flat=True)
            if seriais_existentes:
                raise ValueError(f'Os seguintes seriais já estão cadastrados: {", ".join(seriais_existentes)}')

            # Contador de ONTs cadastradas
            total_cadastradas = 0
            
            # Cadastra uma ONT para cada serial
            for serial in seriais:
                if serial:  # Ignora strings vazias
                    ONT.objects.create(
                        sap=sap,
                        n_doc=n_doc,
                        carga=carga,
                        nome_equipamento=nome_equipamento,
                        serial=serial.upper()  # Converte para maiúsculas
                    )
                    total_cadastradas += 1
            
            messages.success(request, f'{total_cadastradas} ONT(s) cadastrada(s) com sucesso!')
            return redirect('materiais:cadastro_ont')
            
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Erro ao cadastrar ONTs: {str(e)}')

    return render(request, 'materiais/cadastro_ont.html')

def buscar_ont(request):
    query = request.GET.get('query', '')
    onts = []
    
    if query:
        onts = ONT.objects.filter(
            models.Q(sap__icontains=query) |
            models.Q(serial__icontains=query) |
            models.Q(n_doc__icontains=query)
        )[:20]  # Limita a 20 resultados
        
    return render(request, 'materiais/busca_ont.html', {
        'onts': onts,
        'query': query
    }) 