import torch
import torch.nn.functional as F
from .model import GPT2LMHeadModel
from transformers import BertTokenizer
import copy


def _top_k_top_p_filtering(logits, top_k, top_p, filter_value=-float("Inf")):
    """
    top_k或top_p解码策略，仅保留top_k个或累积概率到达top_p的标记，其他标记设为filter_value，后续在选取标记的过程中会取不到值设为无穷小。
    Args:
        logits: 预测结果，即预测成为词典中每个词的分数
        top_k: 只保留概率最高的top_k个标记
        top_p: 只保留概率累积达到top_p的标记
        filter_value: 过滤标记值

    Returns:

    """
    # logits的维度必须为2，即size:[batch_size, vocab_size]
    assert logits.dim() == 2
    # 获取top_k和字典大小中较小的一个，也就是说，如果top_k大于字典大小，则取字典大小个标记
    top_k = min(top_k, logits[0].size(-1))
    # 如果top_k不为0，则将在logits中保留top_k个标记
    if top_k > 0:
        # 由于有batch_size个预测结果，因此对其遍历，选取每个预测结果的top_k标记
        for logit in logits:
            indices_to_remove = logit < torch.topk(logit, top_k)[0][..., -1, None]
            logit[indices_to_remove] = filter_value
    # 如果top_p不为0，则将在logits中保留概率值累积达到top_p的标记
    if top_p > 0.0:
        # 对logits进行递减排序
        sorted_logits, sorted_indices = torch.sort(logits, descending=True, dim=-1)
        # 对排序后的结果使用softmax归一化，再获取累积概率序列
        # 例如：原始序列[0.1, 0.2, 0.3, 0.4]，则变为：[0.1, 0.3, 0.6, 1.0]
        cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
        # 删除累积概率高于top_p的标记
        sorted_indices_to_remove = cumulative_probs > top_p
        # 将索引向右移动，使第一个标记也保持在top_p之上
        sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
        sorted_indices_to_remove[..., 0] = 0
        for index, logit in enumerate(logits):
            # 由于有batch_size个预测结果，因此对其遍历，选取每个预测结果的累积概率达到top_p的标记
            indices_to_remove = sorted_indices[index][sorted_indices_to_remove[index]]
            logit[indices_to_remove] = filter_value
    return logits


class TitleGenerator:
    def __init__(self, model_path, vocab_path, device='cuda',
                 generate_max_len=32, repetition_penalty=1.2,
                 top_k=5, top_p=0.95, max_len=512):
        """模型初始化函数"""
        self.device = torch.device("cuda" if torch.cuda.is_available() and device != '-1' else "cpu")
        self.tokenizer = BertTokenizer.from_pretrained(vocab_path, local_files_only=True, do_lower_case=True)
        self.model = GPT2LMHeadModel.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()

        # 保存生成参数
        self.generate_max_len = generate_max_len
        self.repetition_penalty = repetition_penalty
        self.top_k = top_k
        self.top_p = top_p
        self.max_len = max_len

    def generate(self, content, num_titles=3):
        """最终生成函数
        Args:
            content: 输入文本内容
            num_titles: 需要生成的标题数量
        Returns:
            List[str]: 生成的标题列表
        """
        return self._predict_one_sample(content, num_titles)

    def _predict_one_sample(self, content, batch_size):
        """修改后的预测函数"""
        content_tokens = self.tokenizer.tokenize(content)
        if len(content_tokens) > self.max_len - 3 - self.generate_max_len:
            content_tokens = content_tokens[:self.max_len - 3 - self.generate_max_len]

        content_id = self.tokenizer.convert_tokens_to_ids("[Content]")
        title_id = self.tokenizer.convert_tokens_to_ids("[Title]")
        unk_id = self.tokenizer.convert_tokens_to_ids("[UNK]")
        sep_id = self.tokenizer.convert_tokens_to_ids("[SEP]")

        content_tokens = ["[CLS]"] + content_tokens + ["[SEP]"]
        input_ids = self.tokenizer.convert_tokens_to_ids(content_tokens)

        # 使用传入的batch_size参数
        input_ids = [copy.deepcopy(input_ids) for _ in range(batch_size)]
        token_type_ids = [[content_id] * len(content_tokens) for _ in range(batch_size)]

        input_tensors = torch.tensor(input_ids).long().to(self.device)
        token_type_tensors = torch.tensor(token_type_ids).long().to(self.device)
        next_token_type = torch.tensor([[title_id] for _ in range(batch_size)]).long().to(self.device)

        generated = []
        finish_set = set()

        with torch.no_grad():
            for _ in range(self.generate_max_len):
                outputs = self.model(input_ids=input_tensors, token_type_ids=token_type_tensors)
                next_token_logits = outputs[0][:, -1, :]

                for index in range(batch_size):
                    for token_id in set([token_ids[index] for token_ids in generated]):
                        next_token_logits[index][token_id] /= self.repetition_penalty

                for next_token_logit in next_token_logits:
                    next_token_logit[unk_id] = -float("Inf")

                filter_logits = _top_k_top_p_filtering(
                    next_token_logits,
                    top_k=self.top_k,
                    top_p=self.top_p
                )

                next_tokens = torch.multinomial(F.softmax(filter_logits, dim=-1), num_samples=1)

                for index, token_id in enumerate(next_tokens[:, 0]):
                    if token_id == sep_id:
                        finish_set.add(index)

                finish_flag = True
                for index in range(batch_size):
                    if index not in finish_set:
                        finish_flag = False
                        break
                if finish_flag:
                    break

                generated.append([token.item() for token in next_tokens[:, 0]])
                input_tensors = torch.cat((input_tensors, next_tokens), dim=-1)
                token_type_tensors = torch.cat((token_type_tensors, next_token_type), dim=-1)

        candidate_responses = []
        for index in range(batch_size):
            responses = []
            for token_index in range(len(generated)):
                if generated[token_index][index] != sep_id:
                    responses.append(generated[token_index][index])
                else:
                    break
            candidate_responses.append(
                "".join(self.tokenizer.convert_ids_to_tokens(responses))
                .replace("##", "").replace("[Space]", " ")
            )
        return candidate_responses

if __name__ == "__main__":
    generator = TitleGenerator(
        model_path="core/title/checkpoint-1079962",
        vocab_path="core/title/vocab",
        device="cuda:0"  # 使用第一个GPU
    )

    SAMPLE_TEXT = """人工智能（Artificial Intelligence，简称AI）是研究、开发用于模拟、延伸和扩展人的智能的理论、方法、技术及应用系统的一门新的技术科学。
    人工智能是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。
    该领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。
    人工智能从诞生以来，理论和技术日益成熟，应用领域也不断扩大。"""

    titles = generator.generate(SAMPLE_TEXT, num_titles=3)
    print(titles)
