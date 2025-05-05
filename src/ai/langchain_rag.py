from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.googlesearch import GoogleSearchTools
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.pgvector import PgVector
from agno.vectordb.chroma import ChromaDb
from agno.embedder.sentence_transformer import SentenceTransformerEmbedder

from dotenv import load_dotenv
import os

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")
os.environ["HUGGINGFACE_API_KEY"] = os.getenv("HF_TOKEN")


def create_uud_knowledge_base(pdf_path="documents"):
    vector_db = ChromaDb(
        collection="recipes",
        path="cache/chromadb",
        persistent_client=True,
        embedder=SentenceTransformerEmbedder(),
    )
    uud_kb = PDFKnowledgeBase(
        path=pdf_path,
        vector_db=vector_db
    )
    return uud_kb

def create_agent(debug_mode=True):
    uud_kb = create_uud_knowledge_base(pdf_path="documents")
    # uud_kb.load(recreate=False)
    agent = Agent(
        name="law-agent",
        agent_id="law-agent",
        model=Groq(
            id="llama-3.3-70b-versatile",
            temperature=0.2
        ),
        description="Anda adalah seorang ahli hukum. Anda mengetahui seluk beluk hukum Indonesia dan Undang Undang Dasar yang mendasarinya.",
        instructions=[
            "IMPORTANT: Jawablah dengan bahasa Indonesia yang baik dan benar sesuai dengan Kamus Besar Bahasa Indonesia (KBBI)",
            "Pengguna akan memberikan anda suatu kasus yang sedang terjadi. Tolong berikan beberapa hal:",
            "   1. UUD apa saja kah yang terlanggar. Tolong jelaskan secara singkat.",
            "   2. Cara penanganannya bagaimana.",
            "   3. Hukuman apakah yang pengguna akan dapatkan.",
            "Apabila ada nominal uang yang tersangkut atau terlibat pada kasus ini, tolong berikan dalam mata uang Rupiah Indonesia (IDR)."
        ],
        knowledge=uud_kb,
        search_knowledge=True,
        tools=[
            GoogleSearchTools()
        ],
        show_tool_calls=True,
        debug_mode=debug_mode,
        markdown=True,
    )

    return agent
