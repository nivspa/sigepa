import json
import re
import urllib.error
import urllib.request

from django.core.cache import cache

# Código IBGE do estado (idestado na tabela estado)
UF_SIGLA_PARA_ID = {
    'RO': 11, 'AC': 12, 'AM': 13, 'RR': 14, 'PA': 15, 'AP': 16, 'TO': 17,
    'MA': 21, 'PI': 22, 'CE': 23, 'RN': 24, 'PB': 25, 'PE': 26, 'AL': 27,
    'SE': 28, 'BA': 29, 'MG': 31, 'ES': 32, 'RJ': 33, 'SP': 35, 'PR': 41,
    'SC': 42, 'RS': 43, 'MS': 50, 'MT': 51, 'GO': 52, 'DF': 53,
}


def limpar_cep(cep):
    return re.sub(r'\D', '', str(cep or ''))


def consultar_cep(cep):
    """
    Consulta CEP na ViaCEP (https://viacep.com.br) e normaliza para o SIGEPA.
    Retorna dict ou None se não encontrado.
    """
    cep = limpar_cep(cep)
    if len(cep) != 8:
        return None

    cache_key = f'sigepa:cep:{cep}'
    em_cache = cache.get(cache_key)
    if em_cache is not None:
        return em_cache if em_cache else None

    url = f'https://viacep.com.br/ws/{cep}/json/'
    try:
        req = urllib.request.Request(
            url,
            headers={'Accept': 'application/json', 'User-Agent': 'SIGEPA/1.0'},
        )
        with urllib.request.urlopen(req, timeout=8) as resposta:
            dados = json.loads(resposta.read().decode('utf-8'))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError):
        cache.set(cache_key, False, 300)
        return None

    if dados.get('erro'):
        cache.set(cache_key, False, 3600)
        return None

    ibge = str(dados.get('ibge') or '')
    estado_id = None
    municipio_id = None

    if len(ibge) >= 7:
        municipio_id = int(ibge)
        estado_id = int(ibge[:2])
    elif dados.get('uf'):
        estado_id = UF_SIGLA_PARA_ID.get(str(dados['uf']).upper())

    resultado = {
        'cep': limpar_cep(dados.get('cep') or cep),
        'logradouro': (dados.get('logradouro') or '').strip(),
        'complemento': (dados.get('complemento') or '').strip(),
        'bairro': (dados.get('bairro') or '').strip(),
        'localidade': (dados.get('localidade') or '').strip(),
        'uf': (dados.get('uf') or '').strip(),
        'estado_id': estado_id,
        'municipio_id': municipio_id,
    }

    cache.set(cache_key, resultado, 86400)
    return resultado
