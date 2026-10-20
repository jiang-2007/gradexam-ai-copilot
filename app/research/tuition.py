"""学费情报：全网检索指定院校/专业的学费标准（学硕 vs 专硕 vs 非全）"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import settings
from app.research.search import WebSearch


TUITION_PROMPT = """你是考研情报分析师。下面是从全网搜索到的关于「{school} {major}」的学费与招生信息，请提取并整理成结构化结论。

要求：
1. 分别列出：学术学位学费、专业学位学费、非全日制学费（如果有）
2. 标注学费单位（元/年 或 万元/全程）、学制
3. 区分"已查证"（有明确来源）与"未提及"（资料里没有）
4. 用表格形式输出
5. 如果信息互相矛盾，全部列出并标注来源
6. 最后给出一句话总结：该校该专业读研的学费成本高低

搜索资料：
{context}

请用中文回复。"""


class TuitionAnalyzer:
    def __init__(self):
        self.llm = ChatOpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            temperature=0.1,
        )

    def analyze(self, school: str, major: str) -> str:
        """检索并分析学费"""
        ws = WebSearch()
        query = f"{school} {major} 学费 学制 研究生招生简章"
        try:
            context = ws.search_text(query)
        except RuntimeError as e:
            return f"【搜索未启用】{e}"

        prompt = ChatPromptTemplate.from_template(TUITION_PROMPT)
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"school": school, "major": major, "context": context})
