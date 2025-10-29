import os
import asyncio

from llama_index.core import (
    Settings,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.workflow import Context
from llama_index.core.tools import QueryEngineTool
from llama_index.embeddings.bedrock import BedrockEmbedding
from llama_index.llms.bedrock_converse import BedrockConverse


def initialize_settings():
    """
    Initialize global settings for LlamaIndex.
    This sets up the language model (LLM) and embedding model using Amazon Bedrock.
    """
    # Set the LLM to use Haiku model from Bedrock Converse API (recommended)
    Settings.llm = BedrockConverse(
        model="us.anthropic.claude-haiku-4-5-20251001-v1:0",
        region_name="us-west-2",
    )
    # Set the embedding model to use Amazon's Titan model
    Settings.embed_model = BedrockEmbedding(
        model="amazon.titan-embed-text-v2:0",
        region_name="us-west-2",
    )


def load_or_create_index(file_path, persist_dir):
    """
    Load an existing index from storage or create a new one if it doesn't exist.

    Args:
    file_path (str): Path to the PDF file to index.
    persist_dir (str): Directory to persist the index.

    Returns:
    VectorStoreIndex: The loaded or newly created index.
    """
    if os.path.exists(persist_dir):
        print(f"Loading existing index from {persist_dir}")
        # Load the existing index from the specified directory
        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        return load_index_from_storage(storage_context)
    else:
        print(f"Creating new index from {file_path}")
        # Load documents from the PDF file
        documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
        # Create a new index from the documents
        index = VectorStoreIndex.from_documents(documents)
        # Persist the index to the specified directory
        index.storage_context.persist(persist_dir)
        return index


def create_query_engine_tool(query_engine, name, description):
    """
    Create a QueryEngineTool for use with the ReActAgent.

    Args:
    query_engine: The query engine to use.
    name (str): Name of the tool.
    description (str): Description of the tool.

    Returns:
    QueryEngineTool: A tool that can be used by the ReActAgent.
    """
    return QueryEngineTool.from_defaults(
        query_engine=query_engine,
        name=name,
        description=description,
    )


async def main():
    """
    Main function to orchestrate the index creation/loading and querying process.
    """
    # Initialize LlamaIndex settings
    initialize_settings()

    # Load or create indexes for Lyft and Uber data
    lyft_index = load_or_create_index("./data/10k/lyft_2021.pdf", "./data/lyft_index")
    uber_index = load_or_create_index("./data/10k/uber_2021.pdf", "./data/uber_index")

    # Create query engines from the indexes
    lyft_engine = lyft_index.as_query_engine(similarity_top_k=3)
    uber_engine = uber_index.as_query_engine(similarity_top_k=3)

    # Create query engine tools for the ReActAgent
    query_engine_tools = [
        create_query_engine_tool(
            lyft_engine,
            "lyft_10k",
            "Provides information about Lyft financials for year 2021. "
            "Use a detailed plain text question as input to the tool.",
        ),
        create_query_engine_tool(
            uber_engine,
            "uber_10k",
            "Provides information about Uber financials for year 2021. "
            "Use a detailed plain text question as input to the tool.",
        ),
    ]

    # Create a ReActAgent with the query engine tools
    agent = ReActAgent(
        tools=query_engine_tools,
        llm=Settings.llm,
        verbose=True,
    )

    # Create a context to hold this session/state
    ctx = Context(agent)

    # Use the agent to answer a question
    print("Starting agent query...")
    print("=" * 60)
    handler = agent.run("Compare revenue growth of Uber and Lyft from 2020 to 2021", ctx=ctx)
    response = await handler
    print(str(response))


if __name__ == "__main__":
    asyncio.run(main())
