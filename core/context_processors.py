from django.utils import timezone


def sigepa(request):
    """Data de hoje no fuso configurado (America/Sao_Paulo) para templates e JS."""
    return {'SIGEPA_HOJE': timezone.localdate().isoformat()}
