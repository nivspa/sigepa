# -*- coding: utf-8 -*-
"""Gera o relatório SIGEPA completo (8 páginas) com formatação uniforme."""
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[1]
OUT_PDF = ROOT / "docs" / "Relatorio_Melhorias_Ficha_Ocorrencia_SIGEPA.pdf"
FONT = "Arial"
FONT_DIR = Path(r"C:\Windows\Fonts")
HEADER = "SIGEPA — Melhorias do sistema"


class Relatorio(FPDF):
    def __init__(self):
        super().__init__()
        self.set_margins(22, 18, 22)
        self.set_auto_page_break(auto=True, margin=20)
        self.add_font(FONT, "", str(FONT_DIR / "arial.ttf"))
        self.add_font(FONT, "B", str(FONT_DIR / "arialbd.ttf"))

    @property
    def content_w(self) -> float:
        return self.w - self.l_margin - self.r_margin

    def header(self):
        self.set_font(FONT, size=9)
        self.set_text_color(90, 90, 90)
        self.cell(self.content_w / 2, 7, HEADER, align="L")
        self.cell(self.content_w / 2, 7, f"Página {self.page_no()}", align="R", new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def h1(self, text: str):
        self.set_font(FONT, "B", 16)
        self.set_text_color(0, 0, 0)
        self.multi_cell(self.content_w, 9, text)
        self.ln(3)

    def h2(self, text: str):
        self.set_font(FONT, "B", 12)
        self.multi_cell(self.content_w, 7, text)
        self.ln(2)

    def p(self, text: str, size: int = 11):
        self.set_font(FONT, size=size)
        self.multi_cell(self.content_w, 6, text)
        self.ln(2)

    def bullet(self, text: str):
        self.set_font(FONT, size=11)
        self.multi_cell(self.content_w, 6, f"  •  {text}")

    def item(self, num: str, title: str):
        self.set_font(FONT, "B", 12)
        self.multi_cell(self.content_w, 7, f"{num}. {title}")
        self.ln(1)

    def antes_agora(self, antes: str, agora: str):
        self.set_font(FONT, "B", 11)
        self.cell(self.content_w, 6, "Antes", new_x="LMARGIN", new_y="NEXT")
        self.set_font(FONT, size=11)
        self.multi_cell(self.content_w, 6, antes)
        self.ln(2)
        self.set_font(FONT, "B", 11)
        self.cell(self.content_w, 6, "Agora", new_x="LMARGIN", new_y="NEXT")
        self.set_font(FONT, size=11)
        self.multi_cell(self.content_w, 6, agora)
        self.ln(3)

    def table_row(self, col1: str, col2: str, header: bool = False):
        self.set_font(FONT, "B" if header else "", 10)
        x0 = self.l_margin
        y0 = self.get_y()
        w1 = 48
        w2 = self.content_w - w1
        self.set_xy(x0 + w1, y0)
        self.multi_cell(w2, 6, col2, border=1)
        row_h = self.get_y() - y0
        self.set_xy(x0, y0)
        self.cell(w1, row_h, col1, border=1)
        self.set_xy(x0, y0 + row_h)


def build() -> None:
    pdf = Relatorio()

    # --- Página 1 ---
    pdf.add_page()
    pdf.h1("SIGEPA")
    pdf.p("Sistema de Gestão de Casos de Escalpelamento", size=12)
    pdf.ln(2)
    pdf.h2("O que melhoramos no sistema")
    pdf.p("Resumo para documentação — linguagem simples")
    pdf.p("22/05/2026")
    pdf.ln(4)
    pdf.h2("Para que serve este documento?")
    pdf.p(
        "Registrar, de forma clara, as melhorias feitas no SIGEPA — ficha de ocorrência, "
        "segurança do acesso e atualização em produção — e o que mudou para quem usa o "
        "sistema no dia a dia, sem termos técnicos."
    )

    # --- Página 2 ---
    pdf.add_page()
    pdf.h2("Resumo em uma frase")
    pdf.p(
        "A ficha de ocorrência ficou mais fácil de preencher, com menos erro de digitação, "
        "buscas mais rápidas e campos que se completam sozinhos quando faz sentido (CEP, "
        "idade, endereço etc.). Além disso, o cadastro público de usuários foi fechado: "
        "só quem o administrador liberar consegue entrar. Depois de aprovada, cada melhoria "
        "passa a ir para produção sozinha, em poucos minutos."
    )
    pdf.p(
        "Abas da ficha: Notificação → Paciente → Endereço → Acidente → Transferência → "
        "Investigação → Evolução"
    )

    # --- Página 3 ---
    pdf.add_page()
    pdf.item("1", "Buscar município e estado ficou mais fácil")
    pdf.p("Em vários campos da ficha é preciso escolher estado (UF) e município.")
    pdf.bullet("Dá para digitar e buscar o nome do município na lista.")
    pdf.bullet("Municípios do Pará já aparecem prontos nos campos principais.")
    pdf.bullet("Ao mudar o estado, a lista de municípios atualiza sozinha.")
    pdf.antes_agora(
        "Lista longa, difícil de achar o município.",
        "Busca por nome, igual em um campo de pesquisa moderno.",
    )

    pdf.item("2", "CNES, profissão (CBO) e diagnóstico (CID)")
    pdf.p("Campos usados no atendimento e na investigação.")
    pdf.bullet("Basta digitar 3 letras ou números para aparecerem opções.")
    pdf.bullet("A lupa (ícone de pesquisa) continua disponível para quem preferir abrir a lista completa.")
    pdf.antes_agora(
        "Só dava para escolher rolando uma lista enorme.",
        "Digita um pedaço do nome ou código e o sistema filtra na hora.",
    )

    pdf.item("3", "Datas com botões + e −")
    pdf.bullet("Botão +: avança um dia (se o campo estiver vazio, coloca a data de hoje).")
    pdf.bullet("Botão −: volta um dia.")
    pdf.bullet("Não deixa colocar data no futuro.")
    pdf.antes_agora(
        "Só digitando manualmente no teclado.",
        "Um clique para ajustar o dia, útil em atendimento rápido.",
    )

    # --- Página 4 ---
    pdf.add_page()
    pdf.item("4", "Abas do formulário mais legíveis")
    pdf.bullet("Texto das abas que não estão selecionadas passou a aparecer em cinza escuro.")
    pdf.bullet("Ficou fácil ver em qual aba você está e quais ainda faltam preencher.")
    pdf.antes_agora(
        "Abas inativas quase sumiam (texto branco no fundo claro).",
        "Todas as abas ficaram legíveis.",
    )

    pdf.item("5", "Idade calculada sozinha")
    pdf.p("Na aba Paciente.")
    pdf.bullet("Ao informar a data de nascimento, a idade é preenchida automaticamente.")
    pdf.bullet("O campo idade trava para não digitar um número diferente por engano.")
    pdf.bullet("Se não houver data de nascimento, a idade pode ser informada manualmente.")
    pdf.bullet("Idade acima de 120 anos não é aceita.")

    pdf.item("6", "Tempo de gestação só quando faz sentido")
    pdf.bullet("O campo só aparece quando o sexo informado é feminino.")
    pdf.bullet('Para masculino ou ignorado, o sistema grava "Não se aplica" sozinho.')
    pdf.bullet("Evita preenchimento desnecessário e erro de formulário.")

    pdf.item("7", "CPF e Cartão SUS (CNS) com conferência")
    pdf.bullet("Formatação automática enquanto digita (pontos e traços no CPF, espaços no CNS).")
    pdf.bullet("Ao sair do campo, o sistema avisa se o número parece inválido.")
    pdf.bullet("Reduz cadastros com documento digitado errado.")

    # --- Página 5 ---
    pdf.add_page()
    pdf.item("8", "CEP preenche o endereço")
    pdf.p(
        "Na aba Endereço, o CEP foi para o começo da seção — é o primeiro campo que a "
        "pessoa deve informar."
    )
    pdf.bullet("Digite o CEP (com ou sem traço): o sistema busca na base dos Correios.")
    pdf.bullet("Preenche rua, bairro, estado e município quando existirem.")
    pdf.bullet("CEP de cidade inteira (sem rua): limpa rua e bairro antigos e deixa só cidade/UF.")
    pdf.bullet("Depois do CEP, o cursor vai para o campo Número da casa.")
    pdf.bullet("Aparece um ícone de carregamento enquanto busca.")
    pdf.p("Exemplo para testar: 66010-000 (Belém, com rua) e depois 68440-000 (Abaetetuba, só cidade).")

    pdf.item("9", "Telefone com máscara")
    pdf.bullet("Telefone do paciente, do dono do veículo e do condutor.")
    pdf.bullet("Formata sozinho: (91) 98765-4321 para celular ou (91) 3212-3456 para fixo.")

    pdf.item("10", "Partes do corpo atingidas")
    pdf.p('Na aba Acidente, seção "Partes Atingidas".')
    pdf.bullet("Sempre aparece pelo menos uma linha para escolher a parte do corpo.")
    pdf.bullet('Botão "Adicionar Parte Atingida" passou a funcionar de verdade.')
    pdf.bullet("Cada linha: lista para escolher + botão de lixeira para remover.")
    pdf.bullet("Visual organizado, sem caixinhas estranhas embaixo dos campos.")
    pdf.antes_agora(
        "Em ficha nova o botão de adicionar não fazia nada; layout confuso.",
        "Dá para incluir várias partes (ex.: supercílio, região occipital) e salvar normalmente.",
    )

    # --- Página 6 ---
    pdf.add_page()
    pdf.item("11", "Login mais seguro — sem cadastro aberto")
    pdf.p("Na tela de entrada do sistema (login).")
    pdf.bullet('Removido o link "Registre-se" — qualquer pessoa não pode mais criar conta sozinha.')
    pdf.bullet('Removido o botão "Registrar" do menu para visitantes.')
    pdf.bullet("Quem tentar abrir a página de cadastro antiga é levado de volta ao login, com aviso.")
    pdf.bullet("Novos usuários só entram se forem cadastrados no painel administrativo (/admin/).")
    pdf.bullet('Na tela de login aparece: "Solicite seu cadastro ao administrador do SIGEPA".')
    pdf.antes_agora(
        "Qualquer pessoa podia se registrar pela internet e ganhar acesso ao sistema.",
        "Só usuários criados pelo administrador conseguem fazer login — mais controle e segurança.",
    )
    pdf.p(
        "Quem cadastra usuários? Equipe com acesso ao painel admin do Django (mesmo lugar onde se "
        "gerencia o sistema). Não é mais pela tela \"Crie sua conta\"."
    )

    pdf.ln(2)
    pdf.h2("Lista rápida — o que conferir ao testar")
    pdf.p("Sugestão para quem for documentar ou validar as mudanças:")
    pdf.table_row("O quê testar", "O que deve acontecer", header=True)
    rows = [
        ("CEP", "Digitar 66010-000 e ver se preenche endereço em Belém."),
        ("CEP só cidade", "Digitar 68440-000 depois de um CEP com rua — rua deve limpar."),
        ("CPF errado", "Digitar CPF inválido e ver mensagem ao sair do campo."),
        ("Idade", "Colocar data de nascimento e ver idade aparecer sozinha."),
        ("Gestação", "Mudar sexo e ver campo sumir ou aparecer."),
        ("Partes atingidas", "Clicar em adicionar e incluir mais de uma parte."),
        ("Telefone", "Digitar só números e ver parênteses e traço."),
        ("Datas", "Usar + e − nos campos de data."),
        ("Login", 'Confirmar que não existe mais link "Registre-se".'),
        ("Cadastro bloqueado", "Abrir /usuarios/register/ — deve voltar ao login com mensagem."),
        ("Novo usuário", "Criar conta só pelo painel /admin/ e testar login."),
    ]
    for c1, c2 in rows:
        pdf.table_row(c1, c2)

    # --- Página 7 ---
    pdf.add_page()
    pdf.item("12", "Atualização em produção ficou automática")
    pdf.p(
        "Depois que uma melhoria no sistema é aprovada e enviada para o repositório oficial, "
        "o ambiente de produção passa a receber a versão nova sozinha, em poucos minutos — "
        "sem precisar copiar arquivos na mão nem entrar no servidor a cada correção."
    )

    pdf.h2("Como funciona, em linguagem simples")
    pdf.bullet("O desenvolvedor envia a alteração para a versão principal do projeto.")
    pdf.bullet(
        "Um processo na nuvem (GitHub) monta a nova versão do SIGEPA e publica o pacote "
        "atualizado, no mesmo estilo de outros sistemas da área."
    )
    pdf.bullet(
        "No ambiente de produção (Portainer), o serviço Shepherd verifica, a cada 5 minutos, "
        "se existe versão nova."
    )
    pdf.bullet("Quando encontra, reinicia o SIGEPA já com a versão atualizada.")

    pdf.antes_agora(
        "Cada mudança exigia publicar a versão e, em seguida, alguém abrir o Portainer, "
        "localizar o serviço do SIGEPA e clicar em atualizar manualmente. Era fácil esquecer ou demorar.",
        "O fluxo de rotina é: enviar a melhoria → aguardar o processo na nuvem (cerca de 2 minutos) "
        "→ em até 5 minutos o Shepherd aplica em produção. Quem testa só precisa atualizar a página "
        "no navegador (Ctrl + F5).",
    )

    pdf.h2("O que isso não muda")
    pdf.bullet("Cadastro de usuários continua só pelo administrador (item 11 deste relatório).")
    pdf.bullet("Os dados das fichas no banco não são apagados — só o programa (telas e regras) é trocado.")
    pdf.bullet("Senhas e configurações sensíveis continuam somente no Portainer, não no GitHub.")

    # --- Página 8 ---
    pdf.add_page()
    pdf.h2("Como saber se deu certo")
    pdf.p("(Para quem for testar ou documentar.)")
    pdf.bullet("Na nuvem (GitHub → Actions), o passo de build aparece com sucesso (verde).")
    pdf.bullet('Nos registros do Shepherd no Portainer: "Service sigepa_sigepa was updated!".')
    pdf.bullet("A data de última atualização do serviço SIGEPA no Portainer fica recente.")
    pdf.bullet("A melhoria aparece no site em produção após Ctrl + F5 no navegador.")

    pdf.ln(2)
    pdf.h2("Lista rápida — incluir ao testar")
    pdf.table_row("O quê testar", "O que deve acontecer", header=True)
    pdf.table_row(
        "Deploy automático",
        "Após envio aprovado, em até cerca de 5 min a versão nova em produção (Ctrl + F5).",
    )

    pdf.ln(3)
    pdf.h2("Observações finais")
    pdf.p(
        "As melhorias da ficha valem para nova ocorrência e edição. A mudança do login vale para "
        "todos que acessam o SIGEPA. A atualização em produção (item 12) vale para todas as melhorias "
        "enviadas ao repositório oficial. Após atualizar no servidor, pedir Ctrl + F5 no navegador "
        "para carregar a tela nova."
    )
    pdf.ln(2)
    pdf.p(
        "Este fluxo segue a mesma ideia do backend Saúde Pará: a nuvem prepara a versão; o ambiente "
        "interno da Secretaria aplica em produção. O SIGEPA usa o Shepherd dentro da rede para aplicar "
        "sozinho, sem o desenvolvedor precisar de acesso remoto ao servidor.",
        size=10,
    )
    pdf.ln(4)
    pdf.set_font(FONT, size=9)
    pdf.set_text_color(110, 110, 110)
    pdf.multi_cell(
        pdf.content_w,
        5,
        "Documento preparado para apoio à documentação institucional do SIGEPA — 22/05/2026.",
    )

    pdf.output(str(OUT_PDF))
    print(f"OK: {OUT_PDF} ({pdf.page_no()} páginas)")


if __name__ == "__main__":
    build()
