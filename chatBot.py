# -*- coding: utf-8 -*-
"""leadenhall_analytics.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15Jw_V_FjlvHrw61IhLabkbf3jr8l06Fq
"""

from flask import Flask,render_template, request, jsonify
from dotenv import load_dotenv
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
from langchain.document_loaders.parsers import OpenAIWhisperParser
from langchain.text_splitter import CharacterTextSplitter
import pandas as pd
load_dotenv()
import os
os.environ["OPENAI_API_KEY"] = "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"
def get_chunks(Data):
      titles=Data.columns
      Data = Data.map(lambda x: x.strip() if isinstance(x, str) else x)
      text_data = Data.to_string(index=False)
      text = "".join(text_data)
      document = 'Ω' + text
      for title in titles:
          document = document.replace(title, 'Ω' + title)
      chunk=document.split('Ω')[1:]
      return chunk
def load_data(path1,path2):
    df1 = pd.read_excel(path1)
    df2 = pd.read_excel(path2)
    embeddings = HuggingFaceEmbeddings()
    chunk1=get_chunks(df1)
    chunk2=get_chunks(df2)
    kb1=FAISS.from_texts(chunk1, embeddings)
    kb2=FAISS.from_texts(chunk2, embeddings)
    kb1.merge_from(kb2)
    return kb1
knowledge_base=load_data('Dashboard_Data.xlsx','Dashboard_Data2.xlsx')
llm = ChatOpenAI(model_name="gpt-3.5-turbo-1106")
qa_chain = load_qa_chain(llm, chain_type='stuff')
def get_response(query):
    system_message = '''You are a financial analyst, Answer based on the context in the most detail as possible. YOU MUST provide the statistic or the inference that is needed '''
    input_message= f"{system_message}\n\n User: {query}"
    docs = knowledge_base.similarity_search(input_message)
    with get_openai_callback() as cost:
        response = qa_chain.run(input_documents= docs, question=input_message)
        return response
    return "I am sorry, try again"    
app=Flask(__name__)

@app.get("/") 
def index_get():
    return render_template("base.html")
@app.post("/predict")
def predict():
    text = request.get_json().get("message")
    response= get_response(text)
    message ={"answer" : response}
    return jsonify(message)

if __name__ == "__main__":
    app.run(debug=True)
