import jieba
from docx import Document
from pdfminer.high_level import extract_text

def create_worddict(text):
    """
    创建词频字典
    """

    # 分割文本
    text_seg = jieba.cut(text)

    # 去除空格
    text_seg = [word for word in text_seg if not word.isspace()]

    # 去除停用词
    stopwords = ['\x0c', '.', '。', ',', '，', '(', '（', ')', '）', '/']
    text_seg = [word for word in text_seg if word not in stopwords]

    # 创建词频字典
    worddict = {}
    for word in text_seg:
        worddict[word] = worddict.get(word, 0) + 1
    return worddict

def compare_text(text1, text2):
    """
    Compare two texts.
    """

    # 创建映射字典
    worddict1 = create_worddict(text1)
    worddict2 = create_worddict(text2)

    # 计算相似度
    similarity = 0
    for word in worddict1:
        if word in worddict2:
            similarity += worddict1[word] * worddict2[word]
    return similarity



if __name__ == "__main__":
    article1 = "\n".join([paragraph.text for paragraph in Document('testdatas/科学写作-高亚峰-201892098.docx').paragraphs])
    article2 = extract_text('testdatas/科技写作-丁海川-201892468.pdf')
    
    print(compare_text(article1, article2))