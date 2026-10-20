"""FastAPI 主入口：提供 API + 飞书 Webhook"""
import os
import json
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import settings
from app.rag.loader import load_and_split
from app.rag.vectorstore import add_documents
from app.rag.chain import RAGChain
from app.essay.grader import EssayGrader
from app.planner.planner import ExamPlanner
from app.flashcard.generator import FlashcardGenerator
from app.research.tuition import TuitionAnalyzer
from app.research.ratio import AdmissionAnalyzer
from app.research.compare import ProgramCompare
from app.research.report import ResearchReport
from app.research.search import search_or_hint
from app.feishu.bot import FeishuBot

app = FastAPI(title="考研AIGC助手", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化模块
rag = RAGChain()
grader = EssayGrader()
planner = ExamPlanner()
flashcard_gen = FlashcardGenerator()
tuition_analyzer = TuitionAnalyzer()
admission_analyzer = AdmissionAnalyzer()
program_compare = ProgramCompare()
research_report = ResearchReport()


# ====== Pydantic 模型 ======
class QAQuery(BaseModel):
    question: str


class EssayRequest(BaseModel):
    topic: str
    essay: str
    subject: str = "english"  # english / politics


class PlanRequest(BaseModel):
    target_school: str
    target_major: str
    subjects: str = ""
    foundation: str = "一般"
    months_left: int = 12
    daily_hours: float = 8.0


class SchoolRequest(BaseModel):
    bg: str
    major: str
    score: str
    location: str = "不限"
    degree_type: str = "学硕"
    notes: str = ""


class FlashcardRequest(BaseModel):
    content: str


class SchoolMajorRequest(BaseModel):
    school: str
    major: str


# ====== API 路由 ======
@app.get("/")
def root():
    return {"name": "考研AIGC助手", "status": "running", "version": "2.0.0", "docs": "/docs"}


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传考研资料到知识库"""
    save_dir = "./data/uploaded"
    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, file.filename)

    with open(path, "wb") as f:
        f.write(await file.read())

    docs = load_and_split(path)
    count = add_documents(docs)
    return {"filename": file.filename, "chunks_added": count, "status": "ok"}


@app.post("/api/qa")
def qa(query: QAQuery):
    """RAG 问答"""
    result = rag.ask_with_sources(query.question)
    return result


@app.post("/api/essay/grade")
def grade_essay(req: EssayRequest):
    """作文批改"""
    if req.subject == "politics":
        result = grader.grade_politics(req.topic, req.essay)
    else:
        result = grader.grade_english(req.topic, req.essay)
    return {"result": result}


@app.post("/api/planner/plan")
def make_plan(req: PlanRequest):
    """生成复习计划"""
    result = planner.make_plan(
        target_school=req.target_school,
        target_major=req.target_major,
        subjects=req.subjects,
        foundation=req.foundation,
        months_left=req.months_left,
        daily_hours=req.daily_hours,
    )
    return {"plan": result}


@app.post("/api/planner/schools")
def recommend_schools(req: SchoolRequest):
    """择校推荐"""
    result = planner.recommend_schools(
        bg=req.bg, major=req.major, score=req.score,
        location=req.location, degree_type=req.degree_type, notes=req.notes,
    )
    return {"recommendation": result}


@app.post("/api/flashcard")
def make_flashcards(req: FlashcardRequest):
    """生成闪卡"""
    cards = flashcard_gen.generate(req.content)
    return {"cards": cards}


# ====== 全网情报检索 API ======
@app.post("/api/research/tuition")
def research_tuition(req: SchoolMajorRequest):
    """学费情报检索"""
    return {"result": tuition_analyzer.analyze(req.school, req.major)}


@app.post("/api/research/admission")
def research_admission(req: SchoolMajorRequest):
    """报录比/分数线情报检索"""
    return {"result": admission_analyzer.analyze(req.school, req.major)}


@app.post("/api/research/compare")
def research_compare(req: SchoolMajorRequest):
    """专硕 vs 学硕对比分析"""
    return {"result": program_compare.analyze(req.major)}


@app.post("/api/research/report")
def research_report_api(req: SchoolMajorRequest):
    """一键生成完整分析报告"""
    return {"report": research_report.generate(req.school, req.major)}


@app.post("/api/research/search")
def research_search(req: SchoolMajorRequest):
    """原始全网检索（不经过 LLM 总结）"""
    query = f"{req.school} {req.major} 学费 报录比 分数线 招生"
    return {"result": search_or_hint(query)}


# ====== 飞书 Webhook ======
@app.post("/feishu/webhook")
async def feishu_webhook(request: Request):
    """飞书事件订阅回调"""
    body = await request.json()

    # 飞书 URL 验证
    if body.get("type") == "url_verification":
        return {"challenge": body.get("challenge")}

    # 处理消息事件
    event = body.get("event", {})
    bot = FeishuBot()
    reply = bot.handle_message(event)

    # 发送回复
    chat_id = event.get("message", {}).get("chat_id", "")
    if chat_id:
        bot.send_text(chat_id, reply)

    return {"code": 0}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
