import fitz  # PyMuPDF
import sys

class TextExtractor:
    def __init__(self, header, footer):
        """
        Inicializa o extrator de texto.

        :param header: Coordenada y0 do limite superior do cabeçalho.
        :param footer: Coordenada y1 do limite inferior do rodapé.
        """
        self.header = header
        self.footer = footer

    def extract(self,page, blocks):
        """
        Extrai texto dos blocos, ignorando cabeçalho e rodapé.

        :param blocks: Lista de blocos de texto do PDF.
        :return: Lista de tuplas contendo o texto e suas coordenadas.
        """
        text_elements = []

        for block in blocks:
            # Verificar o tipo de block
            if not isinstance(block, dict):
                print(f"Depuração: Tipo de bloco inesperado: {type(block)}", file=sys.stderr)
                continue
            rect = fitz.Rect(block["bbox"])
            #print(f"Bloco de texto na página {page.number + 1}: {rect.y0} - {rect.y1}")
            # Ignorar texto que está nos limites do cabeçalho e rodapé
            if ((self.header is None or rect.y0 >= self.header) and
                (self.footer is None or rect.y1 <= self.footer)):
                if block['type'] == 0:  # Bloco de texto
                    text = ""
                    for line in block["lines"]:
                        line_text = " ".join([span["text"] for span in line["spans"]])
                        text += line_text + "\n"
                    text_elements.append((text.strip(), rect))

        return text_elements
