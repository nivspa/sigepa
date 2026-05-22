#!/usr/bin/env python
"""
Gera PDF com o relatório das melhorias na ficha de ocorrência (SIGEPA).
Linguagem simples — para documentação e apresentação.
Uso: python scripts/gerar_relatorio_melhorias_ficha_pdf.py
"""
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT = BASE_DIR / "docs" / "Relatorio_Melhorias_Ficha_Ocorrencia_SIGEPA.pdf"

AZUL_ESCURO = colors.HexColor("#1e3a5f")
AZUL = colors.HexColor("#3b82f6")
AZUL_CLARO = colors.HexColor("#eff6ff")
CINZA = colors.HexColor("#6b7280")
CINZA_BORDA = colors.HexColor("#e5e7eb")
VERDE = colors.HexColor("#059669")


def estilos():
    base = getSampleStyleSheet()
    return {
        "titulo_capa": ParagraphStyle(
            "titulo_capa",
            parent=base["Title"],
            fontSize=26,
            leading=32,
            textColor=AZUL_ESCURO,
            alignment=TA_CENTER,
            spaceAfter=12,
            fontName="Helvetica-Bold",
        ),
        "subtitulo_capa": ParagraphStyle(
            "subtitulo_capa",
            parent=base["Normal"],
            fontSize=13,
            leading=18,
            textColor=CINZA,
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "h1": ParagraphStyle(
            "h1",
            parent=base["Heading1"],
            fontSize=15,
            leading=19,
            textColor=AZUL_ESCURO,
            spaceBefore=16,
            spaceAfter=8,
            fontName="Helvetica-Bold",
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontSize=11,
            leading=14,
            textColor=AZUL,
            spaceBefore=10,
            spaceAfter=5,
            fontName="Helvetica-Bold",
        ),
        "corpo": ParagraphStyle(
            "corpo",
            parent=base["Normal"],
            fontSize=10.5,
            leading=15,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            parent=base["Normal"],
            fontSize=10.5,
            leading=14,
            leftIndent=12,
            spaceAfter=5,
        ),
        "destaque": ParagraphStyle(
            "destaque",
            parent=base["Normal"],
            fontSize=10,
            leading=14,
            backColor=AZUL_CLARO,
            borderPadding=8,
            spaceAfter=10,
            alignment=TA_JUSTIFY,
        ),
        "meta": ParagraphStyle(
            "meta",
            parent=base["Normal"],
            fontSize=9,
            textColor=CINZA,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
    }


def caixa_destaque(texto, s):
    return [
        Spacer(1, 4),
        Paragraph(texto, s["destaque"]),
        Spacer(1, 4),
    ]


def secao(story, s, titulo, intro, itens, antes_depois=None):
    story.append(Paragraph(titulo, s["h1"]))
    if intro:
        story.append(Paragraph(intro, s["corpo"]))
    for item in itens:
        story.append(Paragraph(f"• {item}", s["bullet"]))
    if antes_depois:
        story.append(Spacer(1, 6))
        story.append(Paragraph("Antes", s["h2"]))
        story.append(Paragraph(antes_depois[0], s["corpo"]))
        story.append(Paragraph("Agora", s["h2"]))
        story.append(Paragraph(antes_depois[1], s["corpo"]))
    story.append(Spacer(1, 8))


def capa(story, s):
    story.append(Spacer(1, 2.8 * cm))
    story.append(HRFlowable(width="100%", thickness=4, color=AZUL, spaceAfter=22))
    story.append(Paragraph("SIGEPA", s["titulo_capa"]))
    story.append(
        Paragraph(
            "Sistema de Gestão de Casos de Escalpelamento",
            s["subtitulo_capa"],
        )
    )
    story.append(Spacer(1, 1 * cm))
    story.append(
        Paragraph(
            "O que melhoramos na ficha de ocorrência",
            ParagraphStyle(
                "titulo_rel",
                parent=s["titulo_capa"],
                fontSize=19,
                textColor=AZUL,
            ),
        )
    )
    story.append(Spacer(1, 0.6 * cm))
    story.append(
        Paragraph(
            "Resumo para documentação — linguagem simples",
            s["subtitulo_capa"],
        )
    )
    story.append(
        Paragraph(
            date.today().strftime("%d/%m/%Y"),
            s["subtitulo_capa"],
        )
    )
    story.append(Spacer(1, 1.8 * cm))
    story.extend(
        caixa_destaque(
            "<b>Para que serve este documento?</b><br/>"
            "Registrar, de forma clara, as melhorias feitas no SIGEPA — ficha de "
            "ocorrência e segurança do acesso — o que mudou para quem usa o sistema "
            "no dia a dia, sem termos técnicos.",
            s,
        )
    )
    story.append(PageBreak())


def conteudo(story, s):
    story.append(Paragraph("Resumo em uma frase", s["h1"]))
    story.append(
        Paragraph(
            "A ficha de ocorrência ficou mais fácil de preencher, com menos erro de "
            "digitação, buscas mais rápidas e campos que se completam sozinhos quando "
            "faz sentido (CEP, idade, endereço etc.). Além disso, o cadastro público "
            "de usuários foi fechado: só quem o administrador liberar consegue entrar.",
            s["corpo"],
        )
    )
    story.extend(
        caixa_destaque(
            "<b>Abas da ficha:</b> Notificação → Paciente → Endereço → Acidente → "
            "Transferência → Investigação → Evolução",
            s,
        )
    )

    secao(
        story,
        s,
        "1. Buscar município e estado ficou mais fácil",
        "Em vários campos da ficha é preciso escolher estado (UF) e município.",
        [
            "Dá para digitar e buscar o nome do município na lista.",
            "Municípios do Pará já aparecem prontos nos campos principais.",
            "Ao mudar o estado, a lista de municípios atualiza sozinha.",
        ],
        (
            "Lista longa, difícil de achar o município.",
            "Busca por nome, igual em um campo de pesquisa moderno.",
        ),
    )

    secao(
        story,
        s,
        "2. CNES, profissão (CBO) e diagnóstico (CID)",
        "Campos usados no atendimento e na investigação.",
        [
            "Basta digitar 3 letras ou números para aparecerem opções.",
            "A lupa (ícone de pesquisa) continua disponível para quem preferir abrir a lista completa.",
        ],
        (
            "Só dava para escolher rolando uma lista enorme.",
            "Digita um pedaço do nome ou código e o sistema filtra na hora.",
        ),
    )

    secao(
        story,
        s,
        "3. Datas com botões + e −",
        "Todos os campos de data ganharam setinhas ao lado.",
        [
            "Botão <b>+</b>: avança um dia (se o campo estiver vazio, coloca a data de hoje).",
            "Botão <b>−</b>: volta um dia.",
            "Não deixa colocar data no futuro.",
        ],
        (
            "Só digitando manualmente no teclado.",
            "Um clique para ajustar o dia, útil em atendimento rápido.",
        ),
    )

    secao(
        story,
        s,
        "4. Abas do formulário mais legíveis",
        None,
        [
            "Texto das abas que não estão selecionadas passou a aparecer em cinza escuro.",
            "Ficou fácil ver em qual aba você está e quais ainda faltam preencher.",
        ],
        (
            "Abas inativas quase sumiam (texto branco no fundo claro).",
            "Todas as abas ficaram legíveis.",
        ),
    )

    secao(
        story,
        s,
        "5. Idade calculada sozinha",
        "Na aba Paciente.",
        [
            "Ao informar a data de nascimento, a idade é preenchida automaticamente.",
            "O campo idade trava para não digitar um número diferente por engano.",
            "Se não houver data de nascimento, a idade pode ser informada manualmente.",
            "Idade acima de 120 anos não é aceita.",
        ],
    )

    secao(
        story,
        s,
        "6. Tempo de gestação só quando faz sentido",
        None,
        [
            "O campo só aparece quando o sexo informado é feminino.",
            "Para masculino ou ignorado, o sistema grava “Não se aplica” sozinho.",
            "Evita preenchimento desnecessário e erro de formulário.",
        ],
    )

    secao(
        story,
        s,
        "7. CPF e Cartão SUS (CNS) com conferência",
        None,
        [
            "Formatação automática enquanto digita (pontos e traços no CPF, espaços no CNS).",
            "Ao sair do campo, o sistema avisa se o número parece inválido.",
            "Reduz cadastros com documento digitado errado.",
        ],
    )

    story.append(Paragraph("8. CEP preenche o endereço", s["h1"]))
    story.append(
        Paragraph(
            "Na aba <b>Endereço</b>, o CEP foi para o começo da seção — é o primeiro "
            "campo que a pessoa deve informar.",
            s["corpo"],
        )
    )
    for item in [
        "Digite o CEP (com ou sem traço): o sistema busca na base dos Correios.",
        "Preenche rua, bairro, estado e município quando existirem.",
        "CEP de cidade inteira (sem rua): limpa rua e bairro antigos e deixa só cidade/UF.",
        "Depois do CEP, o cursor vai para o campo <b>Número</b> da casa.",
        "Aparece um ícone de carregamento enquanto busca.",
    ]:
        story.append(Paragraph(f"• {item}", s["bullet"]))
    story.append(Spacer(1, 6))
    story.extend(
        caixa_destaque(
            "<b>Exemplo para testar:</b> 66010-000 (Belém, com rua) e depois 68440-000 "
            "(Abaetetuba, só cidade).",
            s,
        )
    )

    secao(
        story,
        s,
        "9. Telefone com máscara",
        None,
        [
            "Telefone do paciente, do dono do veículo e do condutor.",
            "Formata sozinho: (91) 98765-4321 para celular ou (91) 3212-3456 para fixo.",
        ],
    )

    secao(
        story,
        s,
        "10. Partes do corpo atingidas",
        "Na aba Acidente, seção “Partes Atingidas”.",
        [
            "Sempre aparece pelo menos uma linha para escolher a parte do corpo.",
            "Botão “Adicionar Parte Atingida” passou a funcionar de verdade.",
            "Cada linha: lista para escolher + botão de lixeira para remover.",
            "Visual organizado, sem caixinhas estranhas embaixo dos campos.",
        ],
        (
            "Em ficha nova o botão de adicionar não fazia nada; layout confuso.",
            "Dá para incluir várias partes (ex.: supercílio, região occipital) e salvar normalmente.",
        ),
    )

    secao(
        story,
        s,
        "11. Login mais seguro — sem cadastro aberto",
        "Na tela de entrada do sistema (login).",
        [
            "Removido o link “Registre-se” — qualquer pessoa não pode mais criar conta sozinha.",
            "Removido o botão “Registrar” do menu para visitantes.",
            "Quem tentar abrir a página de cadastro antiga é levado de volta ao login, com aviso.",
            "Novos usuários só entram se forem cadastrados no painel administrativo (/admin/).",
            "Na tela de login aparece: “Solicite seu cadastro ao administrador do SIGEPA”.",
        ],
        (
            "Qualquer pessoa podia se registrar pela internet e ganhar acesso ao sistema.",
            "Só usuários criados pelo administrador conseguem fazer login — mais controle e segurança.",
        ),
    )
    story.extend(
        caixa_destaque(
            "<b>Quem cadastra usuários?</b> Equipe com acesso ao painel admin do Django "
            "(mesmo lugar onde se gerencia o sistema). Não é mais pela tela “Crie sua conta”.",
            s,
        )
    )

    story.append(PageBreak())
    story.append(Paragraph("Lista rápida — o que conferir ao testar", s["h1"]))
    story.append(
        Paragraph(
            "Sugestão para quem for documentar ou validar as mudanças:",
            s["corpo"],
        )
    )

    testes = [
        ("CEP", "Digitar 66010-000 e ver se preenche endereço em Belém."),
        ("CEP só cidade", "Digitar 68440-000 depois de um CEP com rua — rua deve limpar."),
        ("CPF errado", "Digitar CPF inválido e ver mensagem ao sair do campo."),
        ("Idade", "Colocar data de nascimento e ver idade aparecer sozinha."),
        ("Gestação", "Mudar sexo e ver campo sumir ou aparecer."),
        ("Partes atingidas", "Clicar em adicionar e incluir mais de uma parte."),
        ("Telefone", "Digitar só números e ver parênteses e traço."),
        ("Datas", "Usar + e − nos campos de data."),
        ("Login", "Confirmar que não existe mais link “Registre-se”."),
        ("Cadastro bloqueado", "Abrir /usuarios/register/ — deve voltar ao login com mensagem."),
        ("Novo usuário", "Criar conta só pelo painel /admin/ e testar login."),
    ]

    dados = [["O quê testar", "O que deve acontecer"]] + testes
    t = Table(dados, colWidths=[3.8 * cm, 12.7 * cm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), AZUL_ESCURO),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, CINZA_BORDA),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, AZUL_CLARO]),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 20))

    story.append(Paragraph("Observações finais", s["h1"]))
    story.append(
        Paragraph(
            "As melhorias da ficha valem para <b>nova ocorrência</b> e <b>edição</b>. "
            "A mudança do login vale para todos que acessam o SIGEPA. Após atualizar no "
            "servidor, pedir <b>Ctrl + F5</b> no navegador para carregar a tela nova.",
            s["corpo"],
        )
    )
    story.append(Spacer(1, 12))
    story.append(
        Paragraph(
            "<font color='#059669'><b>✓</b></font> "
            "Documento preparado para apoio à documentação institucional do SIGEPA.",
            s["meta"],
        )
    )


def rodape(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(CINZA)
    canvas.drawString(2 * cm, 1.2 * cm, "SIGEPA — Melhorias na ficha de ocorrência")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Página {doc.page}")
    canvas.restoreState()


def gerar():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2.2 * cm,
        title="Melhorias na Ficha de Ocorrência — SIGEPA",
    )
    s = estilos()
    story = []
    capa(story, s)
    conteudo(story, s)
    doc.build(story, onFirstPage=rodape, onLaterPages=rodape)
    print(f"PDF gerado: {OUTPUT}")


if __name__ == "__main__":
    gerar()
