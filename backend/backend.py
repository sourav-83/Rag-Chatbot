from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
import os
from langchain_community.document_loaders import TextLoader
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


# uvicorn backend.backend:app --reload

class QuestionInput(BaseModel):
    question: str

app = FastAPI()

os.environ["GOOGLE_API_KEY"] = "I'm not sharing my API key with you :)"


DOCS_FOLDER = os.path.join(os.path.dirname(__file__), "..", "docs")
docs = []
for filename in os.listdir(DOCS_FOLDER):
    if filename.endswith(".txt"):
        file_path = os.path.join(DOCS_FOLDER, filename)
        loader = TextLoader(file_path, encoding='utf-8')
        docs.extend(loader.load())



splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents(docs)



embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vector_store = Chroma.from_documents(chunks, embeddings)


retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})
model = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")



prompt = PromptTemplate(
    template="""
    You are a helpful assistant.
    Answer ONLY from the provided transcript context.
    If the context is insufficient, just say you don't know.
    If the question is in Bengali then answer in Bengali.
    You are a RAG chatbot.So, don't mention any term like 'provided text'.

    {context}
    Question: {question}
    """,
    input_variables=['context', 'question']
)

@app.post("/main")
def response_generator(input: QuestionInput):
    question = input.question
    
    

    if not question:
        return JSONResponse(status_code=400, content={"error": "No question provided."})

    retrieved_docs = retriever.get_relevant_documents(question)
    context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
    final_prompt = prompt.format(context=context_text, question=question)
    answer = model.invoke(final_prompt)

    return JSONResponse(status_code=200, content={'answer': str(answer.content)})
