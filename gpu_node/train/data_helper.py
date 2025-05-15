import re
from functools import partial
from multiprocessing import Pool, cpu_count
from typing import Dict, List, Tuple
from tqdm import tqdm
import json
import random


def clean_weibo_title(title: str) -> str:
    """
    清洗微博标题文本，移除特殊标记和多余空格
    
    Args:
        title: 原始标题文本

    Returns:
        str: 清洗后的标题文本
    """
    # 去除##符号（一般为微博数据的话题标记）
    title = re.sub(r"#", "", title)
    # 去除[]中间的文字（一般为微博数据中的表情）
    title = re.sub(r"(\[{1,2})(.*?)(]{1,2})", "", title)
    # 合并标题中过多的空格
    title = re.sub(r"\s+", " ", title)
    return title


def clean_weibo_content(content: str) -> str:
    """
    清洗微博正文内容，移除URL、多余空格和特殊字符
    
    Args:
        content: 原始正文内容

    Returns:
        str: 清洗后的正文内容
    """
    # 去除网址
    content = re.sub(r"(https|http)?://(\w|\.|/|\?|=|&|%)*\b", "", content)
    # 合并正文中过多的空格
    content = re.sub(r"\s+", " ", content)
    # 去除\u200b字符
    content = content.replace("\u200b", "")
    return content


def clean_data(sample: Tuple[str, str]) -> Dict[str, str]:
    """
    对单个数据样本进行清洗处理
    
    Args:
        sample: 包含(content, title)的元组

    Returns:
        Dict[str, str]: 包含清洗后的content和title的字典
    """
    content, title = sample
    return {
        "title": clean_weibo_title(title.strip()),
        "content": clean_weibo_content(content.strip())
    }


def build_news_data(
    content_path: str,
    title_path: str,
    train_save_path: str,
    test_save_path: str,
    test_size: int = 3000,
    min_content_length: int = 100,
    min_title_length: int = 2
) -> None:
    """
    构建新闻数据集，将原始数据清洗并划分为训练集和测试集
    
    Args:
        content_path: 正文文件路径
        title_path: 标题文件路径
        train_save_path: 训练集保存路径
        test_save_path: 测试集保存路径
        test_size: 测试集大小，默认3000条
        min_content_length: 正文最小长度，默认100字
        min_title_length: 标题最小长度，默认2字
    """
    # 读取原始数据
    with open(content_path, "r", encoding="utf-8") as f_content, \
         open(title_path, "r", encoding="utf-8") as f_title:
        data = zip(f_content.readlines(), f_title.readlines())
    
    # 多进程数据清洗
    n_threads = min(8, cpu_count())
    with Pool(n_threads) as pool:
        cleaned_data = list(tqdm(
            pool.imap(clean_data, data, chunksize=8),
            desc="清洗数据中"
        ))
    
    # 数据过滤
    unique_contents = set()
    filtered_data = []
    for item in cleaned_data:
        if (item["content"] not in unique_contents and 
            len(item["content"]) >= min_content_length and 
            len(item["title"]) >= min_title_length):
            unique_contents.add(item["content"])
            filtered_data.append(item)
    
    # 划分数据集
    random.shuffle(filtered_data)
    train_data = filtered_data[:-test_size]
    test_data = filtered_data[-test_size:]
    
    # 保存数据集
    for path, data in [(train_save_path, train_data), (test_save_path, test_data)]:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    content_path_dir = "data_dir/train_text.txt"
    title_path_dir = "data_dir/train_label.txt"
    train_save_path_dir = "data_dir/train_data.json"
    test_save_path_dir = "data_dir/test_data.json"
    build_news_data(content_path_dir, title_path_dir, train_save_path_dir, test_save_path_dir)
