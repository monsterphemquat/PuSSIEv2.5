import requests
import xml.etree.ElementTree as ET
import urllib.parse
import re
from collections import Counter

# Function to search for articles
def search_articles(query):
    query_encoded = urllib.parse.quote(query)
    search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query_encoded}&retmax=10"
    search_response = requests.get(search_url)
    
    if search_response.status_code == 200:
        search_root = ET.fromstring(search_response.content)
        ids = [id_elem.text for id_elem in search_root.findall(".//Id")]
        return ids
    else:
        print("Error with the search request")
        return []

# Function to fetch article details
def fetch_article_details(ids):
    ids_str = ",".join(ids)
    fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={ids_str}&retmode=xml&idtype=acc"
    fetch_response = requests.get(fetch_url)
    
    if fetch_response.status_code == 200:
        fetch_root = ET.fromstring(fetch_response.content)
        articles = []
        
        for article in fetch_root.findall(".//PubmedArticle"):
            title = article.find(".//ArticleTitle").text
            journal = article.find(".//Journal/Title").text
            year = article.find(".//PubDate/Year").text or "n.d."
            authors = ", ".join([author.find("LastName").text + " " + (author.find("Initials").text or "") for author in article.findall(".//Author") if author.find("LastName") is not None])
            citation = f"{authors} ({year}). {title}. *{journal}*."
            link = f"https://pubmed.ncbi.nlm.nih.gov/{article.find('.//PMID').text}/"
            articles.append((title, citation, link))
        
        return articles
    else:
        print("Error with the fetch request")
        return []

# Function to suggest related keywords based on term frequency
def suggest_keywords(articles):
    all_titles = " ".join(article[0] for article in articles)
    words = re.findall(r'\b\w+\b', all_titles.lower())
    common_words = Counter(words).most_common()
    
    # Filter out common stopwords and single-character words
    stopwords = {'and', 'the', 'of', 'in', 'for', 'on', 'with', 'a', 'to', 'is', 'by', 'an', 'as', 'or', 'at', 'from', 'that', 'this'}
    keywords = [word for word, _ in common_words if word not in stopwords and len(word) > 1]
    
    return keywords[:5]  # Return the top 5 keywords

# Function to save articles to a text file
def save_articles_to_file(articles, filename="articles.txt"):
    with open(filename, "w") as file:
        for title, citation, link in articles:
            file.write(f"Title: {title}\n")
            file.write(f"Citation: {citation}\n")
            file.write(f"Link: {link}\n\n")
    print(f"Articles saved to {filename}")

# Main program
def main():
    print("Welcome to Pubmed Source Sorting, Indexing, and Exporting :)")

    while True:
        query = input("Enter your search query: ")
        ids = search_articles(query)
        
        if ids:
            articles = fetch_article_details(ids)
            
            if articles:
                print("\nArticles found:")
                for title, citation, link in articles:
                    print(f"Title: {title}")
                    print(f"Citation: {citation}")
                    print(f"Link: {link}\n")
                
                save_articles_to_file(articles)
                
                # Show metrics
                print(f"\nNumber of results found: {len(ids)}")
                print(f"Number of articles saved: {len(articles)}")
                
                # Suggest related keywords
                print("\nRelated keywords:")
                suggestions = suggest_keywords(articles)
                for suggestion in suggestions:
                    print(f"- {suggestion}")
                
            else:
                print("No articles found")
        else:
            print("No articles found")
        
        more_queries = input("\nDo you want to perform another search? (yes/no): ")
        if more_queries.lower() != "yes":
            break

    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
