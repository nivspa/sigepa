# -*- coding: utf-8 -*-
"""Anexa a seção 12 (deploy automático) ao PDF do relatório."""
from pathlib import Path

from fpdf import FPDF
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parents[1]
SRC_PDF = ROOT / "docs" / "Relatorio_Melhorias_Ficha_Ocorrencia_SIGEPA.pdf"
OUT_PDF = SRC_PDF
APPEND_PDF = ROOT / "docs" / "_relatorio_secao12_temp.pdf"

FONT = "Arial"
FONT_DIR = Path(r"C:\Windows\Fonts")


class RelatorioPDF(FPDF):
    page_offset = 6  # relatório original tem 6 páginas

    def header(self):
        self.set_font(FONT, size=9)
        self.set_text_color(80, 80, 80)
        w = self.w - self.l_margin - self.r_margin
        pagina = self.page_no() + self.page_offset
        self.cell(w / 2, 8, "SIGEPA — Melhorias na ficha de ocorrência", align="L")
        self.cell(w / 2, 8, f"Página {pagina}", align="R", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def footer(self):
        pass

    def section_title(self, num: str, title: str):
        self.set_font(FONT, "B", 13)
        self.set_text_color(0, 0, 0)
        w = self.w - self.l_margin - self.r_margin
        self.multi_cell(w, 8, f"{num}. {title}")
        self.ln(2)

    def body(self, text: str):
        self.set_font(FONT, size=11)
        w = self.w - self.l_margin - self.r_margin
        self.multi_cell(w, 6, text)
        self.ln(2)

    def bullet(self, text: str):
        self.set_font(FONT, size=11)
        w = self.w - self.l_margin - self.r_margin
        self.multi_cell(w, 6, f"- {text}")

    def antes_agora(self, antes: str, agora: str):
        self.set_font(FONT, "B", 11)
        self.cell(0, 6, "Antes", new_x="LMARGIN", new_y="NEXT")
        self.set_font(FONT, size=11)
        w = self.w - self.l_margin - self.r_margin
        self.multi_cell(w, 6, antes)
        self.ln(1)
        self.set_font(FONT, "B", 11)
        self.cell(0, 6, "Agora", new_x="LMARGIN", new_y="NEXT")
        self.set_font(FONT, size=11)
        self.multi_cell(w, 6, agora)
        self.ln(3)


def build_appendix() -> None:
    pdf = RelatorioPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_font(FONT, "", str(FONT_DIR / "arial.ttf"))
    pdf.add_font(FONT, "B", str(FONT_DIR / "arialbd.ttf"))

    pdf.add_page()
    pdf.section_title(
        "12",
        "Atualização em produção ficou automática",
    )
    pdf.body(
        "Depois que uma melhoria no sistema é aprovada e enviada para o repositório "
        "oficial, o ambiente de produção passa a receber a versão nova sozinha, em "
        "poucos minutos — sem precisar copiar arquivos na mão nem entrar no servidor "
        "a cada correção."
    )

    pdf.set_font(FONT, "B", 11)
    pdf.cell(0, 7, "Como funciona, em linguagem simples", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.bullet(
        "O desenvolvedor envia a alteração para a versão principal do projeto."
    )
    pdf.bullet(
        "Um processo na nuvem (GitHub) monta a nova versão do SIGEPA e publica o "
        "pacote atualizado, no mesmo estilo de outros sistemas da área."
    )
    pdf.bullet(
        "No ambiente de produção (Portainer), o serviço Shepherd verifica, a cada "
        "5 minutos, se existe versão nova."
    )
    pdf.bullet(
        "Quando encontra, reinicia o SIGEPA já com a versão atualizada."
    )
    pdf.ln(2)

    pdf.antes_agora(
        "Cada mudança exigia publicar a versão e, em seguida, alguém abrir o "
        "Portainer, localizar o serviço do SIGEPA e clicar em atualizar manualmente. "
        "Era fácil esquecer ou demorar.",
        "O fluxo de rotina é: enviar a melhoria → aguardar o processo na nuvem "
        "(cerca de 2 minutos) → em até 5 minutos o Shepherd aplica em produção. "
        "Quem testa só precisa atualizar a página no navegador (Ctrl + F5).",
    )

    pdf.set_font(FONT, "B", 11)
    pdf.cell(0, 7, "O que isso não muda", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.bullet(
        "Cadastro de usuários continua só pelo administrador (item 11 deste relatório)."
    )
    pdf.bullet(
        "Os dados das fichas no banco não são apagados — só o programa (telas e regras) é trocado."
    )
    pdf.bullet(
        "Senhas e configurações sensíveis continuam somente no Portainer, não no GitHub."
    )
    pdf.ln(2)

    pdf.add_page()
    pdf.set_font(FONT, "B", 13)
    pdf.cell(0, 8, "Como saber se deu certo", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.body("(Para quem for testar ou documentar.)")
    pdf.bullet("Na nuvem (GitHub → Actions), o passo de build aparece com sucesso (verde).")
    pdf.bullet(
        'Nos registros do Shepherd no Portainer: "Service sigepa_sigepa was updated!".'
    )
    pdf.bullet("A data de última atualização do serviço SIGEPA no Portainer fica recente.")
    pdf.bullet("A melhoria aparece no site em produção após Ctrl + F5 no navegador.")
    pdf.ln(4)

    pdf.set_font(FONT, "B", 12)
    pdf.cell(0, 8, "Lista rápida — incluir ao testar", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font(FONT, size=10)
    col_w = (pdf.w - pdf.l_margin - pdf.r_margin) / 2
    pdf.set_font(FONT, "B", 10)
    pdf.cell(col_w, 7, "O quê testar", border=1)
    pdf.cell(col_w, 7, "O que deve acontecer", border=1, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(FONT, size=10)
    pdf.cell(col_w, 10, "Deploy automático", border=1)
    pdf.cell(
        col_w,
        10,
        "Após envio aprovado, em até ~5 min a versão nova em produção (Ctrl + F5).",
        border=1,
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(6)

    pdf.set_font(FONT, "B", 11)
    pdf.cell(0, 7, "Observação para documentação", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(FONT, size=11)
    w = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.multi_cell(
        w,
        6,
        "Este fluxo segue a mesma ideia do backend Saúde Pará: a nuvem prepara a versão; "
        "o ambiente interno da Secretaria aplica em produção. O SIGEPA usa o Shepherd "
        "dentro da rede para aplicar sozinho, sem o desenvolvedor precisar de acesso "
        "remoto ao servidor.",
    )
    pdf.ln(4)
    pdf.set_font(FONT, size=9)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(
        w,
        5,
        "Seção 12 acrescentada ao relatório de 22/05/2026 — atualização automática em produção.",
    )

    pdf.output(str(APPEND_PDF))


def merge_pdfs() -> None:
    reader = PdfReader(str(SRC_PDF))
    appendix = PdfReader(str(APPEND_PDF))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    for page in appendix.pages:
        writer.add_page(page)
    with open(SRC_PDF, "wb") as f:
        writer.write(f)
    APPEND_PDF.unlink(missing_ok=True)


if __name__ == "__main__":
    build_appendix()
    merge_pdfs()
    print(f"OK: {OUT_PDF} atualizado com seção 12.")
