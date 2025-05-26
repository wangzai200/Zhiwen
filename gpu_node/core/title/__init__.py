from .title import TitleGenerator

generator = TitleGenerator(
        model_path="core/title/checkpoint-1079962",
        vocab_path="core/title/vocab",
        device="cuda:0"  # 使用第一个GPU
    )
