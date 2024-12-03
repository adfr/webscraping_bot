# Importing necessary libraries
import requests
from bs4 import BeautifulSoup
import chromadb
from urllib.parse import urljoin, urlparse
import re

# Initialize ChromaDB client
#chroma_client = chromadb.Client()
chroma_client = chromadb.PersistentClient(path="cdb.db")



def is_valid_url(url, base_domain):
    """Check if URL is valid and belongs to same domain"""
    parsed = urlparse(url)
    return bool(parsed.netloc) and parsed.netloc == base_domain

def scrape_page(url):
    """Scrape content from a single page"""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Get text content
        text = soup.get_text()
        # Clean text
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    except:
        return ""

def crawl_website(start_url,collection_name):
    """Crawl website and index content"""
    collections = chroma_client.list_collections()
    if any(collection.name == collection_name for collection in collections):
        print("db exist")
    else:
        collection = chroma_client.create_collection(name=collection_name)
    base_domain = urlparse(start_url).netloc
    visited_urls = set()
    urls_to_visit = {start_url}
    
    while urls_to_visit:
        current_url = urls_to_visit.pop()
        
        if current_url in visited_urls:
            continue
            
        print(f"Scraping: {current_url}")
        visited_urls.add(current_url)
        
        # Get page content
        try:
            response = requests.get(current_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Index the page content
            content = scrape_page(current_url)
            if content:
                collection.add(
                    documents=[content],
                    metadatas=[{"url": current_url}],
                    ids=[str(len(visited_urls))]
                )
            
            # Find all links on the page
            for link in soup.find_all('a', href=True):
                url = urljoin(current_url, link['href'])
                if is_valid_url(url, base_domain) and url not in visited_urls:
                    urls_to_visit.add(url)
                    
        except Exception as e:
            print(f"Error scraping {current_url}: {str(e)}")
            continue

if __name__ == "__main__":
    print("Please run through the Streamlit interface")
