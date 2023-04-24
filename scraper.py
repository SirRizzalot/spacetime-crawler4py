import re
from lxml import html
from urllib.parse import urlparse

from utils.download import download
from collections import defaultdict

# global variable - a mutual dictionary for all words found
# containing words as key and their frequency as value in a list.
frequented = defaultdict(int)

def computeWordFrequencies(tokenized_text: list, frequented) -> dict:
    for k in tokenized_text:
        frequented[k] += 1
    return frequented  # constant


def scraper(url:str, resp) -> list:
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    stop_words = ["a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", 
                "are", "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", 
                "both", "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", 
                "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", 
                "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", 
                "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", 
                "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", 
                "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", 
                "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", 
                "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", 
                "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", 
                "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", 
                "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", 
                "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", 
                "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", 
                "your", "yours", "yourself", "yourselves"]
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    try:
        tree = html.fromstring(resp.raw_response.content)
        # tree = etree.parse(StringIO(resp.raw_response.content), root)
        # result = etree.tostring(tree.getroot(), pretty_print=True, method="html")
        line_list = tree.xpath("//text()")
        # grabs all the text on the website
        # ++could use improvement as to which body to grab from

        words = ' '.join(line_list)
        match = re.findall('[a-zA-Z0-9]+', words.lower())
        word = [word for word in match if not word in stop_words]
        print(word)
        # basically the same functionality as project1 tokenize

        computeWordFrequencies(word, frequented)

        report()
        print("\n\n\n")
        return list()
    except:
        print("error")


def report(): 
    # Print out the top 50 frequent words
    f1 = open("analytics-report.txt", "w", encoding="UTF-8")
    # sort the frequented dict
    sorted_frequented = dict(sorted(frequented.items(), key=lambda x: (-x[1], x[0])))
    # extract the first 50 key-value pairs
    most_common_words = dict(list(sorted_frequented.items())[0: 50])
    
    
    for (k, v) in most_common_words.items():
        # sorted will take an average of o(n log n)
        # at worst every word is unique, so we loop in times O(N)
        print(f"{k} -> {v}", file=f1)  # constant
    f1.close()


def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)

        if parsed.scheme not in set(["http", "https"]):
            return False
        if not re.match(
                r"[.+(\.ics\.uci\.edu)|(\.cs\.uci\.edu)|(\.informatics\.uci\.edu)|(\.stat\.uci\.edu).+(\#]", parsed):
            return False
        #  url = https://www.ics.uci.edu
        # hostname = www.ics.cui.edu
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise


if __name__ == "__main__":
    extract_next_links("https://webscraper.io/test-sites/e-commerce/allinone", download("https://webscraper.io/test-sites/e-commerce/allinone"))