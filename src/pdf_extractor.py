from .pdf_loader import PDFLoader
from .image_ocr_processor import ImageProcessor
from .text_extractor import TextExtractor
from .header_footer_detector import HeaderFooterDetector

class PDFExtractor:
    def __init__(self, pdf_path, text_output_path, lang='eng'):
        """
        Inicializa o extrator de PDF.

        :param pdf_path: Caminho para o arquivo PDF de entrada.
        :param text_output_path: Caminho para o arquivo de texto de saída.
        :param lang: Idioma para o OCR.
        """
        self.pdf_loader = PDFLoader(pdf_path)
        self.text_output_path = text_output_path
        self.lang = lang

    def extract(self):
        """
        Realiza a extração completa do texto do PDF, removendo cabeçalhos e rodapés, e preservando a ordem.
        """
        # Abrir o PDF
        self.pdf_loader.open_pdf()
        page_count = self.pdf_loader.get_page_count()

        # Coleta de todas as coordenadas para detectar cabeçalho e rodapé
        all_coordinates = {'x0': [], 'y0': [], 'x1': [], 'y1': []}
        for page in self.pdf_loader.iterate_pages():
            blocks = page.get_text('dict')["blocks"]  # Obter blocos como dicionários
            for block in blocks:
                all_coordinates['x0'].append(block['bbox'][0])
                all_coordinates['y0'].append(block['bbox'][1])
                all_coordinates['x1'].append(block['bbox'][2])
                all_coordinates['y1'].append(block['bbox'][3])
                #print(f"Página {page.number + 1}: Coordenadas do bloco: {block['bbox']}")

        # Detectar cabeçalho e rodapé
        detector = HeaderFooterDetector(page_count)
        header, footer = detector.detect(all_coordinates)

        # Adicionar logs de depuração
        #print(f"Header detectado: {header}")
        #print(f"Footer detectado: {footer}")

        # Inicializar processadores
        text_extractor = TextExtractor(header, footer)
        image_processor = ImageProcessor(lang=self.lang)

        final_text = ""

        # Iterar novamente pelas páginas para extrair texto e OCR
        for page in self.pdf_loader.iterate_pages():
            blocks = page.get_text('dict')["blocks"]

            # Extrair texto digital
            text_elements = text_extractor.extract(page, blocks)

            # Extrair texto via OCR das imagens
            ocr_elements = image_processor.extract_and_ocr(page, blocks)

            # Combinar todos os elementos de texto
            all_elements = text_elements + ocr_elements

            # Ordenar os elementos por posição (y0, x0) para manter a ordem do documento
            all_elements.sort(key=lambda elem: (elem[1].y0, elem[1].x0))

            # Concatenar o texto na ordem correta
            for text, rect in all_elements:
                if text:  # Apenas adicionar se houver texto
                    final_text += text + "\n"

            final_text += "\n"  # Adicionar nova linha entre páginas

        # Fechar o PDF
        self.pdf_loader.close_pdf()

        # Salvar o texto extraído em um arquivo
        with open(self.text_output_path, "w", encoding="utf-8") as f:
            f.write(final_text.strip())

        print(f"Texto extraído salvo em: {self.text_output_path}")

    def run(self):
        self.extract()
