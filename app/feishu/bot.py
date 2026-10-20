"""飞书机器人：接收消息 -> 路由到对应功能 -> 回复"""
import json
import lark_oapi as lark
from lark_oapi.api.im.v1 import *
from config import settings
from app.rag.chain import RAGChain
from app.essay.grader import EssayGrader
from app.planner.planner import ExamPlanner
from app.flashcard.generator import FlashcardGenerator
from app.research.tuition import TuitionAnalyzer
from app.research.ratio import AdmissionAnalyzer
from app.research.compare import ProgramCompare
from app.research.report import ResearchReport


# 命令路由
HELP_TEXT = """📚 考研AIGC助手 指令大全

【问答】直接输入问题即可，例如：什么是认知失调？
【作文批改】/essay 题目 | 作文内容
【政治批改】/politics 题目 | 答案内容
【复习计划】/plan 目标院校 | 目标专业 | 基础 | 剩余月数 | 每日小时
【择校】/school 本科层次 | 专业 | 估分 | 地域 | 学硕/专硕
【闪卡】/flashcard 笔记内容
【学费情报】/tuition 院校 | 专业
【报录比情报】/ratio 院校 | 专业
【专硕学硕对比】/compare 专业
【一键深度报告】/report 院校 | 专业
【帮助】/help"""


class FeishuBot:
    def __init__(self):
        self.rag = RAGChain()
        self.grader = EssayGrader()
        self.planner = ExamPlanner()
        self.flashcard = FlashcardGenerator()
        self.tuition = TuitionAnalyzer()
        self.admission = AdmissionAnalyzer()
        self.compare = ProgramCompare()
        self.report = ResearchReport()

        self.client = lark.Client.builder() \
            .app_id(settings.feishu_app_id) \
            .app_secret(settings.feishu_app_secret) \
            .build()

    def handle_message(self, event: dict) -> str:
        """处理收到的消息事件，返回回复文本"""
        try:
            msg_type = event.get("message", {}).get("message_type", "")
            content = event.get("message", {}).get("content", "{}")

            if msg_type != "text":
                return "目前只支持文字消息哦~"

            content_dict = json.loads(content)
            text = content_dict.get("text", "").strip()

            # 去掉 @机器人 的部分
            text = text.replace("@_user_1", "").strip()

            if not text:
                return HELP_TEXT

            # 命令路由
            if text in ("/help", "帮助", "？", "?"):
                return HELP_TEXT

            elif text.startswith("/essay "):
                payload = text[len("/essay "):]
                if "|" in payload:
                    topic, essay = payload.split("|", 1)
                    return self.grader.grade_english(topic.strip(), essay.strip())
                return "格式：/essay 题目 | 作文内容"

            elif text.startswith("/politics "):
                payload = text[len("/politics "):]
                if "|" in payload:
                    topic, answer = payload.split("|", 1)
                    return self.grader.grade_politics(topic.strip(), answer.strip())
                return "格式：/politics 题目 | 答案内容"

            elif text.startswith("/plan "):
                parts = text[len("/plan "):].split("|")
                if len(parts) >= 5:
                    return self.planner.make_plan(
                        target_school=parts[0].strip(),
                        target_major=parts[1].strip(),
                        subjects="",
                        foundation=parts[2].strip(),
                        months_left=int(parts[3].strip()),
                        daily_hours=float(parts[4].strip()),
                    )
                return "格式：/plan 院校 | 专业 | 基础 | 剩余月 | 每日小时"

            elif text.startswith("/school "):
                parts = text[len("/school "):].split("|")
                if len(parts) >= 5:
                    return self.planner.recommend_schools(
                        bg=parts[0].strip(),
                        major=parts[1].strip(),
                        score=parts[2].strip(),
                        location=parts[3].strip(),
                        degree_type=parts[4].strip(),
                        notes=parts[5].strip() if len(parts) > 5 else "",
                    )
                return "格式：/school 本科 | 专业 | 估分 | 地域 | 学硕/专硕 | 备注"

            elif text.startswith("/flashcard "):
                note = text[len("/flashcard "):]
                return self.flashcard.generate_from_text(note)

            elif text.startswith("/tuition "):
                payload = text[len("/tuition "):]
                if "|" in payload:
                    school, major = payload.split("|", 1)
                    return self.tuition.analyze(school.strip(), major.strip())
                return "格式：/tuition 院校 | 专业（如：/tuition 复旦大学 | 应用心理）"

            elif text.startswith("/ratio "):
                payload = text[len("/ratio "):]
                if "|" in payload:
                    school, major = payload.split("|", 1)
                    return self.admission.analyze(school.strip(), major.strip())
                return "格式：/ratio 院校 | 专业（如：/ratio 复旦大学 | 应用心理）"

            elif text.startswith("/compare "):
                major = text[len("/compare "):].strip()
                return self.compare.analyze(major)

            elif text.startswith("/report "):
                payload = text[len("/report "):]
                if "|" in payload:
                    school, major = payload.split("|", 1)
                    return self.report.generate(school.strip(), major.strip())
                return "格式：/report 院校 | 专业（如：/report 复旦大学 | 应用心理）"

            else:
                # 默认走 RAG 问答
                return self.rag.ask(text)

        except Exception as e:
            return f"处理出错了：{str(e)[:200]}"

    def send_text(self, chat_id: str, text: str):
        """发送文本消息到指定会话"""
        request = CreateMessageRequest.builder() \
            .receive_id(chat_id) \
            .request_body(
                CreateMessageRequestBody.builder()
                .msg_type("text")
                .content(json.dumps({"text": text}))
                .build()
            ) \
            .build()

        # receive_id 类型默认用 chat_id
        request.request_id_type = "chat_id"
        response = self.client.im.v1.message.create(request)
        return response.success()
