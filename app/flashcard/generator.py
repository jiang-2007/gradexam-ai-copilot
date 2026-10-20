"""AI 自动生成考研背诵闪卡"""
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import settings


FLASHCARD_PROMPT = """请把下面的考研笔记内容拆解成背诵闪卡。

要求：
1. 每张闪卡正面是问题/名词，背面是答案
2. 答案要精炼，控制在 50 字以内
3. 优先提取高频考点和易混淆概念
4. 输出格式为 JSON 数组，每个元素包含 "front" 和 "back" 字段

笔记内容：
{content}

只输出 JSON，不要其他文字。"""


class FlashcardGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            temperature=0.1,
        )

    def generate(self, content: str, max_cards: int = 20) -> list:
        """从笔记内容生成闪卡列表"""
        prompt = ChatPromptTemplate.from_template(FLASHCARD_PROMPT)
        chain = prompt | self.llm | StrOutputParser()
        raw = chain.invoke({"content": content[:3000]})

        # 解析 JSON
        try:
            # 清理可能的 markdown 代码块标记
            raw = raw.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1]
            if raw.endswith("```"):
                raw = raw.rsplit("```", 1)[0]
            raw = raw.strip()

            cards = json.loads(raw)
            return cards[:max_cards]
        except json.JSONDecodeError:
            # 解析失败时返回原始文本
            return [{"front": "解析失败", "back": raw[:500]}]

    def generate_from_text(self, text: str) -> str:
        """生成可读格式的闪卡文本"""
        cards = self.generate(text)
        lines = []
        for i, card in enumerate(cards, 1):
            lines.append(f"【闪卡 {i}】")
            lines.append(f"Q: {card.get('front', '')}")
            lines.append(f"A: {card.get('back', '')}")
            lines.append("")
        return "\n".join(lines)
