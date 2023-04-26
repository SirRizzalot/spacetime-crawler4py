import re
from lxml import html
from urllib.parse import urlparse

from utils.download import download
from collections import defaultdict

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



longest_page = {"url":"", "word-count": 0}

def scraper(url:str, resp) -> list:
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

#once url is checked for is_valid added to unqiue_url list with fragment cut off
unqiue_url_list = []
def unique_url(url):
    temp_url = url.split("#")
    if temp_url[0] not in unique_url_list:
        unqiue_url_list += temp_url[0]
    return temp_url[0]


def extract_next_links(url, resp):
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
        line_list = tree.xpath("//p//text()")
        # grabs item within <p> </p>

        words = ' '.join(line_list)
        match = re.findall('[0-9]+|(?:[a-zA-Z0-9]{1,}[a-zA-Z0-9]+(?:\'s|\.d){0,1})', words.lower())
        # regex for including that's and ph.d as it is:
        #                   [0-9]+|(?:[a-zA-Z0-9]{1,}[a-zA-Z0-9]+(?:\'s|\.d){0,1})
        #regext for spliting it:
        #                   [0-9]+|(?:[a-zA-Z0-9]{1,}[a-zA-Z0-9]+)

        # print (append) all words to the txt file for word count later on
        f1 = open("word_list.txt", "a", encoding="UTF-8")
        for each_word in match:
            print(each_word, file=f1)
        f1.close()

        # print(match)

        # update page's word_count to len of word list
        word_count = len(match)
        # if current page's word count > the one in longest_page, update longest_page to wordcount and url of current page
        if word_count > longest_page["word-count"]:
            longest_page["url"] = resp.url
            longest_page["word-count"] = word_count


        return list()
    except:
        print("error")


def report(): 
    # initialize list variables
    # a dictionary for all words found; containing words as key and their frequency as value in a list.
    frequented = defaultdict(int)

    # TOP 50 FREQUENCIES
    # read word_list.txt file and compute word freq, store in frequented dict 
    word_list_read = open("word_list.txt", "r")
    for word in word_list_read: # each line will contain a word
        frequented[word.strip()] += 1
    word_list_read.close()


    # write the top 50 frequent words to analytics-report.txt file
    word_list_write = open("analytics-report.txt", "w", encoding="UTF-8")
    # sort the frequented dict
    sorted_frequented = sorted(frequented.items(), key=lambda x: (-x[1], x[0]))
    # extract the first 50 key-value pairs
    most_common_words = list()
    cur_word = 0
    while len(most_common_words) < 50:
        if sorted_frequented[cur_word][0] not in stop_words:
            most_common_words.append(sorted_frequented[cur_word])
        cur_word+=1
    print("50 MOST COMMON WORDS:", file=word_list_write)
    for (k, v) in most_common_words:
        # sorted will take an average of o(n log n)
        # at worst every word is unique, so we loop in times O(N)
        print(f"{k} -> {v}", file=word_list_write)  # constant
        print(f"{k} -> {v}")
    
    # LONGEST PAGE
    print(f"\nThe longest page's URL: {longest_page['url']}. Word count: {longest_page['word-count']}", file=word_list_write)
    print(f"\nThe longest page's URL: {longest_page['url']}. Word count: {longest_page['word-count']}")


    word_list_write.close()


#black listed sites?


def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    #remove fragement before running through is valid
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