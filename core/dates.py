IDADE_MAXIMA = 120


def calcular_idade_anos(data_nascimento, data_referencia):
    """Idade em anos completos na data de referência."""
    if not data_nascimento or not data_referencia:
        return None
    if data_nascimento > data_referencia:
        return None
    idade = data_referencia.year - data_nascimento.year
    if (data_referencia.month, data_referencia.day) < (data_nascimento.month, data_nascimento.day):
        idade -= 1
    return max(0, idade)


def data_referencia_para_idade(cleaned_data):
    """Idade na data da notificação (evento epidemiológico) ou hoje se ainda não informada."""
    from django.utils import timezone

    return cleaned_data.get('data_notificacao') or timezone.localdate()
