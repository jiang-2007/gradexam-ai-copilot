"""专硕 vs 学硕：内置对比知识 + 全网检索最新政策补充"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import settings
from app.research.search import WebSearch


# 内置权威对比（来源：研招网《专业硕士与学术硕士的区别》)
BUILTIN_COMPARE = """
【学硕与专硕六大核心区别（权威口径：中国研究生招生信息网）】
1. 培养目标：学硕培养学术研究人才；专硕培养高层次应用型人才。
2. 培养方式：学硕重基础理论与科研方法，单导师制；专硕重实践应用与案例教学，实行双导师制（校内+校外），要求至少半年实践环节。
3. 考试科目：学硕多数考英语（一）；专硕多数考英语（二），难度相对较低。数学与专业课科目因专业而异。
4. 学制学费：学硕一般3年，学费按国家指导价（原则上不超8000元/年），奖助覆盖率高；专硕一般2-3年，学费由院校自定，普遍高于学硕（多数1万-3万/年，商科/艺术类更高）。
5. 读博路径：学硕可申请硕博连读/直博；专硕一般需参加博士统考或申请考核制。
6. 调剂规则：学硕可调剂到专硕；专硕一般不能反向调剂学硕。
"""

COMPARE_PROMPT = """你是考研择校规划专家。请结合权威对比知识，并根据全网最新政策（重点看学硕缩招、专硕扩招趋势），对「{major}」专业的学硕与专硕做完整对比分析。

请输出：
1. 学硕与专硕对比总表（培养目标/学制/学费/考试科目/读博/就业/调剂/导师制度，至少8个维度）
2. 该专业最新的招生趋势（学硕缩招情况、专硕扩招情况，基于搜索资料）
3. 就业与读博路径差异（针对该专业具体说明）
4. 给三类考生分别给出选择建议：想读博科研的人 / 想尽快就业的人 / 经济条件有限的人
5. 最终一句话结论

权威对比知识：
{builtin}

全网最新政策信息：
{context}

请用中文回复。"""


class ProgramCompare:
    def __init__(self):
        self.llm = ChatOpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            temperature=0.3,
        )

    def analyze(self, major: str) -> str:
        """对比分析某专业的学硕与专硕"""
        ws = WebSearch()
        query = f"{major} 专硕 学硕 区别 学硕缩招 专硕扩招 2026 2027"
        try:
            context = ws.search_text(query)
        except RuntimeError as e:
            # 无搜索能力时退化为纯内置知识对比
            context = "（无网络检索，仅基于内置权威知识对比）"

        prompt = ChatPromptTemplate.from_template(COMPARE_PROMPT)
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({
            "major": major,
            "builtin": BUILTIN_COMPARE,
            "context": context,
        })
