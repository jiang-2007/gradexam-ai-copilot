"""报录比 / 分数线 / 招生数据情报"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import settings
from app.research.search import WebSearch


RATIO_PROMPT = """你是考研数据情报分析师。下面是从全网搜索到的关于「{school} {major}」的招生数据，请整理成结构化情报。

要求输出：
1. 复试分数线（区分学硕/专硕、全日制/非全、总分与单科）
2. 国家线对比（该专业所在学科门类 A 类线）
3. 招生计划与统考录取人数（历年变化）
4. 报考人数 / 报录比（能找到多少写多少，标明年份）
5. 推免占比（如果提到）
6. 数据可信度标注：官方来源 vs 第三方整理

搜索资料：
{context}

请用中文回复，用表格和列表组织。"""


class AdmissionAnalyzer:
    def __init__(self):
        self.llm = ChatOpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            temperature=0.1,
        )

    def analyze(self, school: str, major: str) -> str:
        """检索并分析报录比/分数线"""
        ws = WebSearch()
        query = f"{school} {major} 复试分数线 报录比 录取人数 招生计划"
        try:
            context = ws.search_text(query)
        except RuntimeError as e:
            return f"【搜索未启用】{e}"

        prompt = ChatPromptTemplate.from_template(RATIO_PROMPT)
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"school": school, "major": major, "context": context})
