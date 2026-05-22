from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # URLs para Ocorrência
    path('ocorrencias/', views.OcorrenciaListView.as_view(), name='ocorrencia_list'),
    path('ocorrencias/nova/', views.OcorrenciaCreateView.as_view(), name='ocorrencia_create'),
    path('ocorrencias/<int:pk>/', views.OcorrenciaDetailView.as_view(), name='ocorrencia_detail'),
    path('ocorrencias/<int:pk>/editar/', views.OcorrenciaUpdateView.as_view(), name='ocorrencia_update'),
    path('ocorrencias/<int:pk>/excluir/', views.OcorrenciaDeleteView.as_view(), name='ocorrencia_delete'),
    
    # URLs para Evolução do Tratamento
    path('evolucao-tratamento/nova/', views.EvolucaoTratamentoCreateView.as_view(), name='evolucao_tratamento_create'),
    
    # APIs para autocomplete
    path('api/cbo/', views.autocomplete_cbo, name='autocomplete_cbo'),
    path('api/cid/', views.autocomplete_cid, name='autocomplete_cid'),
    path('api/estabelecimentos/', views.autocomplete_estabelecimentos, name='autocomplete_estabelecimentos'),
    
    # API para carregar municípios por estado
    path('api/municipios/', views.load_municipios, name='load_municipios'),
    path('api/cep/', views.consulta_cep, name='consulta_cep'),
]
