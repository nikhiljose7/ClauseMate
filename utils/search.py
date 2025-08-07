from tavily import TavilyClient
from config.config import TAVILY_API_KEY
import logging

def live_web_search(query):
    """
    Perform a live web search using Tavily API.
    """
    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        # The search method returns a dictionary, and the actual results
        # are in a list under the 'results' key.
        response = client.search(query, max_results=3)
        
        # Safely get the list of results
        results_list = response.get('results', [])
        
        if not results_list:
            logging.warning("Tavily search returned no results.")
            return "No information could be found from a web search."
            
        return "\n".join([r.get('content', '') for r in results_list])

    except Exception as e:
        logging.error(f"Tavily search failed: {e}", exc_info=True)
        return "Sorry, the live web search failed. Please check the API key and service status."
