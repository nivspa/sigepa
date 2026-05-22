import re


def limpar_digitos(valor):
    if not valor:
        return ''
    return re.sub(r'\D', '', str(valor))


def validar_cpf(cpf):
    """Valida CPF pelos dígitos verificadores (módulo 11)."""
    cpf = limpar_digitos(cpf)
    if len(cpf) != 11:
        return False
    if cpf == cpf[0] * 11:
        return False

    def digito_verificador(base, peso_inicial):
        soma = sum(int(base[i]) * (peso_inicial - i) for i in range(len(base)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    d1 = digito_verificador(cpf[:9], 10)
    d2 = digito_verificador(cpf[:10], 11)
    return cpf[-2:] == f'{d1}{d2}'


def validar_cns(cns):
    """Valida Cartão Nacional de Saúde (CNS / Cartão SUS)."""
    cns = limpar_digitos(cns)
    if len(cns) != 15:
        return False
    if cns[0] not in '12789':
        return False

    if cns[0] in '12':
        return _validar_cns_definitivo(cns)
    return _validar_cns_provisorio(cns)


def _validar_cns_definitivo(cns):
    pis = cns[:11]
    soma = sum(int(pis[i]) * (15 - i) for i in range(11))
    resto = soma % 11
    dv = 11 - resto
    if dv == 11:
        dv = 0
    if dv == 10:
        soma = sum(int(pis[i]) * (15 - i) for i in range(11)) + 2
        resto = soma % 11
        dv = 11 - resto
    return int(cns[11]) == dv


def _validar_cns_provisorio(cns):
    soma = sum(int(cns[i]) * (15 - i) for i in range(15))
    return soma % 11 == 0
