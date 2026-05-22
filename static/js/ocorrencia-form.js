// Script para formulário de ocorrência
console.log('🚀 Carregando script de pesquisa...');

// Variáveis globais para controle de paginação
let currentTargetField = null;
let currentPage = 1;
let currentSearch = '';
let currentType = '';

// Configurar CSRF token para AJAX
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Configurar AJAX padrão
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

// Função para abrir modal de pesquisa
function openSearchModal(type, targetField) {
    console.log('📂 Abrindo modal de pesquisa:', type, 'para campo:', targetField);
    currentTargetField = targetField;
    currentType = type;
    currentPage = 1;
    currentSearch = '';
    
    // Limpar campo de pesquisa
    $('#search' + capitalizeFirst(type)).val('');
    
    // Abrir modal apropriado
    $('#modal' + capitalizeFirst(type)).modal('show');
    
    // Carregar primeira página sem filtro (mostrar todos os primeiros itens)
    loadSearchResults(type, 1, '');
    
    // Focar no campo de pesquisa após abrir o modal
    setTimeout(function() {
        $('#search' + capitalizeFirst(type)).focus();
    }, 500);
}

console.log('✅ Função openSearchModal definida');

// Função para executar pesquisa via botão
function executeSearchFromButton(type) {
    const searchField = $('#search' + capitalizeFirst(type));
    const searchTerm = searchField.val();
    console.log('🔍 Pesquisa via botão:', type, 'termo:', searchTerm);
    
    currentSearch = searchTerm;
    currentPage = 1;
    loadSearchResults(type, 1, searchTerm);
}

// Função para limpar pesquisa
function clearSearch(type) {
    console.log('🧹 Limpando pesquisa:', type);
    const searchField = $('#search' + capitalizeFirst(type));
    searchField.val('');
    
    currentSearch = '';
    currentPage = 1;
    loadSearchResults(type, 1, '');
    
    // Focar novamente no campo
    searchField.focus();
}
    
// Função para capitalizar primeira letra
function capitalizeFirst(str) {
    if (str === 'estabelecimentos') return 'Estabelecimentos';
    if (str === 'cbo') return 'Cbo';
    if (str === 'cid') return 'Cid';
    return str;
}
    
// Função para carregar resultados de pesquisa
function loadSearchResults(type, page, search) {
    console.log('🔍 Carregando resultados:', type, 'página:', page, 'busca:', search);
    const loading = $('#loading' + capitalizeFirst(type));
    const results = $('#results' + capitalizeFirst(type));
    const pagination = $('#pagination' + capitalizeFirst(type));
    
    // Mostrar loading
    loading.removeClass('d-none');
    results.empty();
    pagination.empty();
    
    // Fazer requisição
    $.ajax({
        url: '/core/api/' + type + '/',
        data: {
            q: search || '',
            page: page || 1
        },
        success: function(data) {
            console.log('✅ Dados recebidos:', data);
            loading.addClass('d-none');
            renderResults(type, data.results || []);
            renderPagination(type, data.pagination || {});
        },
        error: function(xhr, status, error) {
            console.error('❌ Erro na busca:', error, xhr.responseText);
            loading.addClass('d-none');
            results.html('<div class="alert alert-danger">Erro ao carregar dados: ' + error + '</div>');
        }
    });
}
    
// Função para renderizar resultados
function renderResults(type, results) {
    const container = $('#results' + capitalizeFirst(type));
    
    if (results.length === 0) {
        container.html('<div class="alert alert-info">Nenhum resultado encontrado.</div>');
        return;
    }
    
    let html = '<div class="list-group">';
    results.forEach(function(item) {
        html += `
            <div class="list-group-item d-flex justify-content-between align-items-center">
                <span>${item.text}</span>
                <button type="button" class="btn btn-primary btn-sm" onclick="selectItem('${item.id}', '${item.text.replace(/\'/g, "\\'")}')">
                    Selecionar
                </button>
            </div>
        `;
    });
    html += '</div>';
    
    container.html(html);
}
    
// Função para renderizar paginação
function renderPagination(type, pagination) {
    const container = $('#pagination' + capitalizeFirst(type));
    
    if (!pagination.total_pages || pagination.total_pages <= 1) {
        return;
    }
    
    let html = '';
    
    // Botão anterior
    if (pagination.current_page > 1) {
        html += `<li class="page-item">
            <a class="page-link" href="#" onclick="changePage(${pagination.current_page - 1})">Anterior</a>
        </li>`;
    }
    
    // Páginas
    for (let i = 1; i <= pagination.total_pages; i++) {
        if (i === pagination.current_page) {
            html += `<li class="page-item active"><span class="page-link">${i}</span></li>`;
        } else if (i === 1 || i === pagination.total_pages || Math.abs(i - pagination.current_page) <= 2) {
            html += `<li class="page-item">
                <a class="page-link" href="#" onclick="changePage(${i})">${i}</a>
            </li>`;
        } else if (i === pagination.current_page - 3 || i === pagination.current_page + 3) {
            html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
    }
    
    // Botão próximo
    if (pagination.current_page < pagination.total_pages) {
        html += `<li class="page-item">
            <a class="page-link" href="#" onclick="changePage(${pagination.current_page + 1})">Próximo</a>
        </li>`;
    }
    
    container.html(html);
}
    
// Função para mudar página
function changePage(page) {
    currentPage = page;
    loadSearchResults(currentType, page, currentSearch);
}

// Função para selecionar item
function selectItem(id, text) {
    const $select = $(currentTargetField);
    if ($select.find(`option[value="${id}"]`).length === 0) {
        const option = new Option(text, id, true, true);
        $select.append(option);
    }

    $select.val(id).trigger('change');

    $('.modal').modal('hide');

    console.log('Item selecionado:', id, text);
}

// Função debounce para otimizar pesquisa
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = function() {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Django gera id="id_id_*" quando o nome do campo já começa com "id_"
function selectByName(fieldName) {
    return `select[name="${fieldName}"]`;
}

// Idade do paciente: calculada pela data de nascimento (somente leitura) ou manual
const IDADE_MAXIMA = 120;
const DATA_NASCIMENTO_SELECTOR = '#id_data_nascimento';
const IDADE_SELECTOR = '#id_idade';
const DATA_REFERENCIA_IDADE_SELECTOR = '#id_data_notificacao';

function parseDataISO(str) {
    if (!str) {
        return null;
    }
    const partes = str.split('-').map(Number);
    if (partes.length !== 3 || partes.some(isNaN)) {
        return null;
    }
    return new Date(partes[0], partes[1] - 1, partes[2]);
}

function formatarDataISO(data) {
    const y = data.getFullYear();
    const m = String(data.getMonth() + 1).padStart(2, '0');
    const d = String(data.getDate()).padStart(2, '0');
    return y + '-' + m + '-' + d;
}

function obterDataReferenciaIdade() {
    const notificacao = $(DATA_REFERENCIA_IDADE_SELECTOR).val();
    if (notificacao) {
        return { iso: notificacao, origem: 'notificacao' };
    }
    const doServidor = document.documentElement.getAttribute('data-sigepa-hoje');
    const iso = doServidor || formatarDataISO(new Date());
    return { iso: iso, origem: 'hoje' };
}

function limparErroCampo($el) {
    if (!$el || !$el.length) {
        return;
    }
    $el.removeClass('is-invalid is-valid');
    const el = $el[0];
    if (el && typeof el.setCustomValidity === 'function') {
        el.setCustomValidity('');
    }
}

function marcarErroCampo($el) {
    if (!$el || !$el.length) {
        return;
    }
    $el.addClass('is-invalid');
    const el = $el[0];
    if (el && typeof el.setCustomValidity === 'function') {
        el.setCustomValidity('Valor inválido.');
    }
}

function calcularIdadeAnos(dataNascISO, dataRefISO) {
    const nasc = parseDataISO(dataNascISO);
    const ref = parseDataISO(dataRefISO);
    if (!nasc || !ref || nasc > ref) {
        return null;
    }
    let idade = ref.getFullYear() - nasc.getFullYear();
    if (
        ref.getMonth() < nasc.getMonth()
        || (ref.getMonth() === nasc.getMonth() && ref.getDate() < nasc.getDate())
    ) {
        idade -= 1;
    }
    return Math.max(0, idade);
}

function atualizarCampoIdadePaciente() {
    const $nasc = $(DATA_NASCIMENTO_SELECTOR);
    const $idade = $(IDADE_SELECTOR);

    if (!$nasc.length || !$idade.length) {
        return;
    }

    const nascVal = $nasc.val();

    if (nascVal) {
        const refInfo = obterDataReferenciaIdade();
        const idade = calcularIdadeAnos(nascVal, refInfo.iso);
        if (idade !== null && idade > IDADE_MAXIMA) {
            $idade.val('');
            marcarErroCampo($nasc);
            limparErroCampo($idade);
            $idade.prop('readonly', false);
            $idade.removeClass('idade-calculada');
            return;
        }
        limparErroCampo($nasc);
        limparErroCampo($idade);
        if (idade !== null) {
            $idade.val(String(idade));
        }
        $idade.prop('readonly', true);
        $idade.addClass('idade-calculada');
        $idade.attr('title', 'Calculada a partir da data de nascimento');
    } else {
        limparErroCampo($nasc);
        $idade.prop('readonly', false);
        $idade.removeClass('idade-calculada');
        $idade.removeAttr('title');
        validarIdadeManual();
    }
}

function validarIdadeManual() {
    const $idade = $(IDADE_SELECTOR);
    if (!$idade.length) {
        return;
    }
    if ($idade.prop('readonly')) {
        limparErroCampo($idade);
        return;
    }
    const valor = parseInt($idade.val(), 10);
    if ($idade.val() && (!Number.isFinite(valor) || valor < 0 || valor > IDADE_MAXIMA)) {
        marcarErroCampo($idade);
    } else {
        limparErroCampo($idade);
    }
}

// Tempo de gestação: visível apenas para sexo feminino
const SEXO_FEMININO_ID = '2';
const TEMPO_GESTACAO_NAO_APLICA_ID = '21';
const SEXO_SELECTOR = selectByName('id_sexo');
const GESTACAO_WRAP_SELECTOR = '#campo-tempo-gestacao-wrap';
const GESTACAO_SELECTOR = selectByName('id_tempo_gestacao');

function sexoEhFeminino(valorSexo) {
    if (!valorSexo) {
        return false;
    }
    if (String(valorSexo) === SEXO_FEMININO_ID) {
        return true;
    }
    const texto = $(SEXO_SELECTOR + ' option:selected').text().toLowerCase();
    return texto.indexOf('feminin') !== -1;
}

function atualizarCampoTempoGestacao() {
    const $wrap = $(GESTACAO_WRAP_SELECTOR);
    const $gestacao = $(GESTACAO_SELECTOR);
    const $sexo = $(SEXO_SELECTOR);

    if (!$wrap.length || !$gestacao.length || !$sexo.length) {
        return;
    }

    const valorSexo = $sexo.val();

    if (sexoEhFeminino(valorSexo)) {
        $wrap.removeClass('d-none');
        $gestacao.prop('disabled', false);
        $gestacao.prop('required', true);
        if ($gestacao.val() === TEMPO_GESTACAO_NAO_APLICA_ID) {
            $gestacao.val('');
        }
    } else {
        $wrap.addClass('d-none');
        $gestacao.val(TEMPO_GESTACAO_NAO_APLICA_ID);
        $gestacao.prop('disabled', false);
        $gestacao.prop('required', false);
        limparErroCampo($gestacao);
    }
}

// CPF e Cartão SUS (CNS) — validação por dígito verificador
const CPF_SELECTOR = '#id_cpf';
const CNS_SELECTOR = '#id_cartao_sus';

function limparDigitos(valor) {
    return String(valor || '').replace(/\D/g, '');
}

function validarCpfJs(cpf) {
    cpf = limparDigitos(cpf);
    if (cpf.length !== 11) {
        return false;
    }
    if (/^(\d)\1{10}$/.test(cpf)) {
        return false;
    }

    function digito(base, pesoInicial) {
        let soma = 0;
        for (let i = 0; i < base.length; i++) {
            soma += parseInt(base.charAt(i), 10) * (pesoInicial - i);
        }
        const resto = soma % 11;
        return resto < 2 ? 0 : 11 - resto;
    }

    const d1 = digito(cpf.substring(0, 9), 10);
    const d2 = digito(cpf.substring(0, 10), 11);
    return cpf.substring(9, 11) === String(d1) + String(d2);
}

function validarCnsDefinitivoJs(cns) {
    const pis = cns.substring(0, 11);
    let soma = 0;
    for (let i = 0; i < 11; i++) {
        soma += parseInt(pis.charAt(i), 10) * (15 - i);
    }
    let resto = soma % 11;
    let dv = 11 - resto;
    if (dv === 11) {
        dv = 0;
    }
    if (dv === 10) {
        soma = 0;
        for (let i = 0; i < 11; i++) {
            soma += parseInt(pis.charAt(i), 10) * (15 - i);
        }
        soma += 2;
        resto = soma % 11;
        dv = 11 - resto;
    }
    return parseInt(cns.charAt(11), 10) === dv;
}

function validarCnsProvisorioJs(cns) {
    let soma = 0;
    for (let i = 0; i < 15; i++) {
        soma += parseInt(cns.charAt(i), 10) * (15 - i);
    }
    return soma % 11 === 0;
}

function validarCnsJs(cns) {
    cns = limparDigitos(cns);
    if (cns.length !== 15) {
        return false;
    }
    if ('12789'.indexOf(cns.charAt(0)) === -1) {
        return false;
    }
    if (cns.charAt(0) === '1' || cns.charAt(0) === '2') {
        return validarCnsDefinitivoJs(cns);
    }
    return validarCnsProvisorioJs(cns);
}

function formatarCpf(valor) {
    const d = limparDigitos(valor).substring(0, 11);
    if (d.length <= 3) {
        return d;
    }
    if (d.length <= 6) {
        return d.substring(0, 3) + '.' + d.substring(3);
    }
    if (d.length <= 9) {
        return d.substring(0, 3) + '.' + d.substring(3, 6) + '.' + d.substring(6);
    }
    return d.substring(0, 3) + '.' + d.substring(3, 6) + '.' + d.substring(6, 9) + '-' + d.substring(9);
}

function formatarCns(valor) {
    const d = limparDigitos(valor).substring(0, 15);
    return d.replace(/(\d{3})(?=\d)/g, '$1 ').trim();
}

const TELEFONE_SELECTORS = [
    'input[name="telefone"]',
    'input[name="telefone_dono"]',
    'input[name="telefone_condutor"]',
];

function formatarTelefone(valor) {
    const d = limparDigitos(valor).substring(0, 11);
    if (!d.length) {
        return '';
    }
    if (d.length <= 2) {
        return d.length === 2 ? `(${d}) ` : `(${d}`;
    }

    const ddd = d.substring(0, 2);
    const resto = d.substring(2);

    if (resto.length <= 4) {
        return `(${ddd}) ${resto}`;
    }
    if (d.length <= 10) {
        return `(${ddd}) ${resto.substring(0, 4)}-${resto.substring(4)}`;
    }
    return `(${ddd}) ${resto.substring(0, 5)}-${resto.substring(5)}`;
}

function aplicarMascaraTelefone($el) {
    const formatado = formatarTelefone($el.val());
    if ($el.val() !== formatado) {
        $el.val(formatado);
    }
}

function configurarMascaraTelefones() {
    TELEFONE_SELECTORS.forEach(function(seletor) {
        const $campos = $(seletor);
        if (!$campos.length) {
            return;
        }

        $campos.each(function() {
            const $el = $(this);
            aplicarMascaraTelefone($el);

            $el.off('input.telefone blur.telefone');
            $el.on('input.telefone', function() {
                aplicarMascaraTelefone($el);
            });
            $el.on('blur.telefone', function() {
                aplicarMascaraTelefone($el);
            });
        });
    });
}

function validarCampoDocumento($el, validador, mensagem) {
    const bruto = $el.val();
    if (!bruto || !limparDigitos(bruto)) {
        limparErroCampo($el);
        return;
    }
    if (validador(bruto)) {
        limparErroCampo($el);
    } else {
        marcarErroCampo($el);
        const el = $el[0];
        if (el) {
            el.setCustomValidity(mensagem);
        }
    }
}

// CEP — busca endereço (ViaCEP via API SIGEPA)
const CEP_SELECTOR = '#id_cep';
const UF_RESIDENCIA_SELECTOR = selectByName('id_uf_residencia');
const MUNICIPIO_RESIDENCIA_SELECTOR = selectByName('id_municipio_residencia');
let cepBuscaTimeout = null;
let cepUltimaBusca = '';

function formatarCep(valor) {
    const digitos = limparDigitos(valor).substring(0, 8);
    if (digitos.length <= 5) {
        return digitos;
    }
    return digitos.substring(0, 5) + '-' + digitos.substring(5);
}

function mostrarLoadingCep(mostrar) {
    const $loading = $('#cep-loading');
    if ($loading.length) {
        $loading.toggleClass('d-none', !mostrar);
    }
}

function preencherEnderecoPorCep(dados) {
    const $cep = $(CEP_SELECTOR);
    const $logradouro = $('input[name="logradouro"]');
    const $bairro = $('input[name="bairro"]');
    const $complemento = $('input[name="complemento"]');
    const $distrito = $('input[name="distrito"]');
    const $uf = $(UF_RESIDENCIA_SELECTOR);
    const $municipio = $(MUNICIPIO_RESIDENCIA_SELECTOR);

    $cep.val(formatarCep(dados.cep || $cep.val()));
    limparErroCampo($cep);

    // Sempre substitui (CEP genérico pode vir só com cidade/UF)
    $logradouro.val(dados.logradouro || '');
    $bairro.val(dados.bairro || '');
    $complemento.val(dados.complemento || '');
    $distrito.val('');

    limparErroCampo($logradouro);
    limparErroCampo($bairro);
    limparErroCampo($complemento);

    if (dados.estado_id) {
        $uf.val(String(dados.estado_id));
        loadMunicipiosComFiltro(
            MUNICIPIO_RESIDENCIA_SELECTOR,
            dados.estado_id,
            'Residência (CEP)',
            function($selectMunicipio) {
                if (dados.municipio_id) {
                    $selectMunicipio.val(String(dados.municipio_id));
                    $selectMunicipio.trigger('change');
                }
            }
        );
    }

    $('input[name="numero"]').trigger('focus');
}

function buscarEnderecoPorCep() {
    const $cep = $(CEP_SELECTOR);
    if (!$cep.length) {
        return;
    }

    const cep = limparDigitos($cep.val());
    if (cep.length !== 8) {
        return;
    }
    if (cep === cepUltimaBusca) {
        return;
    }

    cepUltimaBusca = cep;
    mostrarLoadingCep(true);
    limparErroCampo($cep);

    $.ajax({
        url: '/core/api/cep/',
        method: 'GET',
        data: { cep: cep },
        dataType: 'json',
        timeout: 10000,
        success: function(resposta) {
            mostrarLoadingCep(false);
            if (resposta.success && resposta.endereco) {
                preencherEnderecoPorCep(resposta.endereco);
            } else {
                marcarErroCampo($cep);
            }
        },
        error: function(xhr) {
            mostrarLoadingCep(false);
            marcarErroCampo($cep);
            const el = $cep[0];
            if (el) {
                const msg = (xhr.responseJSON && xhr.responseJSON.error) || 'CEP não encontrado.';
                el.setCustomValidity(msg);
            }
        }
    });
}

function agendarBuscaCep() {
    const $cep = $(CEP_SELECTOR);
    if (!$cep.length) {
        return;
    }

    const cep = limparDigitos($cep.val());
    clearTimeout(cepBuscaTimeout);

    if (cep.length < 8) {
        cepUltimaBusca = '';
        limparErroCampo($cep);
        return;
    }

    $cep.val(formatarCep(cep));
    cepBuscaTimeout = setTimeout(buscarEnderecoPorCep, 400);
}

function configurarBuscaCep() {
    const $cep = $(CEP_SELECTOR);
    if (!$cep.length) {
        return;
    }

    $cep.off('input.cepBusca blur.cepBusca');
    $cep.on('input.cepBusca', agendarBuscaCep);
    $cep.on('blur.cepBusca', function() {
        $cep.val(formatarCep($cep.val()));
        buscarEnderecoPorCep();
    });

    const tabEndereco = document.getElementById('endereco-tab');
    if (tabEndereco) {
        tabEndereco.addEventListener('shown.bs.tab', function() {
            $cep.trigger('focus');
        });
    }
}

function configurarValidacaoCpfCns() {
    const $cpf = $(CPF_SELECTOR);
    const $cns = $(CNS_SELECTOR);

    if ($cpf.length) {
        $cpf.off('blur.cpfCns');
        $cpf.on('blur.cpfCns', function() {
            $cpf.val(formatarCpf($cpf.val()));
            validarCampoDocumento($cpf, validarCpfJs, 'CPF inválido.');
        });
    }

    if ($cns.length) {
        $cns.off('blur.cpfCns');
        $cns.on('blur.cpfCns', function() {
            $cns.val(formatarCns($cns.val()));
            validarCampoDocumento($cns, validarCnsJs, 'Cartão SUS (CNS) inválido.');
        });
    }
}

function configurarTempoGestacaoPorSexo() {
    const $sexo = $(SEXO_SELECTOR);
    if (!$sexo.length) {
        return;
    }

    $sexo.off('change.tempoGestacao');
    $sexo.on('change.tempoGestacao', atualizarCampoTempoGestacao);
    atualizarCampoTempoGestacao();
}

function configurarIdadePaciente() {
    const $nasc = $(DATA_NASCIMENTO_SELECTOR);
    const $idade = $(IDADE_SELECTOR);

    if (!$nasc.length || !$idade.length) {
        return;
    }

    $nasc.off('change.idadePaciente input.idadePaciente');
    $nasc.on('change.idadePaciente input.idadePaciente', atualizarCampoIdadePaciente);

    $(DATA_REFERENCIA_IDADE_SELECTOR).off('change.idadePaciente');
    $(DATA_REFERENCIA_IDADE_SELECTOR).on('change.idadePaciente', atualizarCampoIdadePaciente);

    $idade.off('input.idadePaciente blur.idadePaciente');
    $idade.on('input.idadePaciente blur.idadePaciente', validarIdadeManual);

    const tabPaciente = document.getElementById('paciente-tab');
    if (tabPaciente) {
        tabPaciente.addEventListener('shown.bs.tab', function() {
            atualizarCampoIdadePaciente();
            atualizarCampoTempoGestacao();
        });
    }

    atualizarCampoIdadePaciente();
}

// UF da notificação (lista completa no HTML)
const UF_NOTIFICACAO_SELECTOR = selectByName('id_uf_notificacao');

const SELECT2_UF_OPTS = {
    theme: 'bootstrap-5',
    width: '100%',
    placeholder: 'Digite para buscar a UF...',
    allowClear: false,
    minimumResultsForSearch: 0,
    dropdownCssClass: 'select2-busca-unificada',
    language: {
        noResults: function() { return 'Nenhuma UF encontrada'; },
        searching: function() { return 'Buscando...'; }
    }
};

function destroySelect2Busca(selector) {
    const $el = $(selector);
    if (!$el.length) {
        return;
    }
    $el.parent('.select-busca-wrap').removeClass('select2-aberto');
    if ($el.hasClass('select2-hidden-accessible')) {
        try {
            $el.select2('destroy');
        } catch (e) {
            /* já destruído */
        }
    }
    $el.siblings('.select2-container').remove();
}

function obterWrapperSelect2($el) {
    let $wrap = $el.parent('.select-busca-wrap');
    if (!$wrap.length) {
        $el.wrap('<div class="select-busca-wrap"></div>');
        $wrap = $el.parent('.select-busca-wrap');
    }
    return $wrap;
}

function ajustarLarguraDropdown($el) {
    const $wrap = obterWrapperSelect2($el);
    const $container = $el.next('.select2-container');
    const largura = $container.outerWidth();
    const instance = $el.data('select2');
    if (instance && instance.$dropdown) {
        instance.$dropdown.css({
            width: largura + 'px',
            maxWidth: largura + 'px',
            minWidth: largura + 'px'
        });
    }
    $wrap.css('width', largura ? largura + 'px' : '100%');
}

function configurarBuscaNoCampo($el) {
    const $wrap = obterWrapperSelect2($el);

    $el.off('select2:open.buscaCampo select2:close.buscaCampo');
    $el.on('select2:open.buscaCampo', function() {
        $wrap.addClass('select2-aberto');
        ajustarLarguraDropdown($el);

        const $container = $el.next('.select2-container');
        setTimeout(function() {
            const $search = $container.find('.select2-search__field');
            const instance = $el.data('select2');
            const $searchField = instance && instance.$dropdown
                ? instance.$dropdown.find('.select2-search__field')
                : $search;
            const texto = $container.find('.select2-selection__rendered').text().trim();
            const ehPlaceholder = !texto || texto.indexOf('Digite') !== -1 || texto === 'Selecione...';

            $searchField.val(ehPlaceholder ? '' : texto);
            $searchField.trigger('focus');
            if ($searchField[0] && $searchField[0].select) {
                $searchField[0].select();
            }
        }, 0);
    });

    $el.on('select2:close.buscaCampo', function() {
        $wrap.removeClass('select2-aberto');
    });
}

function initSelect2Busca(selector, options) {
    if (typeof $.fn.select2 !== 'function') {
        console.error('Select2 não está disponível');
        return false;
    }

    const $el = $(selector);
    if ($el.length === 0 || $el.find('option').length <= 1) {
        return false;
    }

    destroySelect2Busca(selector);

    const $wrap = obterWrapperSelect2($el);
    const opts = $.extend({}, options, {
        dropdownParent: $wrap,
        minimumResultsForSearch: options.minimumResultsForSearch !== undefined
            ? options.minimumResultsForSearch
            : 0,
        dropdownCssClass: ((options.dropdownCssClass || '') + ' select2-busca-unificada').trim()
    });

    $el.select2(opts);
    if ($el.hasClass('select2-hidden-accessible')) {
        configurarBuscaNoCampo($el);
    }
    return $el.hasClass('select2-hidden-accessible');
}

function initSelect2UfNotificacao() {
    const $uf = $(UF_NOTIFICACAO_SELECTOR);
    if (!$uf.length) {
        return false;
    }

    // Select2 exige opção vazia para placeholder + caixa de busca
    if ($uf.find('option[value=""]').length === 0) {
        $uf.prepend($('<option value=""></option>'));
    }

    const ok = initSelect2Busca(UF_NOTIFICACAO_SELECTOR, SELECT2_UF_OPTS);
    if (!ok) {
        console.warn('Select2 não aplicado em UF da notificação');
    }
    return ok;
}

// Todos os selects de município do formulário de ocorrência
const MUNICIPIO_SELECTORS = [
    selectByName('id_municipio_notificacao'),
    selectByName('id_municipio_residencia'),
    selectByName('id_municipio_transferencia'),
    selectByName('id_municipio_ocorrencia'),
    selectByName('id_municipio_investigador')
];

const SELECT2_MUNICIPIO_OPTS = {
    theme: 'bootstrap-5',
    width: '100%',
    placeholder: 'Digite para buscar o município...',
    allowClear: false,
    minimumResultsForSearch: 0,
    dropdownCssClass: 'select2-busca-unificada',
    language: {
        noResults: function() { return 'Nenhum município encontrado'; },
        searching: function() { return 'Buscando...'; }
    }
};

function destroySelect2Municipio(selector) {
    destroySelect2Busca(selector);
}

function initSelect2Municipio(selector) {
    initSelect2Busca(selector, SELECT2_MUNICIPIO_OPTS);
}

function initSelect2Municipios() {
    MUNICIPIO_SELECTORS.forEach(initSelect2Municipio);
}

// CNES — busca AJAX no campo (mín. 3 caracteres) + modal pela lupa
const CNES_SELECTORS = [
    selectByName('id_cnes'),
    selectByName('id_cnes_invertigador'),
    selectByName('id_unidade_atendimento'),
    selectByName('id_cnes_investigacao')
];

const SELECT2_CNES_OPTS = {
    theme: 'bootstrap-5',
    width: '100%',
    placeholder: 'Digite CNES ou nome (mín. 3 caracteres)...',
    allowClear: true,
    minimumInputLength: 3,
    dropdownCssClass: 'select2-busca-unificada',
    language: {
        inputTooShort: function(args) {
            const restantes = args.minimum - args.input.length;
            return 'Digite mais ' + restantes + ' caractere' + (restantes === 1 ? '' : 's');
        },
        noResults: function() { return 'Nenhum estabelecimento encontrado'; },
        searching: function() { return 'Buscando...'; }
    },
    ajax: {
        url: '/core/api/estabelecimentos/',
        dataType: 'json',
        delay: 300,
        data: function(params) {
            return {
                q: params.term || '',
                page: params.page || 1
            };
        },
        processResults: function(data, params) {
            params.page = params.page || 1;
            const pagination = data.pagination || {};
            return {
                results: data.results || [],
                pagination: {
                    more: Boolean(pagination.has_next)
                }
            };
        },
        cache: true
    }
};

function initSelect2Cnes(selector) {
    if (typeof $.fn.select2 !== 'function') {
        console.error('Select2 não está disponível');
        return false;
    }

    const $el = $(selector);
    if (!$el.length) {
        return false;
    }

    destroySelect2Busca(selector);

    const $wrap = obterWrapperSelect2($el);
    const placeholder = $el.data('placeholder') || SELECT2_CNES_OPTS.placeholder;

    if ($el.find('option[value=""]').length === 0) {
        $el.prepend($('<option value=""></option>'));
    }

    const opts = $.extend(true, {}, SELECT2_CNES_OPTS, {
        dropdownParent: $wrap,
        placeholder: placeholder,
        allowClear: $el.attr('name') !== 'id_cnes'
    });

    $el.select2(opts);

    if ($el.hasClass('select2-hidden-accessible')) {
        configurarBuscaNoCampo($el);
    }

    return $el.hasClass('select2-hidden-accessible');
}

function initSelect2CnesFields() {
    CNES_SELECTORS.forEach(function(selector) {
        const ok = initSelect2Cnes(selector);
        if (!ok) {
            console.warn('Select2 AJAX não aplicado em', selector);
        }
    });
}

// CBO — busca AJAX no campo (mín. 3 caracteres) + modal pela lupa
const CBO_SELECTORS = [
    selectByName('id_cbo'),
    selectByName('funcao_invertigador'),
    selectByName('id_funcao_investigador')
];

const SELECT2_CBO_OPTS = {
    theme: 'bootstrap-5',
    width: '100%',
    placeholder: 'Digite código ou ocupação (mín. 3 caracteres)...',
    allowClear: true,
    minimumInputLength: 3,
    dropdownCssClass: 'select2-busca-unificada',
    language: {
        inputTooShort: function(args) {
            const restantes = args.minimum - args.input.length;
            return 'Digite mais ' + restantes + ' caractere' + (restantes === 1 ? '' : 's');
        },
        noResults: function() { return 'Nenhuma ocupação (CBO) encontrada'; },
        searching: function() { return 'Buscando...'; }
    },
    ajax: {
        url: '/core/api/cbo/',
        dataType: 'json',
        delay: 300,
        data: function(params) {
            return {
                q: params.term || '',
                page: params.page || 1
            };
        },
        processResults: function(data, params) {
            params.page = params.page || 1;
            const pagination = data.pagination || {};
            return {
                results: data.results || [],
                pagination: {
                    more: Boolean(pagination.has_next)
                }
            };
        },
        cache: true
    }
};

function initSelect2Cbo(selector) {
    if (typeof $.fn.select2 !== 'function') {
        console.error('Select2 não está disponível');
        return false;
    }

    const $el = $(selector);
    if (!$el.length) {
        return false;
    }

    destroySelect2Busca(selector);

    const $wrap = obterWrapperSelect2($el);
    const placeholder = $el.data('placeholder') || SELECT2_CBO_OPTS.placeholder;

    if ($el.find('option[value=""]').length === 0) {
        $el.prepend($('<option value=""></option>'));
    }

    const opts = $.extend(true, {}, SELECT2_CBO_OPTS, {
        dropdownParent: $wrap,
        placeholder: placeholder,
        allowClear: true
    });

    $el.select2(opts);

    if ($el.hasClass('select2-hidden-accessible')) {
        configurarBuscaNoCampo($el);
    }

    return $el.hasClass('select2-hidden-accessible');
}

function initSelect2CboFields() {
    CBO_SELECTORS.forEach(function(selector) {
        const ok = initSelect2Cbo(selector);
        if (!ok) {
            console.warn('Select2 AJAX CBO não aplicado em', selector);
        }
    });
}

// CID — busca AJAX no campo (mín. 3 caracteres) + modal pela lupa
const CID_SELECTORS = [
    selectByName('id_cid')
];

const SELECT2_CID_OPTS = {
    theme: 'bootstrap-5',
    width: '100%',
    placeholder: 'Digite código ou descrição CID (mín. 3 caracteres)...',
    allowClear: true,
    minimumInputLength: 3,
    dropdownCssClass: 'select2-busca-unificada',
    language: {
        inputTooShort: function(args) {
            const restantes = args.minimum - args.input.length;
            return 'Digite mais ' + restantes + ' caractere' + (restantes === 1 ? '' : 's');
        },
        noResults: function() { return 'Nenhum CID encontrado'; },
        searching: function() { return 'Buscando...'; }
    },
    ajax: {
        url: '/core/api/cid/',
        dataType: 'json',
        delay: 300,
        data: function(params) {
            return {
                q: params.term || '',
                page: params.page || 1
            };
        },
        processResults: function(data, params) {
            params.page = params.page || 1;
            const pagination = data.pagination || {};
            return {
                results: data.results || [],
                pagination: {
                    more: Boolean(pagination.has_next)
                }
            };
        },
        cache: true
    }
};

function initSelect2Cid(selector) {
    if (typeof $.fn.select2 !== 'function') {
        console.error('Select2 não está disponível');
        return false;
    }

    const $el = $(selector);
    if (!$el.length) {
        return false;
    }

    destroySelect2Busca(selector);

    const $wrap = obterWrapperSelect2($el);
    const placeholder = $el.data('placeholder') || SELECT2_CID_OPTS.placeholder;

    if ($el.find('option[value=""]').length === 0) {
        $el.prepend($('<option value=""></option>'));
    }

    const opts = $.extend(true, {}, SELECT2_CID_OPTS, {
        dropdownParent: $wrap,
        placeholder: placeholder,
        allowClear: true
    });

    $el.select2(opts);

    if ($el.hasClass('select2-hidden-accessible')) {
        configurarBuscaNoCampo($el);
    }

    return $el.hasClass('select2-hidden-accessible');
}

function initSelect2CidFields() {
    CID_SELECTORS.forEach(function(selector) {
        const ok = initSelect2Cid(selector);
        if (!ok) {
            console.warn('Select2 AJAX CID não aplicado em', selector);
        }
    });
}

// Função para carregar municípios (com ou sem filtro de UF)
function loadMunicipiosComFiltro(target, ufId = null, nomeContexto = '', aoConcluir = null) {
    console.log(`🔄 Carregando municípios para: ${target}${ufId ? ` (UF: ${ufId})` : ' (todos)'}${nomeContexto ? ` - ${nomeContexto}` : ''}`);
    
    if (!target) {
        console.log('⚠️ Target não fornecido');
        return;
    }
    
    var municipioSelect = $(target);
    if (municipioSelect.length === 0) {
        console.error('❌ Elemento target não encontrado:', target);
        return;
    }
    
    // Preservar valor atual em modo de edição
    const currentValue = municipioSelect.val();
    const isEdit = isEditMode();
    
    destroySelect2Municipio(target);

    // Mostrar indicador de carregamento
    municipioSelect.prop('disabled', true);
    municipioSelect.html('<option value="">Carregando...</option>');
    
    const url = '/core/api/municipios/';
    const data = ufId ? { 'estado_id': ufId } : {};
    
    console.log(`📡 Fazendo requisição AJAX para ${ufId ? `municípios da UF ${ufId}` : 'todos os municípios'}...`);
    
    $.ajax({
        url: url,
        method: 'GET',
        data: data,
        dataType: 'json',
        timeout: 15000,
        success: function(data) {
            console.log(`✅ Resposta da API (${nomeContexto || 'municípios'}):`, data);
            
            try {
                // Limpar select atual
                municipioSelect.empty();
                municipioSelect.append('<option value="">Selecione...</option>');
                
                // Verificar se a resposta é válida
                if (data && data.success !== false) {
                    // Adicionar municípios
                    if (data.municipios && Array.isArray(data.municipios) && data.municipios.length > 0) {
                        $.each(data.municipios, function(index, municipio) {
                            if (municipio && municipio.id && municipio.nome) {
                                municipioSelect.append('<option value="' + municipio.id + '">' + municipio.nome + '</option>');
                            }
                        });
                        console.log(`📋 ${nomeContexto ? nomeContexto + ' - ' : ''}Municípios carregados: ${data.municipios.length}`);
                    } else {
                        municipioSelect.append('<option value="">Nenhum município encontrado</option>');
                        console.log(`⚠️ Nenhum município encontrado${ufId ? ` para UF ${ufId}` : ''}`);
                    }
                } else {
                    municipioSelect.append('<option value="">Erro na resposta do servidor</option>');
                    console.log('❌ Resposta inválida da API:', data);
                }
            } catch (e) {
                console.error('❌ Erro ao processar dados dos municípios:', e);
                municipioSelect.empty();
                municipioSelect.append('<option value="">Erro ao processar dados</option>');
            }
            
            // Restaurar valor selecionado em modo de edição (exceto quando veio do CEP)
            if (typeof aoConcluir === 'function') {
                aoConcluir(municipioSelect);
            } else if (isEdit && currentValue) {
                municipioSelect.val(currentValue);
                console.log(`🔄 Valor restaurado para ${target}: ${currentValue}`);
            }

            // Reabilitar o select
            municipioSelect.prop('disabled', false);
            initSelect2Municipio(target);
        },
        error: function(xhr, status, error) {
            console.error(`❌ Erro na requisição AJAX (${nomeContexto || 'municípios'}):`, {
                error: error,
                status: status,
                responseText: xhr.responseText,
                url: url,
                ufId: ufId
            });
            
            municipioSelect.empty();
            
            let errorMessage = 'Erro ao carregar municípios';
            if (status === 'timeout') {
                errorMessage = 'Timeout - tente novamente';
            } else if (status === 'abort') {
                errorMessage = 'Requisição cancelada';
            } else if (xhr.status === 404) {
                errorMessage = 'API não encontrada';
            } else if (xhr.status === 500) {
                errorMessage = 'Erro do servidor';
            }
            
            municipioSelect.append('<option value="">' + errorMessage + '</option>');
            municipioSelect.prop('disabled', false);
        }
    });
}

// Função para carregar todos os municípios (para campos sem UF) - mantida para compatibilidade
function loadAllMunicipios(target, nomeContexto = '') {
    return loadMunicipiosComFiltro(target, null, nomeContexto);
}

// Municípios fixos do Pará (SIGEPA atua no estado do Pará)
const UF_PARA_ID = 15;

// Campos de município sem UF associada no formulário — sempre Pará
const MUNICIPIOS_UF_PARA = [
    { selector: selectByName('id_municipio_ocorrencia'), nome: 'Ocorrência' },
    { selector: selectByName('id_municipio_investigador'), nome: 'Investigador' }
];

function carregarMunicipiosPara(campo) {
    const selector = typeof campo === 'string' ? campo : campo.selector;
    const nome = typeof campo === 'string' ? selector : campo.nome;
    const $select = $(selector);
    if ($select.length === 0) {
        return;
    }
    // Opções já renderizadas pelo Django (municípios do Pará)
    if ($select.find('option').length > 1) {
        console.log(`✅ ${nome}: municípios já presentes no HTML (${$select.find('option').length - 1})`);
        initSelect2Municipio(selector);
        return;
    }
    loadMunicipiosComFiltro(selector, UF_PARA_ID, `Municípios do Pará - ${nome}`);
}

function carregarMunicipiosParaUf(ufSelector, municipioSelector, nomeContexto) {
    const ufId = $(ufSelector).val();
    if (ufId) {
        loadMunicipiosComFiltro(municipioSelector, ufId, nomeContexto);
    } else {
        $(municipioSelector).empty().append('<option value="">Selecione a UF primeiro</option>');
    }
}

// Função para carregar municípios dinamicamente (compatibilidade)
function loadMunicipios(ufId, target) {
    const nomeContexto = `Municípios por UF (${ufId})`;
    return loadMunicipiosComFiltro(target, ufId, nomeContexto);
}

// Função para inicializar o formulário de forma segura
function initializeFormulario(elementosDisponiveis = {}) {
    console.log('🔄 Inicializando formulário com modais de pesquisa...');
    
    // Primeiro, vamos ver todos os elementos de formulário disponíveis
    console.log('🔍 Elementos de formulário disponíveis:');
    $('form input, form select').each(function() {
        if (this.id) {
            console.log('   - ID encontrado:', this.id);
        }
    });
    
    console.log('🔍 Elementos disponíveis passados para inicialização:', elementosDisponiveis);

    // Configurar gatilhos para mudança de UF usando elementos encontrados dinamicamente
    const ufMunicipioMap = [
        { 
            uf: elementosDisponiveis['uf_notificacao'], 
            municipio: elementosDisponiveis['municipio_notificacao'], 
            nome: 'Notificação',
            carregarInicial: false  // Não carregar inicialmente em novos registros
        },
        { 
            uf: elementosDisponiveis['uf_residencia'], 
            municipio: elementosDisponiveis['municipio_residencia'], 
            nome: 'Residência',
            carregarInicial: false  // Não carregar inicialmente em novos registros
        },
        { 
            uf: elementosDisponiveis['uf_transferencia'], 
            municipio: elementosDisponiveis['municipio_transferencia'], 
            nome: 'Transferência',
            carregarInicial: false  // Não carregar inicialmente em novos registros
        }
    ];
    
    ufMunicipioMap.forEach(function(map) {
        if (!map.uf || !map.municipio) {
            console.warn(`⚠️ Elementos não encontrados para ${map.nome}`);
            return;
        }
        
        const $uf = $(map.uf);
        const $municipio = $(map.municipio);
        
        if ($uf.length && $municipio.length) {
            console.log(`✅ Configurando gatilho para UF ${map.nome} (${map.uf} -> ${map.municipio})`);
            
            $uf.on('change', function() {
                var ufId = $(this).val();
                console.log(`🔄 UF ${map.nome} mudou para:`, ufId);
                
                // Em modo de edição, preservar o valor atual do município se não mudou a UF
                const currentMunicipioValue = $municipio.val();
                const isEdit = isEditMode();
                
                // Limpar município atual apenas se não estivermos em modo de edição
                // ou se a UF realmente mudou
                if (!isEdit || !currentMunicipioValue) {
                    $municipio.val('');
                }
                
                if (ufId) {
                    loadMunicipios(ufId, map.municipio);
                } else {
                    $municipio.empty().append('<option value="">Selecione...</option>');
                }
            });
            
            // Carregar municípios se a UF já estiver selecionada (criação ou edição)
            if ($uf.val()) {
                console.log(`📍 Carregando municípios iniciais para ${map.nome}`);
                loadMunicipios($uf.val(), map.municipio);
            }
        } else {
            console.warn(`⚠️ Elementos DOM não encontrados para ${map.nome}: UF=${$uf.length}, Município=${$municipio.length}`);
        }
    });
    
    // Município da ocorrência e do investigador: sempre Pará (sem campo de UF no formulário)
    console.log('🔍 Carregando municípios do Pará (ocorrência e investigador)...');
    [
        { key: 'municipio_ocorrencia', nome: 'Ocorrência', fallback: selectByName('id_municipio_ocorrencia') },
        { key: 'municipio_investigador', nome: 'Investigador', fallback: selectByName('id_municipio_investigador') }
    ].forEach(function(campo) {
        const selector = elementosDisponiveis[campo.key] || campo.fallback;
        carregarMunicipiosPara({ selector: selector, nome: campo.nome });
    });

    setTimeout(function() {
        initSelect2UfNotificacao();
        initSelect2Municipios();
        initSelect2CnesFields();
        initSelect2CboFields();
        initSelect2CidFields();
        configurarIdadePaciente();
        configurarTempoGestacaoPorSexo();
        configurarValidacaoCpfCns();
        configurarBuscaCep();
        configurarMascaraTelefones();
    }, 150);
}

// Função para encontrar elementos com seletores flexíveis
function findElement(baseName) {
    const possibleSelectors = [
        `#id_${baseName}`,
        `#${baseName}`,
        `[name="${baseName}"]`,
        `[name="id_${baseName}"]`
    ];
    
    console.log(`🔍 Procurando elemento: ${baseName}`);
    
    for (const selector of possibleSelectors) {
        const element = $(selector);
        console.log(`   - Tentando seletor: ${selector} -> ${element.length > 0 ? 'ENCONTRADO' : 'Não encontrado'}`);
        if (element.length > 0) {
            console.log(`✅ Encontrado ${baseName} usando seletor: ${selector}`);
            return { element, selector };
        }
    }
    
    // Se não encontrou, vamos tentar buscar por atributos parciais
    const allElements = $('input, select').filter(function() {
        const id = this.id || '';
        const name = this.name || '';
        return id.includes(baseName) || name.includes(baseName);
    });
    
    if (allElements.length > 0) {
        console.log(`🔍 Elementos similares encontrados para ${baseName}:`);
        allElements.each(function() {
            console.log(`   - ID: "${this.id}", Name: "${this.name}", Tag: ${this.tagName}`);
        });
    }
    
    console.warn(`⚠️ ${baseName} não encontrado com nenhum seletor`);
    return null;
}

// Função para aguardar elementos estarem disponíveis
function waitForElements(retries = 5, delay = 500) {
    console.log(`🔄 Tentativa ${6 - retries} de verificar elementos...`);
    
    const elementos = [
        'uf_notificacao',
        'municipio_notificacao', 
        'uf_residencia',
        'municipio_residencia',
        'uf_transferencia',
        'municipio_transferencia',
        'municipio_ocorrencia',
        'municipio_investigador'
    ];
    
    // Mapear nomes dos elementos para seletores corretos
    const elementoMap = {
        'uf_notificacao': 'id_uf_notificacao',
        'municipio_notificacao': 'id_municipio_notificacao',
        'uf_residencia': 'id_uf_residencia', 
        'municipio_residencia': 'id_municipio_residencia',
        'uf_transferencia': 'id_uf_transferencia',
        'municipio_transferencia': 'id_municipio_transferencia',
        'municipio_ocorrencia': 'id_municipio_ocorrencia',
        'municipio_investigador': 'id_municipio_investigador'
    };
    
    let elementosEncontrados = 0;
    const elementosDisponiveis = {};
    
    elementos.forEach(baseName => {
        // Usar o mapeamento correto para encontrar o elemento
        const realFieldName = elementoMap[baseName] || baseName;
        const result = findElement(realFieldName);
        if (result) {
            elementosEncontrados++;
            elementosDisponiveis[baseName] = result.selector;
        }
    });
    
    console.log(`📊 Elementos encontrados: ${elementosEncontrados}/${elementos.length}`);
    
    if (elementosEncontrados >= 3 || retries <= 0) { // Pelo menos 3 elementos ou esgotou tentativas
        console.log('✅ Prosseguindo com inicialização...');
        try {
            initializeFormulario(elementosDisponiveis);
        } catch (error) {
            console.error('❌ Erro durante inicialização do formulário:', error);
        }
    } else if (retries > 0) {
        console.log(`⏳ Aguardando ${delay}ms antes da próxima tentativa...`);
        setTimeout(() => waitForElements(retries - 1, delay), delay);
    } else {
        console.warn('⚠️ Elementos não encontrados após todas as tentativas. Inicializando mesmo assim...');
        try {
            initializeFormulario({});
        } catch (error) {
            console.error('❌ Erro durante inicialização do formulário:', error);
        }
    }
}

// Função para detectar se estamos editando uma ocorrência existente
function isEditMode() {
    const form = document.getElementById('ocorrencia-form');
    if (form && form.dataset.editMode === 'true') {
        return true;
    }
    const urlPath = window.location.pathname;
    return /\/edit\/?$/.test(urlPath) || /\/\d+\/edit\/?$/.test(urlPath);
}

// Função para verificar campos de data (apenas para debug)
function verificarCamposData() {
    console.log('📅 Verificando campos de data...');
    
    const dateFields = [
        'id_data_notificacao', 'id_data_acidente', 'id_data_cadastro', 'id_data_nascimento',
        'id_data_investigacao', 'id_data_atendimento', 'id_data_transferencia', 'id_data_cadastro_atendimento'
    ];
    
    dateFields.forEach(fieldId => {
        const $field = $(`#${fieldId}`);
        if ($field.length > 0) {
            const currentValue = $field.val();
            console.log(`📅 Campo ${fieldId}: valor atual = "${currentValue}"`);
        }
    });
}

// Funções para navegação entre abas - definidas globalmente
function goToNextTab(nextTabId) {
    console.log('➡️ Navegando para próxima aba:', nextTabId);
    const nextTab = document.getElementById(nextTabId);
    if (nextTab) {
        if (typeof bootstrap !== 'undefined') {
            const nextTabButton = new bootstrap.Tab(nextTab);
            nextTabButton.show();
        } else {
            console.error('❌ Bootstrap não está disponível');
            $(nextTab).tab('show');
        }
        atualizarMunicipiosDaAba(nextTabId);
    }
}

function atualizarMunicipiosDaAba(tabId) {
    if (tabId === 'acidente-tab') {
        MUNICIPIOS_UF_PARA.forEach(carregarMunicipiosPara);
    } else if (tabId === 'transferencia-tab') {
        carregarMunicipiosParaUf(selectByName('id_uf_transferencia'), selectByName('id_municipio_transferencia'), 'Transferência');
    }
}

function goToPreviousTab(previousTabId) {
    console.log('⬅️ Navegando para aba anterior:', previousTabId);
    const previousTab = document.getElementById(previousTabId);
    if (previousTab) {
        if (typeof bootstrap !== 'undefined') {
            const previousTabButton = new bootstrap.Tab(previousTab);
            previousTabButton.show();
        } else {
            console.error('❌ Bootstrap não está disponível');
            // Fallback usando jQuery
            $(previousTab).tab('show');
        }
    }
}

// Expor funções globalmente para debug
console.log('✅ Funções de navegação definidas:', typeof goToNextTab, typeof goToPreviousTab);

// Funções para manipular o formset de partes atingidas
function obterFormsetParteAtingida() {
    const formsetContainer = $('#parte-atingida-formset');
    const totalForms = formsetContainer.find('input[name*="TOTAL_FORMS"]');
    if (!totalForms.length) {
        return null;
    }
    return {
        container: formsetContainer,
        totalForms: totalForms,
        prefix: totalForms.attr('name').replace('-TOTAL_FORMS', ''),
    };
}

function substituirIndiceFormsetParteAtingida($form, formsetPrefix, novoIndice) {
    const idPrefix = 'id_' + formsetPrefix.replace(/-/g, '_');
    $form.find('input, select').each(function() {
        const name = $(this).attr('name');
        const id = $(this).attr('id');

        if (name) {
            const newName = name
                .replace(/__prefix__/g, String(novoIndice))
                .replace(new RegExp(formsetPrefix + '-\\d+-', 'g'), formsetPrefix + '-' + novoIndice + '-');
            $(this).attr('name', newName);
        }
        if (id) {
            const newId = id
                .replace(/__prefix__/g, String(novoIndice))
                .replace(new RegExp(idPrefix + '-\\d+-', 'g'), idPrefix + '-' + novoIndice + '-');
            $(this).attr('id', newId);
        }
    });
    $form.attr('data-form-index', novoIndice);
}

function linhasParteAtingidaNoFormset(formsetContainer) {
    return formsetContainer
        .find('.parte-atingida-form')
        .not('.parte-atingida-form--template');
}

function linhasParteAtingidaAtivas(formsetContainer) {
    return linhasParteAtingidaNoFormset(formsetContainer).filter(function() {
        const $row = $(this);
        if ($row.css('display') === 'none') {
            return false;
        }
        return !$row.find('input[name$="-DELETE"]').prop('checked');
    });
}

function reindexarFormsetParteAtingida() {
    const ctx = obterFormsetParteAtingida();
    if (!ctx) {
        return;
    }

    const linhas = linhasParteAtingidaNoFormset(ctx.container);
    linhas.each(function(index) {
        substituirIndiceFormsetParteAtingida($(this), ctx.prefix, index);
    });
    ctx.totalForms.val(linhas.length);
}

function obterTemplateParteAtingida(formsetContainer) {
    let template = linhasParteAtingidaAtivas(formsetContainer).first();
    if (template.length) {
        return template;
    }
    return $('#parte-atingida-empty-form-template .parte-atingida-form').first();
}

function addParteAtingidaForm() {
    const ctx = obterFormsetParteAtingida();
    if (!ctx) {
        console.error('Formset de partes atingidas não encontrado.');
        return;
    }

    const formCount = parseInt(ctx.totalForms.val(), 10) || 0;
    const template = obterTemplateParteAtingida(ctx.container);
    if (!template.length) {
        console.error('Nenhum modelo de linha para partes atingidas.');
        return;
    }

    const newForm = template.clone(true);
    newForm.removeClass('parte-atingida-form--template');
    newForm.find('.text-danger').remove();

    substituirIndiceFormsetParteAtingida(newForm, ctx.prefix, formCount);

    newForm.find('input[name$="-id"]').val('');
    newForm.find('input[name$="-pk"]').val('');
    newForm.find('input[name$="-DELETE"]').prop('checked', false);

    newForm.find('select').val('');

    newForm.find('.btn-remover-parte').off('click').on('click', function() {
        removeParteAtingidaForm(this);
    });

    ctx.container.append(newForm);
    ctx.totalForms.val(formCount + 1);

    newForm.find('select').trigger('focus');
}

function removeParteAtingidaForm(button) {
    const ctx = obterFormsetParteAtingida();
    if (!ctx) {
        return;
    }

    const formContainer = $(button).closest('.parte-atingida-form');
    const formId = formContainer.find('input[name$="-id"]').val();

    if (formId) {
        formContainer.find('input[name$="-DELETE"]').prop('checked', true);
        formContainer.hide();
    } else {
        formContainer.remove();
    }

    reindexarFormsetParteAtingida();
}

window.addParteAtingidaForm = addParteAtingidaForm;
window.removeParteAtingidaForm = removeParteAtingidaForm;

// Recarrega municípios ao exibir abas que usam selects dependentes
function configurarRecargaMunicipiosNasAbas() {
    const tabHandlers = [
        {
            tabId: 'acidente-tab',
            init: function() {
                MUNICIPIOS_UF_PARA.forEach(carregarMunicipiosPara);
            }
        },
        {
            tabId: 'transferencia-tab',
            init: function() {
                carregarMunicipiosParaUf(selectByName('id_uf_transferencia'), selectByName('id_municipio_transferencia'), 'Transferência');
            }
        }
    ];

    tabHandlers.forEach(function(handler) {
        const tab = document.getElementById(handler.tabId);
        if (tab) {
            tab.addEventListener('shown.bs.tab', handler.init);
        }
    });
}

// Inicialização quando o documento estiver pronto
$(document).ready(function() {
    console.log('📄 DOM ready - aguardando elementos...');
    console.log(`🔍 Modo: ${isEditMode() ? 'EDIÇÃO' : 'CRIAÇÃO'}`);
    
    verificarCamposData();
    configurarIdadePaciente();
    configurarTempoGestacaoPorSexo();
    configurarValidacaoCpfCns();
    configurarBuscaCep();
    configurarMascaraTelefones();
    configurarRecargaMunicipiosNasAbas();
    
    setTimeout(() => {
        waitForElements();
        setTimeout(verificarCamposData, 500);
    }, 200);
});

// Select2 após página e CSS totalmente carregados (evita falha no campo UF)
$(window).on('load', function() {
    initSelect2UfNotificacao();
    initSelect2CnesFields();
    initSelect2CboFields();
    initSelect2CidFields();
    setTimeout(function() {
        initSelect2UfNotificacao();
        initSelect2CnesFields();
        initSelect2CboFields();
        initSelect2CidFields();
    }, 400);
});
