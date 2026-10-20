"""综合情报分析报告：一键生成指定院校+专业的完整考研分析报告（Markdown）"""
import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import settings
from app.research.search import WebSearch
from app.research.tuition import TuitionAnalyzer
from app.research.ratio import AdmissionAnalyzer
from app.research.compare import ProgramCompare


REPORT_PROMPT = """你是考研情报研究总编辑。请基于以下三份情报，为「{school} {major}」生成一份完整的考研分析报告（Markdown 格式）。

报告必须包含以下章节：
# {school} {major} 考研深度分析报告
> 生成时间：{date} | 数据来源：全网公开信息检索（以官方渠道为准）

## 一、院校与专业概况
（从情报中提取该校该专业的定位、学科排名、培养特色）

## 二、招生数据情报
（复试线、国家线对比、招生人数、报录比、推免占比，尽量用表格）

## 三、学费与学制情报
（学硕/专硕/非全学费与学制对比表）

## 四、学硕 vs 专硕分析
（针对该专业的具体对比与选择建议）

## 五、竞争态势评估
（用 ★ 打难度分：上岸难度、竞争热度、性价比，并说明理由）

## 六、风险与机会提示
（缩招风险、学费成本、调剂空间、跨考友好度等）

## 七、结论与行动建议
（3-5条可执行建议）

【重要】报告末尾附：
## 八、信息来源
列出检索到的核心来源链接。

情报一（学费）：
{t1}

情报二（报录比/分数线）：
{t2}

情报三（专硕学硕对比）：
{t3}

请用中文输出完整 Markdown 报告，数据要注明"已查证/未提及"。"""


class ResearchReport:
    """一键生成考研分析报告"""

    def generate(self, school: str, major: str) -> str:
        """完整报告（联网检索版）"""
        ws = WebSearch()
        ta = TuitionAnalyzer()
        aa = AdmissionAnalyzer()
        pc = ProgramCompare()

        # 并行情报收集（逐个调用，失败不中断）
        t1 = ta.analyze(school, major)
        t2 = aa.analyze(school, major)
        t3 = pc.analyze(major)

        llm = ChatOpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            temperature=0.3,
        )
        prompt = ChatPromptTemplate.from_template(REPORT_PROMPT)
        chain = prompt | llm | StrOutputParser()

        report = chain.invoke({
            "school": school,
            "major": major,
            "date": datetime.date.today().strftime("%Y-%m-%d"),
            "t1": t1,
            "t2": t2,
            "t3": t3,
        })

        # 附上检索到的原始来源
        sources = self._collect_sources(school, major)
        if sources:
            report += "\n\n---\n### 检索来源链接\n" + "\n".join(f"- {s}" for s in sources)
        return report

    def _collect_sources(self, school: str, major: str) -> list:
        """收集检索到的原始来源 URL"""
        ws = WebSearch()
        urls = []
        for query in [f"{school} {major} 招生 学费 报录比", f"{school} 研究生复试分数线"]:
            try:
                results = ws.search(query, count=5)
                urls.extend([r["url"] for r in results if r.get("url")])
            except Exception:
                continue
        # 去重保序
        seen, out = set(), []
        for u in urls:
            if u not in seen:
                seen.add(u)
                out.append(u)
        return out[:10]

    def quick_report(self, school: str, major: str) -> str:
        """离线快速版：无搜索 Key 时基于内置知识生成基础报告"""
        t1 = "（学费：未启用网络检索，请配置 BOCHA_API_KEY 后获取实时学费数据）"
        t2 = "（报录比：未启用网络检索，请配置 BOCHA_API_KEY 后获取实时招生数据）"
        t3 = ProgramCompare().analyze(major)

        llm = ChatOpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            temperature=0.3,
        )
        prompt = ChatPromptTemplate.from_template(REPORT_PROMPT)
        chain = prompt | llm | StrOutputParser()
        return chain.invoke({
            "school": school,
            "major": major,
            "date": datetime.date.today().strftime("%Y-%m-%d"),
            "t1": t1,
            "t2": t2,
            "t3": t3,
        })
