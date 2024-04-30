# -*- coding: utf-8 -*-
"""
@Time ： 2024/2/29 11:19
@Auth ： Juexiao Zhou
@File ：build_RAG.py
@IDE ：PyCharm
@Page: www.joshuachou.ink
"""

import os.path
import os
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    Settings
)
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def preload_retriever(local_engine = True, openai = None, PERSIST_DIR = "../softwares_database_RAG", SOURCE_DIR = "../softwares_database"):
    if not local_engine:
        os.environ['OPENAI_API_KEY'] = openai
        Settings.embed_model = OpenAIEmbedding()
    else:
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5"
        )

    if not os.path.exists(PERSIST_DIR):
        # load the documents and create the index
        documents = SimpleDirectoryReader(SOURCE_DIR).load_data()
        index = VectorStoreIndex.from_documents(documents, embeddings=Settings.embed_model)
        # store it for later
        index.storage_context.persist(persist_dir=PERSIST_DIR)
    else:
        # load the existing index
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)

    # Either way we can now query the index
    retriever = index.as_retriever(similarity_top_k=1)
    return retriever

def retrive(retriever,
            retriever_prompt="To perform RNA-seq alignment, what tools and parameters should I use?"
):
    response = retriever.retrieve(retriever_prompt)
    response = response[0].get_text()
    return response

if __name__ == '__main__':
    local_engine = True
    openai = 'sk-xxx'
    retriever = preload_retriever(local_engine, openai)
    response = retrive(retriever)
    print(response)