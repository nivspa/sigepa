from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db import transaction
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from .models import (
    Ocorrencia, EvolucaoTratamento, Cbo, Cid, Estabelecimentos,
    TipoNotificacao, Estado, Municipios, Sexo, TempoGestacao, Raca,
    PovoTradicional, Escolaridade, Pais, Zona, TipoEscalpelamento,
    TipoCausaAcidente, TipoTransporte, TipoComplicacao, TipoProcedimento,
    TipoRegimeAtendimento, TipoEvolucaoCaso, TipoParteAtingida
)
from .forms import (
    OcorrenciaForm, EvolucaoTratamentoForm, EvolucaoTratamentoComplicacaoFormSet,
    EvolucaoTratamentoProcedimentoFormSet, OcorrenciaParteAtingidaFormSet
)
from .cep import consultar_cep, limpar_cep


class OcorrenciaListView(LoginRequiredMixin, ListView):
    """Lista de ocorrências com paginação e busca"""
    model = Ocorrencia
    template_name = 'core/ocorrencia_list.html'
    context_object_name = 'ocorrencias'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Ocorrencia.objects.select_related(
            'tipo_notificacao', 'id_uf_notificacao', 'id_municipio_notificacao',
            'id_cnes', 'id_sexo', 'id_tempo_gestacao', 'id_raca'
        ).order_by('-data_notificacao')
        
        # Busca
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nome_paciente__icontains=search) |
                Q(num_registro__icontains=search) |
                Q(cartao_sus__icontains=search) |
                Q(cpf__icontains=search)
            )
        
        # Filtros
        tipo_notificacao = self.request.GET.get('tipo_notificacao')
        if tipo_notificacao:
            queryset = queryset.filter(tipo_notificacao_id=tipo_notificacao)
            
        uf = self.request.GET.get('uf')
        if uf:
            queryset = queryset.filter(id_uf_notificacao_id=uf)
            
        municipio = self.request.GET.get('municipio')
        if municipio:
            queryset = queryset.filter(id_municipio_notificacao_id=municipio)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipos_notificacao'] = TipoNotificacao.objects.all()
        context['estados'] = Estado.objects.all()
        context['municipios'] = Municipios.objects.all()
        return context


class OcorrenciaDetailView(LoginRequiredMixin, DetailView):
    """Detalhes de uma ocorrência"""
    model = Ocorrencia
    template_name = 'core/ocorrencia_detail.html'
    context_object_name = 'ocorrencia'
    
    def get_queryset(self):
        return Ocorrencia.objects.select_related(
            'tipo_notificacao', 'id_uf_notificacao', 'id_municipio_notificacao',
            'id_cnes', 'id_sexo', 'id_tempo_gestacao', 'id_raca', 'id_povo_tradicional',
            'id_cbo', 'id_escolaridade', 'id_pais', 'id_uf_residencia',
            'id_municipio_residencia', 'id_zona', 'id_cid', 'id_tipo_escalpelamento',
            'id_causa_acidente', 'id_municipio_ocorrencia', 'id_uf_transferencia',
            'id_municipio_transferencia', 'id_tipo_transporte', 'id_municipio_investigador',
            'id_cnes_invertigador'
        ).prefetch_related('evolucaotratamento_set')


class OcorrenciaCreateView(LoginRequiredMixin, CreateView):
    """Criar nova ocorrência"""
    model = Ocorrencia
    form_class = OcorrenciaForm
    template_name = 'core/ocorrencia_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nova Ocorrência'
        context['button_text'] = 'Salvar'
        
        # Formset para partes atingidas
        if self.object:
            context['parte_atingida_formset'] = OcorrenciaParteAtingidaFormSet(
                instance=self.object
            )
        else:
            context['parte_atingida_formset'] = OcorrenciaParteAtingidaFormSet()
        
        return context
    
    def form_valid(self, form):
        with transaction.atomic():
            # Salvar o objeto primeiro
            response = super().form_valid(form)
            
            print(f"\n🔍 POST data recebido (CREATE): {self.request.POST}")
            
            # Salvar formset de partes atingidas
            parte_atingida_formset = OcorrenciaParteAtingidaFormSet(
                self.request.POST, instance=self.object
            )
            
            print(f"📊 Formset criado. Total de forms: {len(parte_atingida_formset.forms)}")
            
            if parte_atingida_formset.is_valid():
                print("✅ Formset válido! Iniciando save...")
                # O método save do formset agora gerencia corretamente as instâncias
                parte_atingida_formset.save()
                messages.success(self.request, 'Ocorrência criada com sucesso!')
            else:
                # Se o formset não for válido, mostrar erros detalhados
                errors = parte_atingida_formset.errors
                non_form_errors = parte_atingida_formset.non_form_errors()
                error_msg = 'Erro ao salvar partes atingidas.'
                if non_form_errors:
                    error_msg += f' {non_form_errors}'
                messages.error(self.request, error_msg)
                print(f"❌ Erros do formset: {errors}")
                print(f"❌ Erros não-form: {non_form_errors}")
                # Imprimir erros de cada formulário
                for form_index, form_errors in enumerate(errors):
                    if form_errors:
                        print(f"❌ Form {form_index}: {form_errors}")
                
        return response

class OcorrenciaUpdateView(LoginRequiredMixin, UpdateView):
    """Editar ocorrência existente"""
    model = Ocorrencia
    form_class = OcorrenciaForm
    template_name = 'core/ocorrencia_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Ocorrência'
        context['button_text'] = 'Atualizar'
        
        # Formsets para relações Many-to-Many
        if self.object:
            context['parte_atingida_formset'] = OcorrenciaParteAtingidaFormSet(
                instance=self.object
            )
        else:
            context['parte_atingida_formset'] = OcorrenciaParteAtingidaFormSet()
        
        return context
    
    def form_valid(self, form):
        with transaction.atomic():
            # Salvar o objeto primeiro
            response = super().form_valid(form)
            
            print(f"\n🔍 POST data recebido:")
            # Mostrar apenas dados relevantes do formset
            for key in self.request.POST:
                if 'ocorrenciahastipoparteatingida' in key:
                    print(f"  {key}: {self.request.POST.get(key)}")
            
            # Salvar formset de partes atingidas
            parte_atingida_formset = OcorrenciaParteAtingidaFormSet(
                self.request.POST, instance=self.object
            )
            
            print(f"📊 Formset criado. Total de forms: {len(parte_atingida_formset.forms)}")
            print(f"📊 TOTAL_FORMS: {parte_atingida_formset.total_form_count()}")
            print(f"📊 INITIAL_FORMS: {parte_atingida_formset.initial_form_count()}")
            
            if parte_atingida_formset.is_valid():
                print("✅ Formset válido! Iniciando save...")
                # O método save do formset agora gerencia corretamente as instâncias
                parte_atingida_formset.save()
                messages.success(self.request, 'Ocorrência atualizada com sucesso!')
            else:
                # Se o formset não for válido, mostrar erros detalhados
                errors = parte_atingida_formset.errors
                non_form_errors = parte_atingida_formset.non_form_errors()
                error_msg = 'Erro ao salvar partes atingidas.'
                if non_form_errors:
                    error_msg += f' {non_form_errors}'
                messages.error(self.request, error_msg)
                print(f"❌ Erros do formset: {errors}")
                print(f"❌ Erros não-form: {non_form_errors}")
                # Imprimir erros de cada formulário
                for form_index, form_errors in enumerate(errors):
                    if form_errors:
                        print(f"❌ Form {form_index}: {form_errors}")
                
        return response


class OcorrenciaDeleteView(LoginRequiredMixin, DeleteView):
    """Excluir ocorrência"""
    model = Ocorrencia
    template_name = 'core/ocorrencia_confirm_delete.html'
    success_url = reverse_lazy('core:ocorrencia_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Ocorrência excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


# Views para Evolução do Tratamento
class EvolucaoTratamentoCreateView(LoginRequiredMixin, CreateView):
    """Criar evolução do tratamento"""
    model = EvolucaoTratamento
    form_class = EvolucaoTratamentoForm
    template_name = 'core/evolucao_tratamento_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nova Evolução do Tratamento'
        context['button_text'] = 'Salvar'
        
        # Formsets para relações Many-to-Many
        context['complicacao_formset'] = EvolucaoTratamentoComplicacaoFormSet()
        context['procedimento_formset'] = EvolucaoTratamentoProcedimentoFormSet()
        
        return context
    
    def form_valid(self, form):
        with transaction.atomic():
            response = super().form_valid(form)
            
            # Salvar formsets
            complicacao_formset = EvolucaoTratamentoComplicacaoFormSet(
                self.request.POST, instance=self.object
            )
            procedimento_formset = EvolucaoTratamentoProcedimentoFormSet(
                self.request.POST, instance=self.object
            )
            
            if complicacao_formset.is_valid() and procedimento_formset.is_valid():
                complicacao_formset.save()
                procedimento_formset.save()
                messages.success(self.request, 'Evolução do tratamento criada com sucesso!')
            else:
                messages.error(self.request, 'Erro ao salvar evolução do tratamento.')
                
        return response


# Views para APIs de autocomplete
@csrf_exempt
def autocomplete_cbo(request):
    """API para autocomplete de CBO com paginação"""
    query = request.GET.get('q', '')
    page = int(request.GET.get('page', 1))
    per_page = 10
    
    # Filtrar CBOs
    cbos_query = Cbo.objects.all().order_by('codigo')
    if query:
        cbos_query = cbos_query.filter(
            Q(codigo__icontains=query) | Q(titulo__icontains=query)
        )
    
    # Aplicar paginação
    paginator = Paginator(cbos_query, per_page)
    try:
        cbos_page = paginator.page(page)
    except:
        cbos_page = paginator.page(1)
    
    results = []
    for cbo in cbos_page.object_list:
        results.append({
            'id': cbo.codigo,
            'text': f"{cbo.codigo} - {cbo.titulo}"
        })
    
    return JsonResponse({
        'results': results,
        'pagination': {
            'current_page': cbos_page.number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'has_next': cbos_page.has_next(),
            'has_previous': cbos_page.has_previous()
        }
    })


@csrf_exempt
def autocomplete_cid(request):
    """API para autocomplete de CID com paginação"""
    query = request.GET.get('q', '')
    page = int(request.GET.get('page', 1))
    per_page = 10
    
    # Filtrar CIDs
    cids_query = Cid.objects.all().order_by('cod_categoria', 'cod_subcategoria')
    if query:
        cids_query = cids_query.filter(
            Q(cod_categoria__icontains=query) | 
            Q(cod_subcategoria__icontains=query) |
            Q(desc_categoria__icontains=query) |
            Q(desc_subcategoria__icontains=query)
        )
    
    # Aplicar paginação
    paginator = Paginator(cids_query, per_page)
    try:
        cids_page = paginator.page(page)
    except:
        cids_page = paginator.page(1)
    
    results = []
    for cid in cids_page.object_list:
        codigo = f"{cid.cod_categoria}.{cid.cod_subcategoria}" if cid.cod_subcategoria else cid.cod_categoria
        descricao = cid.desc_subcategoria or cid.desc_categoria
        results.append({
            'id': cid.sk_causa,
            'text': f"{codigo} - {descricao}"
        })
    
    return JsonResponse({
        'results': results,
        'pagination': {
            'current_page': cids_page.number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'has_next': cids_page.has_next(),
            'has_previous': cids_page.has_previous()
        }
    })


@csrf_exempt
def autocomplete_estabelecimentos(request):
    """API para autocomplete de Estabelecimentos com paginação"""
    query = request.GET.get('q', '')
    page = int(request.GET.get('page', 1))
    per_page = 10
    
    # Filtrar estabelecimentos
    estabelecimentos_query = Estabelecimentos.objects.all().order_by('co_cnes')
    if query:
        estabelecimentos_query = estabelecimentos_query.filter(
            Q(co_cnes__icontains=query) | 
            Q(no_fantasia__icontains=query) |
            Q(nu_cnpj__icontains=query)
        )
    
    # Aplicar paginação
    paginator = Paginator(estabelecimentos_query, per_page)
    try:
        estabelecimentos_page = paginator.page(page)
    except:
        estabelecimentos_page = paginator.page(1)
    
    results = []
    for est in estabelecimentos_page.object_list:
        results.append({
            'id': est.co_unidade,
            'text': f"{est.co_cnes} - {est.no_fantasia or 'Sem nome'}"
        })
    
    return JsonResponse({
        'results': results,
        'pagination': {
            'current_page': estabelecimentos_page.number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'has_next': estabelecimentos_page.has_next(),
            'has_previous': estabelecimentos_page.has_previous()
        }
    })


@csrf_exempt
def consulta_cep(request):
    """Consulta endereço pelo CEP (ViaCEP)."""
    cep = limpar_cep(request.GET.get('cep', ''))
    if len(cep) != 8:
        return JsonResponse({
            'success': False,
            'error': 'Informe um CEP com 8 dígitos.',
        }, status=400)

    endereco = consultar_cep(cep)
    if not endereco:
        return JsonResponse({
            'success': False,
            'error': 'CEP não encontrado.',
        }, status=404)

    return JsonResponse({
        'success': True,
        'endereco': endereco,
    })


# View para carregar municípios por estado
@csrf_exempt
def load_municipios(request):
    """Carregar municípios por estado ou todos os municípios"""
    try:
        estado_id = request.GET.get('estado_id')
        print(f"🔍 Carregando municípios para estado_id: {estado_id}")
        
        if estado_id:
            # Verificar se o estado existe
            try:
                estado = Estado.objects.get(idestado=estado_id)
                print(f"📍 Estado encontrado: {estado.descricao}")
            except Estado.DoesNotExist:
                print(f"❌ Estado não encontrado: {estado_id}")
                return JsonResponse({
                    'municipios': [],
                    'error': f'Estado {estado_id} não encontrado',
                    'success': False
                })
            
            # Buscar municípios do estado específico
            municipios = Municipios.objects.filter(
                id_uf_id=estado_id,
                nome_municipio__isnull=False
            ).exclude(
                nome_municipio__exact=''
            ).order_by('nome_municipio')
            
            count = municipios.count()
            print(f"📊 Encontrados {count} municípios para estado {estado_id}")
        else:
            # Carregar todos os municípios
            municipios = Municipios.objects.filter(
                nome_municipio__isnull=False
            ).exclude(
                nome_municipio__exact=''
            ).order_by('nome_municipio')
            
            count = municipios.count()
            print(f"📊 Carregando todos os {count} municípios")
        
        # Processar dados dos municípios
        data = []
        for m in municipios:
            if m.nome_municipio and m.nome_municipio.strip():  # Verificar se o nome não é vazio
                municipio_data = {
                    'id': m.id_municipio, 
                    'nome': m.nome_municipio.strip()
                }
                # Adicionar nome do estado se disponível
                if hasattr(m, 'id_uf') and m.id_uf:
                    municipio_data['uf'] = m.nome_uf or (m.id_uf.descricao if hasattr(m.id_uf, 'descricao') else '')
                
                data.append(municipio_data)
        
        result = {
            'municipios': data,
            'success': True,
            'total': len(data),
            'estado_id': estado_id
        }
        
        print(f"✅ Retornando {len(data)} municípios válidos")
        return JsonResponse(result)
            
    except Exception as e:
        print(f"❌ Erro ao carregar municípios: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'error': str(e), 
            'municipios': [],
            'success': False,
            'total': 0
        }, status=500)