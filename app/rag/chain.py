"""RAG 问答链"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from config import settings
from app.rag.vectorstore import get_vectorstore


PROMPT_TEMPLATE = """你是一位专业的考研辅导老师。请根据下面提供的参考资料回答学生的问题。

要求：
1. 只基于参考资料回答，不要编造
2. 如果资料里没有相关信息，直接说"知识库中暂无相关内容"
3. 回答要条理清晰，分点说明
4. 涉及知识点时，标注可能的考点

参考资料：
{context}

学生问题：{question}

回答："""


def get_llm():
    return ChatOpenAI(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        temperature=0.3,
    )


class RAGChain:
    def __init__(self):
        self.llm = get_llm()
        self.prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)

    def ask(self, question: str) -> str:
        """基于知识库回答问题"""
        vs = get_vectorstore()
        retriever = vs.as_retriever(search_kwargs={"k": 4})

        chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        return chain.invoke(question)

    def ask_with_sources(self, question: str) -> dict:
        """回答并返回引用来源"""
        vs = get_vectorstore()
        docs = vs.similarity_search(question, k=4)
        context = "\n\n".join([d.page_content for d in docs])

        chain = self.prompt | self.llm | StrOutputParser()
        answer = chain.invoke({"context": context, "question": question})

        sources = []
        for d in docs:
            src = d.metadata.get("source", "未知")
            page = d.metadata.get("page", "")
            sources.append(f"{src} (p.{page})" if page else src)

        return {"answer": answer, "sources": list(set(sources))}
