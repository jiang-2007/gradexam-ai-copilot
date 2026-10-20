"""考研规划与择校助手"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import settings


PLAN_PROMPT = """你是一位资深考研规划师，帮助学生制定复习计划。

学生情况：
- 目标院校：{target_school}
- 目标专业：{target_major}
- 考试科目：{subjects}
- 目前基础：{foundation}
- 剩余时间：{months_left} 个月
- 每日可学习时长：{daily_hours} 小时

请输出：
1. 总体阶段划分（基础/强化/冲刺/模考）
2. 每月详细任务安排
3. 各科复习策略与推荐资料
4. 每周时间分配表
5. 风险预警与调整建议

要求：计划要具体到可执行，不要空话。"""


SCHOOL_PROMPT = """你是考研择校专家。请根据以下学生情况推荐合适的院校。

学生情况：
- 本科院校层次：{bg}
- 目标专业：{major}
- 估分水平：{score}
- 地域偏好：{location}
- 学硕/专硕：{degree_type}
- 其他要求：{notes}

请输出：
1. 冲刺院校（2-3所）：理由 + 近年分数线 + 报录比
2. 稳妥院校（2-3所）：理由 + 近年分数线 + 报录比
3. 保底院校（1-2所）：理由 + 近年分数线 + 报录比
4. 最终推荐及理由
5. 注意事项（复试线、歧视、压分等）"""


class ExamPlanner:
    def __init__(self):
        self.llm = ChatOpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            temperature=0.4,
        )

    def make_plan(self, target_school: str, target_major: str,
                  subjects: str, foundation: str,
                  months_left: int, daily_hours: float) -> str:
        """生成复习计划"""
        prompt = ChatPromptTemplate.from_template(PLAN_PROMPT)
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({
            "target_school": target_school,
            "target_major": target_major,
            "subjects": subjects,
            "foundation": foundation,
            "months_left": months_left,
            "daily_hours": daily_hours,
        })

    def recommend_schools(self, bg: str, major: str, score: str,
                          location: str, degree_type: str, notes: str = "") -> str:
        """择校推荐"""
        prompt = ChatPromptTemplate.from_template(SCHOOL_PROMPT)
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({
            "bg": bg,
            "major": major,
            "score": score,
            "location": location,
            "degree_type": degree_type,
            "notes": notes,
        })
