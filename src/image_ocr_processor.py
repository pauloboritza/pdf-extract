from PIL import Image
import pytesseract
import io
import sys
import fitz  # PyMuPDF
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class ImageProcessor:
    def __init__(self, lang='eng'):
        """
        Inicializa o processador de imagens.

        :param lang: Idioma para o OCR.
        """
        self.lang = lang

    def extract_and_ocr(self, page, blocks):
        """
        Extrai imagens dos blocos e realiza OCR nelas.

        :param page: Objeto de página do PyMuPDF.
        :param blocks: Lista de blocos da página.
        :return: Lista de tuplas contendo o texto OCR e suas coordenadas.
        """
        text_elements = []

        for block in blocks:
            # Verificar o tipo de block
            if not isinstance(block, dict):
                print(f"Depuração: Tipo de bloco inesperado: {type(block)}", file=sys.stderr)
                continue
            if block['type'] == 1:  # Bloco de imagem
                try:
                    image_info = block.get("image")

                    if isinstance(image_info, dict):
                        # Caso 1: Bloco de imagem com 'xref'
                        xref = image_info.get("xref")
                        if xref:
                            base_image = page.parent.extract_image(xref)
                            image_bytes = base_image["image"]
                        else:
                            # Caso 2: Bloco de imagem sem 'xref', tenta acessar 'image' diretamente
                            print(f"Depuração: Bloco de imagem na página {page.number + 1} não possui 'xref'.", file=sys.stderr)
                            image_bytes = image_info.get("image")
                            if not isinstance(image_bytes, bytes):
                                print(f"Erro: Dados de imagem inválidos na página {page.number + 1}.", file=sys.stderr)
                                continue
                            # Inferir a extensão da imagem, se possível
                            image_ext = "png"  # Padrão, pode ajustar conforme necessário

                    elif isinstance(image_info, bytes):
                        # Caso 3: 'image' é diretamente bytes
                        image_bytes = image_info
                        image_ext = "png"  # Padrão, pode ajustar conforme necessário

                    else:
                        print(f"Erro: Formato inesperado de 'image' na página {page.number + 1}. Tipo: {type(image_info)}", file=sys.stderr)
                        continue

                    # Processa a imagem em memória
                    image_stream = io.BytesIO(image_bytes)
                    try:
                        pil_image = Image.open(image_stream)
                    except Exception as e:
                        print(f"Erro ao abrir a imagem na página {page.number + 1}: {e}", file=sys.stderr)
                        continue

                    # (Opcional) Pré-processamento da imagem para melhorar o OCR
                    # pil_image = pil_image.convert('L')  # Converte para escala de cinza
                    # pil_image = pil_image.point(lambda x: 0 if x < 128 else 255, '1')  # Binarização

                    # Realiza OCR na imagem
                    ocr_text = pytesseract.image_to_string(pil_image, lang=self.lang)

                    # Adiciona o texto OCR e a posição à lista
                    rect = fitz.Rect(block["bbox"])
                    text_elements.append((ocr_text.strip(), rect))

                except KeyError as e:
                    print(f"Erro: Bloco de imagem na página {page.number + 1} não possui a chave esperada: {e}", file=sys.stderr)
                except Exception as e:
                    print(f"Erro ao processar a imagem na página {page.number + 1}: {e}", file=sys.stderr)
                    continue

        return text_elements
