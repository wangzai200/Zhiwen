import jiagu


def generate_summary(text: str, sentences_count: int = 3) -> list:
    if not text.strip():
        raise ValueError("Text cannot be empty")

    try:
        sentences = jiagu.summarize(text, sentences_count)
        if not sentences:
            return ["No meaningful summary could be generated"]
        return sentences
    except Exception as e:
        raise RuntimeError(f"Summary generation failed: {str(e)}")

if __name__ == '__main__':
    sample_text = "这是一个测试文本，用于生成摘要。它包含多个句子，目的是验证摘要功能是否正常工作。希望能够生成一个有意义的摘要。"
    try:
        summary = generate_summary(sample_text, 5)
        print("生成的摘要:", summary)
    except Exception as e:
        print("错误:", str(e))