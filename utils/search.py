from tavily import TavilyClient
from config.config import TAVILY_API_KEY

def live_web_search(query):
    """
    Perform a live web search using Tavily API.
    """
    client = TavilyClient(api_key=TAVILY_API_KEY)
    results = client.search(query, max_results=3)
    return "\n".join([r['content'] for r in results])
