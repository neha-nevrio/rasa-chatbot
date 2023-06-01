from llama_index import SimpleDirectoryReader, GPTListIndex, GPTVectorStoreIndex, LLMPredictor, PromptHelper, \
    ServiceContext, StorageContext, load_index_from_storage
from langchain import OpenAI


import os

os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")


def create_index(path):
    max_input = 4096
    tokens = 256
    chunk_size = 600
    max_chunk_overlap = 20

    prompt_helper = PromptHelper(max_input, tokens, max_chunk_overlap, chunk_size_limit=chunk_size)

    # define LLM
    llmPredictor = LLMPredictor(llm=OpenAI(temperature=0, model_name="text-ada-001", max_tokens=tokens))

    docs = SimpleDirectoryReader(os.getenv('DOCUMENTS_PATH')).load_data()

    service_context = ServiceContext.from_defaults(llm_predictor=llmPredictor, prompt_helper=prompt_helper)

    vectorIndex = GPTVectorStoreIndex.from_documents(documents=docs, service_context=service_context)

    vectorIndex.storage_context.persist(persist_dir='Store')


create_index(os.getenv('OPENAI_MODEL_INDEX_PATH'))
