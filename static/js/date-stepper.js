// SIGEPA-STATIC-VERSION: 2026-05-22-ficha-v2
/**
 * Campos de data com botões − / +:
 * - vazio + "+" → data de hoje
 * - "+" desabilitado quando a data já é hoje (sem datas futuras)
 * - "−" diminui um dia (se houver valor)
 */
(function() {
    'use strict';

    function hojeISO() {
        const doServidor = document.documentElement.getAttribute('data-sigepa-hoje');
        if (doServidor) {
            return doServidor;
        }
        return formatarISO(new Date());
    }

    function formatarISO(data) {
        const y = data.getFullYear();
        const m = String(data.getMonth() + 1).padStart(2, '0');
        const day = String(data.getDate()).padStart(2, '0');
        return y + '-' + m + '-' + day;
    }

    function parseISO(str) {
        if (!str) {
            return null;
        }
        const partes = str.split('-').map(Number);
        if (partes.length !== 3 || partes.some(isNaN)) {
            return null;
        }
        return new Date(partes[0], partes[1] - 1, partes[2]);
    }

    function somarDias(iso, dias) {
        const data = parseISO(iso);
        if (!data) {
            return null;
        }
        data.setDate(data.getDate() + dias);
        return formatarISO(data);
    }

    function atualizarBotaoMais(input, btnMais) {
        const hoje = hojeISO();
        const valor = input.value;
        btnMais.disabled = Boolean(valor && valor >= hoje);
    }

    function garantirMaxHoje(input) {
        const hoje = hojeISO();
        if (!input.max || input.max > hoje) {
            input.max = hoje;
        }
    }

    function envolverCampoData(input) {
        if (input.dataset.dateStepperInit === '1') {
            return;
        }
        input.dataset.dateStepperInit = '1';
        garantirMaxHoje(input);

        const grupo = document.createElement('div');
        grupo.className = 'input-group date-stepper-group';

        const btnMenos = document.createElement('button');
        btnMenos.type = 'button';
        btnMenos.className = 'btn btn-outline-secondary date-stepper-btn';
        btnMenos.setAttribute('aria-label', 'Diminuir um dia');
        btnMenos.setAttribute('title', 'Diminuir um dia');
        btnMenos.textContent = '−';

        const btnMais = document.createElement('button');
        btnMais.type = 'button';
        btnMais.className = 'btn btn-outline-secondary date-stepper-btn';
        btnMais.setAttribute('aria-label', 'Aumentar um dia');
        btnMais.setAttribute('title', 'Aumentar um dia');
        btnMais.textContent = '+';

        const pai = input.parentNode;
        pai.insertBefore(grupo, input);
        grupo.appendChild(btnMenos);
        grupo.appendChild(input);
        grupo.appendChild(btnMais);

        input.classList.add('date-stepper-input');

        btnMenos.addEventListener('click', function() {
            if (!input.value) {
                return;
            }
            const nova = somarDias(input.value, -1);
            if (nova) {
                input.value = nova;
                input.dispatchEvent(new Event('change', { bubbles: true }));
            }
            atualizarBotaoMais(input, btnMais);
        });

        btnMais.addEventListener('click', function() {
            const hoje = hojeISO();
            if (!input.value) {
                input.value = hoje;
            } else {
                const nova = somarDias(input.value, 1);
                if (nova && nova <= hoje) {
                    input.value = nova;
                }
            }
            input.dispatchEvent(new Event('change', { bubbles: true }));
            atualizarBotaoMais(input, btnMais);
        });

        input.addEventListener('change', function() {
            if (input.value && input.value > hojeISO()) {
                input.value = hojeISO();
            }
            garantirMaxHoje(input);
            atualizarBotaoMais(input, btnMais);
        });

        input.addEventListener('input', function() {
            atualizarBotaoMais(input, btnMais);
        });

        atualizarBotaoMais(input, btnMais);
    }

    function initDateSteppers(root) {
        const escopo = root && root.querySelectorAll ? root : document;
        escopo.querySelectorAll('input[type="date"]:not([data-date-stepper-init="1"])').forEach(envolverCampoData);
    }

    window.initDateSteppers = initDateSteppers;

    document.addEventListener('DOMContentLoaded', function() {
        initDateSteppers();
    });

    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType !== 1) {
                    return;
                }
                if (node.matches && node.matches('input[type="date"]')) {
                    envolverCampoData(node);
                }
                initDateSteppers(node);
            });
        });
    });

    observer.observe(document.body, { childList: true, subtree: true });
})();
