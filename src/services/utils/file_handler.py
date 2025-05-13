import fitz


class PDFHandler:
    @staticmethod
    def extract_text_from(file_bytes):
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        full_text = ""
        for page in doc:
            full_text += page.get_text() + "\n"
        return full_text
