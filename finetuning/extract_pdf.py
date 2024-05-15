# Refer to LangChain docs https://python.langchain.com/v0.1/docs/use_cases/question_answering/quickstart/#indexing-split
# and  video tutorial: https://www.youtube.com/watch?v=tcqEUSNCn8I&t=423s

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain import hub

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Load data from PDF and split it into chunks
loader = PyPDFLoader("data/text/Materials_and_Interior_Design.pdf",extract_images=True)
splits = loader.load_and_split()

# Embed data chunks and store them in a vectorstore
vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())

# Initiate a retriever from the vectorstore
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 6})

# Let's test retrieving some documents based on a query
# retrieved_docs = retriever.invoke("What are good cheap and sustainable materials?")
# print(len(retrieved_docs))
# print(retrieved_docs[0].page_content)

# Now, let's use an LLM to generate a response to the query, based on the retrieved documents
llm = ChatOpenAI(model="gpt-3.5-turbo-16k-0613")
prompt = hub.pull("rlm/rag-prompt")
example_messages = prompt.invoke(
    {"context": "filler context", "question": "filler question"}
).to_messages()



def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

for chunk in rag_chain.stream("What are good cheap and sustainable materials?"):
    print(chunk, end="", flush=True)