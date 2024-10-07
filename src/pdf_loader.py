import fitz  # PyMuPDF

class PDFLoader:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.document = None

    def open_pdf(self):
        self.document = fitz.open(self.pdf_path)

    def close_pdf(self):
        if self.document:
            self.document.close()

    def get_page_count(self):
        return self.document.page_count

    def iterate_pages(self):
        for page_number in range(self.get_page_count()):
            yield self.document.load_page(page_number)
