# 1) Monkey-patch torch.Module.to to fall back to to_empty() on meta-tensor errors
import torch
from torch.nn.modules.module import Module as _TorchModule
_orig_to = _TorchModule.to
def _safe_to(self, *args, **kwargs):
    try:
        return _orig_to(self, *args, **kwargs)
    except NotImplementedError as e:
        if "Cannot copy out of meta tensor" in str(e):
            # allocate real storage and move
            return self.to_empty(*args, **kwargs)
        raise
_TorchModule.to = _safe_to  # now all Module.to() calls will handle meta tensors :contentReference[oaicite:0]{index=0}

# 2) Disable Streamlit’s file watcher so it won’t introspect torch.classes
import os
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"  

from agno.agent import Agent
from agno.models.groq import Groq
from agno.models.openai import OpenAIChat
from agno.tools.googlesearch import GoogleSearchTools
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.pgvector import PgVector

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
from agno.vectordb.chroma import ChromaDb

from agno.embedder.sentence_transformer import SentenceTransformerEmbedder
from agno.document.chunking.semantic import SemanticChunking

from dotenv import load_dotenv

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
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
        vector_db=vector_db,
    )
    return uud_kb

def create_agent(debug_mode=True):
    uud_kb = create_uud_knowledge_base(pdf_path="documents")
    uud_kb.load(recreate=False)
    agent = Agent(
        name="law-agent",
        agent_id="law-agent",
        # UNCOMMENT when using Groq
        model=Groq(
            id="llama-3.3-70b-versatile",
            temperature=0.2
        ),
        # UNCOMMENT when using OpenAI
        # model=OpenAIChat(
        #     id="gpt-4o",
        #     response_format="json",
        #     temperature=0.2,
        #     top_p=0.2,
        # ),
        description="Anda adalah seorang ahli hukum. Anda mengetahui seluk beluk hukum Indonesia dan Undang Undang Dasar yang mendasarinya.",
        instructions=[
            "IMPORTANT: Jawablah dengan bahasa Indonesia yang baik dan benar sesuai dengan Kamus Besar Bahasa Indonesia (KBBI)",
            "DILARANG Halusinasi. Gunakan dokumen-dokumen yang ada di knowledge-base atau carilah melalui Google.",
            "Pengguna akan memberikan anda suatu kasus yang sedang terjadi. Tolong berikan beberapa hal:",
            "   1. Peraturan apa saja kah yang terlanggar. Tolong jelaskan secara singkat.",
            "   2. Cara penanganannya bagaimana.",
            "   3. Hukuman apakah yang pengguna akan dapatkan.",
            "Apabila ada nominal uang yang tersangkut atau terlibat pada kasus ini, tolong berikan dalam mata uang Rupiah Indonesia (IDR)."
            # "Jawablah pertanyaan pengguna dengan baik dan jujur."
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
