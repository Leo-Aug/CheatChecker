from docx import Document

document = Document('testdatas/科学写作-高亚峰-201892098.docx')

for paragraph in document.paragraphs:
    print(paragraph.text)