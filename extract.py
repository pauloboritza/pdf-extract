from src.pdf_extractor import PDFExtractor
if __name__ == "__main__":
    import argparse
    import os
    import sys
    from pathlib import Path

    # Configuração de argumentos de linha de comando
    parser = argparse.ArgumentParser(description="Extrator de Texto de PDFs com OCR.")
    parser.add_argument('--pdf', required=True, help='Caminho para o arquivo PDF de entrada.')
    parser.add_argument('--output', required=True, help='Caminho para o arquivo de texto de saída.')
    parser.add_argument('--lang', default='eng', help='Idioma para o OCR (padrão: eng).')

    args = parser.parse_args()
    pdf = Path(args.pdf)
    output = Path(args.output)

    # Verificar se o arquivo PDF existe
    if not os.path.isfile(pdf):
        print(f"Erro: O arquivo '{args.pdf}' não foi encontrado.", file=sys.stderr)
        sys.exit(1)

    # Inicializar e executar o extrator
    extractor = PDFExtractor(pdf, output, lang=args.lang)
    extractor.run()