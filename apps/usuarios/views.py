from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json
from .forms import UsuarioCreationForm
from core.models import Ocorrencia, TipoEscalpelamento, Estado, Municipios, Estabelecimentos


def home(request):
    """
    View para a página inicial com dashboard de estatísticas.
    """
    context = {}
    
    if request.user.is_authenticated:
        # Estatísticas básicas
        total_ocorrencias = Ocorrencia.objects.count()
        
        # Ocorrências do mês atual
        hoje = timezone.localdate()
        inicio_mes = hoje.replace(day=1)
        ocorrencias_mes = Ocorrencia.objects.filter(
            data_notificacao__gte=inicio_mes
        ).count()
        
        # Municípios únicos atendidos
        municipios_atendidos = Ocorrencia.objects.values('id_municipio_notificacao').distinct().count()
        
        # Estabelecimentos únicos
        estabelecimentos_ativos = Ocorrencia.objects.values('id_cnes').distinct().count()
        
        # Dados para gráfico de ocorrências por mês (últimos 12 meses)
        meses = []
        dados_mensais = []
        
        for i in range(11, -1, -1):
            data_ref = hoje - timedelta(days=30*i)
            mes_inicio = data_ref.replace(day=1)
            if i == 0:
                mes_fim = hoje
            else:
                proximo_mes = mes_inicio + timedelta(days=32)
                mes_fim = proximo_mes.replace(day=1) - timedelta(days=1)
            
            count = Ocorrencia.objects.filter(
                data_notificacao__gte=mes_inicio,
                data_notificacao__lte=mes_fim
            ).count()
            
            meses.append(mes_inicio.strftime('%m/%Y'))
            dados_mensais.append(count)
        
        # Dados para gráfico de distribuição por UF
        ufs_data = []
        ufs_labels = []
        
        ufs_ocorrencias = Ocorrencia.objects.values('id_uf_notificacao__descricao').annotate(
            total=Count('id')
        ).order_by('-total')[:8]
        
        for uf in ufs_ocorrencias:
            ufs_labels.append(uf['id_uf_notificacao__descricao'])
            ufs_data.append(uf['total'])
        
        # Ocorrências recentes (últimas 10)
        ocorrencias_recentes = Ocorrencia.objects.select_related(
            'id_uf_notificacao', 'id_municipio_notificacao'
        ).order_by('-data_notificacao')[:10]
        
        # Tipos de escalpelamento com estatísticas
        tipos_escalpelamento = []
        tipos_data = TipoEscalpelamento.objects.annotate(
            total=Count('ocorrencia')
        ).filter(total__gt=0).order_by('-total')
        
        total_tipos = sum(tipo.total for tipo in tipos_data)
        
        for tipo in tipos_data:
            percentual = (tipo.total / total_tipos * 100) if total_tipos > 0 else 0
            tipos_escalpelamento.append({
                'descricao': tipo.descricao,
                'total': tipo.total,
                'percentual': round(percentual, 1)
            })
        
        context.update({
            'total_ocorrencias': total_ocorrencias,
            'ocorrencias_mes': ocorrencias_mes,
            'municipios_atendidos': municipios_atendidos,
            'estabelecimentos_ativos': estabelecimentos_ativos,
            'meses': json.dumps(meses),
            'dados_mensais': json.dumps(dados_mensais),
            'ufs_labels': json.dumps(ufs_labels),
            'ufs_data': json.dumps(ufs_data),
            'ocorrencias_recentes': ocorrencias_recentes,
            'tipos_escalpelamento': tipos_escalpelamento,
        })
    
    return render(request, 'usuarios/home.html', context)


def register(request):
    """
    View para registro de novos usuários.
    """
    if request.method == 'POST':
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada para {username}!')
            login(request, user)
            return redirect('usuarios:home')
    else:
        form = UsuarioCreationForm()
    return render(request, 'usuarios/register.html', {'form': form})


class CustomLoginView(LoginView):
    """
    View personalizada para login com redirecionamento.
    """
    template_name = 'usuarios/login.html'
    form_class = AuthenticationForm
    
    def get_success_url(self):
        """Redireciona para a página inicial após login bem-sucedido."""
        return reverse_lazy('usuarios:home')
    
    def form_valid(self, form):
        """Override para adicionar mensagem de sucesso."""
        messages.success(self.request, f'Bem-vindo, {form.get_user().first_name or form.get_user().username}!')
        return super().form_valid(form)


@login_required
def profile(request):
    """
    View para o perfil do usuário logado.
    """
    return render(request, 'usuarios/profile.html', {'user': request.user})


def logout_view(request):
    """
    View personalizada para logout que aceita requisições GET.
    """
    logout(request)
    messages.success(request, 'Você foi deslogado com sucesso!')
    return redirect('usuarios:home')
