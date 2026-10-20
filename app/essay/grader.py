"""作文批改：英语作文 + 政治论述题"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import settings


ENGLISH_PROMPT = """你是考研英语作文阅卷老师。请按照考研英语一/二评分标准（满分20分）批改下面的作文。

请输出：
1. 总分（0-20分）
2. 评分理由（内容、结构、语言三方面）
3. 语法错误逐句标注
4. 词汇升级建议（至少3个）
5. 润色后的高分范文

作文题目：{topic}
学生作文：{essay}

请用中文回复。"""


POLITICS_PROMPT = """你是考研政治阅卷组组长。请按照考研政治分析题评分标准（满分10分）批改下面的论述题答案。

请输出：
1. 总分（0-10分）
2. 踩分点对照（答到了哪些，漏了哪些）
3. 逻辑结构问题
4. 规范表述修正
5. 参考答案要点

题目：{topic}
学生答案：{essay}

请用中文回复。"""


class EssayGrader:
    def __init__(self):
        self.llm = ChatOpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            temperature=0.2,
        )

    def grade_english(self, topic: str, essay: str) -> str:
        """批改英语作文"""
        prompt = ChatPromptTemplate.from_template(ENGLISH_PROMPT)
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"topic": topic, "essay": essay})

    def grade_politics(self, topic: str, essay: str) -> str:
        """批改政治论述题"""
        prompt = ChatPromptTemplate.from_template(POLITICS_PROMPT)
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"topic": topic, "essay": essay})
