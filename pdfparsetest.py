from pdfminer.high_level import extract_text

text = extract_text('testdatas/科技写作-丁海川-201892468.pdf')

print(text)