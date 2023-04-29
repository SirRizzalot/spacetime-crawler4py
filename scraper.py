import re
import os
from lxml import html, etree
from urllib.parse import urlparse, urlunparse, urldefrag, urljoin



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
domain_list = [".ics.uci.edu", ".cs.uci.edu", ".informatics.uci.edu", ".stat.uci.edu"]
disallowed_paths = {}
finger_prints = {}


#then parse robots.txt of all domains
for domain in domain_list:
    curl_url = "curl https://www" + domain + "/robots.txt"
    result = os.popen(curl_url).read()
    result_data_set = {"Disallowed":[], "Allowed":[]}
    print(result)
    for line in result.split("\n"):
        if line.startswith('Allow'):    # this is for allowed url
            result_data_set["Allowed"].append(line.split(': ')[1].split(' ')[0])
        elif line.startswith('Disallow'):    # this is for disallowed url
            result_data_set["Disallowed"].append(line.split(': ')[1].split(' ')[0])

    disallowed_paths[domain] = result_data_set

# dictionary to contain subdomains of ics.uci.edu and number of unique pages in that subdomain
subdomain_pages = {}
set_subdomain_pages = set()
discovered_set_pages = set()

def scraper(url:str, resp) -> list:
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def similarity(mod3:{int})->bool:
    for (url, val) in finger_prints.items():
        intersect = mod3.intersection(val)
        union = mod3.union(val)
        similarity = len(intersect) / len(union)
        if similarity == 0:
            return True
    return False

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
    urls = []
    try:
        if resp.status == 200:

            ### content parsing


            html_tree = html.fromstring(resp.raw_response.content)
            line_list = html_tree.xpath("//div//text()")
            # grabs item within <p> </p>

            words = ' '.join(line_list)
            match = re.findall('[0-9]+|(?:[a-zA-Z0-9]{1,}[a-zA-Z0-9]+(?:\'s|\.d){0,1})', words.lower())
            # regex for including that's and ph.d as it is:
            #                   [0-9]+|(?:[a-zA-Z0-9]{1,}[a-zA-Z0-9]+(?:\'s|\.d){0,1})
            # regext for spliting it:
            #                   [0-9]+|(?:[a-zA-Z0-9]{1,}[a-zA-Z0-9]+)

            # print (append) all words to the txt file for word count later on
            f1 = open("word_list.txt", "a", encoding="UTF-8")
            for each_word in match:
                print(each_word, file=f1)
            f1.close()

            f2 = open("word_list2.txt", "a", encoding="UTF-8")
            for each_word in discovered_set_pages:
                print(each_word, file=f2)
            f2.close()

            f3 = open("word_list3.txt", "a", encoding="UTF-8")
            for each_word in set_subdomain_pages:
                print(each_word, file=f3)
            f3.close()



            # using finger-print method to detect similarity
            three_gram = [' '.join(match[i:i + 3]) for i in range(len(match) - 2)]

            three_gram_hash_values = [sum(ord(t) for t in i) for i in three_gram]
            # print("got this far")
            mod3 = {i for i in three_gram_hash_values if i % 4 == 0}

            if similarity(mod3):
                return list()

            finger_prints[url] = mod3





            # update page's word_count to len of word list
            word_count = len(match)
            # if current page's word count > the one in longest_page, update longest_page to wordcount and url of current page
            if word_count > longest_page["word-count"]:
                longest_page["url"] = resp.url
                longest_page["word-count"] = word_count

            ### URL retrieval
            parser = etree.HTMLParser()
            tree = etree.HTML(resp.raw_response.content, parser)
            # tree = etree.parse(StringIO(resp.raw_response.content), root)
            # result = etree.tostring(tree.getroot(), pretty_print=True, method="html")
            # parsed_url = urlparse(etree.tostring(tree))


            # getting only the hyperlinks
            for link in tree.xpath('//a | //img'):
                relative_url = link.get('href') or link.get('src')
                # relativeurl_src = link.get('src')
                # print(relativeurl_src)

                # statement to ignore #
                if relative_url and relative_url.startswith('#'):
                    # print(relative_url)
                    continue

                parsed_url = urlparse(relative_url)

                # converting relative urls to absolute URL
                if parsed_url.netloc == '' and parsed_url.scheme == '':
                    # print(parsed_url)
                    relative_url = url + parsed_url.path
                    parsed_url = urlparse(relative_url)
                    # print(parsed_url)

                # checking to see if hyperlink has required properties of URLs
                if parsed_url.scheme and parsed_url.netloc:
                    # removing fragments from URL
                    defrag, _ = urldefrag(relative_url)
                    if defrag in set_subdomain_pages:
                        continue
                    # looking for subdomains of the domain ics.uci.edu
                    if "ics.uci.edu" in parsed_url.netloc:
                        split_list = parsed_url.netloc.split(".")
                        # print("HERE", split_list, split_list[1] == 'ics', split_list[2] == 'uci', split_list[3] == 'edu')
                        if split_list[1] == 'ics' and split_list[2] == 'uci' and split_list[3] == 'edu':
                            # print(split_list, "TRUE")
                            if defrag not in set_subdomain_pages:
                                if split_list[0] in subdomain_pages:
                                    subdomain_pages[split_list[0]] = subdomain_pages.get(split_list[0]) + 1
                                else:
                                    subdomain_pages[split_list[0]] = 1
                            set_subdomain_pages.add(defrag)
                        # print(defrag, "NETLOC", parsed_url.netloc, "SPLIT", parsed_url.netloc.split(".")[0])
                    urls.append(defrag)

                # converting relative urls to absolute URL
                # if parsed_url.netloc == '' and parsed_url.scheme == '':
                #     # print(parsed_url)
                #     absolute_url = url + parsed_url.path
                #     parsed_url = urlparse(absolute_url)
                #     if "ics.uci.edu" in absolute_url:
                #         print("ABOSLUTEURL", absolute_url,  urlparse(absolute_url))
                #         if absolute_url in subdomain_pages:
                #             subdomain_pages[absolute_url] = subdomain_pages.get(absolute_url) + 1
                #         else:
                #             subdomain_pages[absolute_url] = 1
                #     urls.append(absolute_url)

                # urls.append(relative_url)
            urls = list(dict.fromkeys(urls))
            # print(urls)
            # print(len(urls))
            # print(set_subdomain_pages)
            # subdomain_pages = sorted(subdomain_pages.items(), key = lambda x: (x[1],x[0]))

            # print(subdomain_pages)

            # print(etree.tostring(tree))
            # print("\n\n\n")
            # return urls
            # return list()

            return urls
        else:
            # print(url, resp.error)
            return list()
    except Exception as e:
        print(e)
        print("error")


def report(): 
    #FOR TESTING ONLY!!!!!!!!!!!!!!
    # print(disallowed_paths)

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




def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    if url in discovered_set_pages:
        return False
    else:
        discovered_set_pages.add(url)
    try:
        parsed = urlparse(url)
        domain_name = re.findall(
                r"(?:\.ics\.uci\.edu)|(?:\.cs\.uci\.edu)|(?:\.informatics\.uci\.edu)|(?:\.stat\.uci\.edu)", parsed.netloc)
        if not domain_name:
            return False
        if parsed.path in disallowed_paths[domain_name[0]]["Disallowed"]:
            if parsed.path in disallowed_paths[domain_name[0]]["Allowed"]:
                return True
            return False
        if parsed.scheme not in ["http", "https"]:
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

    except:
        print(parsed)
        raise


if __name__ == "__main__":
    extract_next_links("https://webscraper.io/test-sites/e-commerce/allinone", download("https://webscraper.io/test-sites/e-commerce/allinone"))
