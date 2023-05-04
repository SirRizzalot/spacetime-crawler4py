import re
import os
from lxml import html, etree
from urllib.parse import urlparse, urlunparse, urldefrag, urljoin
import time


from utils.download import download
from collections import defaultdict, Counter

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
bot_name = "robot"  # bot name (to check on robots.txt file)


#then parse robots.txt of all domains
for domain in domain_list:
    curl_url = "curl https://www" + domain + "/robots.txt"
    result = os.popen(curl_url).read()
    result_data_set = {"Disallowed":[], "Allowed":[]}
    useragent_list = {}

    # if there is our bot, slice result to that block only
    if "User-agent: " + bot_name in result:
        # substring of result, from User-agent: bot_name until the end of that section (empty line)
        result = result[result.find("User-agent: " + bot_name): result.find("\n\n", result.find("User-agent: " + bot_name))]
    else:
        # substring of result, from User-agent: * until the end of that section (empty line)
        result = result[result.find("User-agent: *"): result.find("\n\n", result.find("User-agent: *"))]
    for line in result.split("\n"):
        if line.startswith('Allow'):    # this is for allowed url
            result_data_set["Allowed"].append(line.split(': ')[1].split(' ')[0])
        elif line.startswith('Disallow'):    # this is for disallowed url
            result_data_set["Disallowed"].append(line.split(': ')[1].split(' ')[0])

    disallowed_paths[domain] = result_data_set
    time.sleep(0.5)
    #politeness


# dictionary to contain subdomains of ics.uci.edu and number of unique pages in that subdomain
subdomain_pages = {}
set_subdomain_pages = set()
discovered_set_pages = set()

# receives url and parses through before returning valid urls scrapped from page to continue crawling towards
def scraper(url:str, resp) -> list:
    links = extract_next_links(url, resp)
    valid_links = [link for link in links if is_valid(link)]

    valid_urls = open("valid_urls.txt", "a", encoding="UTF-8")
    # writing all valid urls into a file
    for i in valid_links:
        print(i, file=valid_urls)
    valid_urls.close()

    return valid_links

# similarity based on fingerprint method
def similarity(mod3:{int})->bool:
    for (url, val) in finger_prints.items():
        intersect = mod3.intersection(val)
        union = mod3.union(val)
        similarity = len(intersect) / len(union)
        if similarity == 1:
            return True
    return False



# function to determine which urls to scrape
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
    # handling case where response is none
    if resp.raw_response is None or resp is None:
        word = f'{{"url": "{url}", "content": {{"error": "resp.raw_response is none or resp is none", "status": -1, "word_count": -1, "word": [], "raw_response.content": []}}}},'
        f5 = open("all_web.json", "a", encoding="UTF-8")
        print(word, file=f5)
        f5.close()
        return list()

    try:
        # handling case where status code of url is 300s or redirect
        if resp.status == 301 or resp.status == 302:
            word = f'{{"url": "{url}", "content": {{"error": "redirect", , "status": {resp.status}, "word_count": -1, "word": [] , "raw_response.content": []}}}}, '
            f5 = open("all_web.json", "a", encoding="UTF-8")
            print(word, file=f5)
            f5.close()
            if url in finger_prints.keys():
                return list()
            urls.append(resp.raw_response.url)
            return urls

        # parses through url if status is 200
        if resp.status == 200:
            if url in finger_prints.keys():
                return list()
            ### content parsing
            html_tree = html.fromstring(resp.raw_response.content)
            line_list = html_tree.xpath('//body//*[not(self::script or self::style)]/text()')

            # grabs item within <p> </p>
            words = ' '.join(line_list)
            match = re.findall('[0-9]+|(?:[a-zA-Z0-9]{1,}[a-zA-Z0-9]+(?:\'s|\.d){0,1})', words.lower())

            try:
                word_list = [f'"{w}"' for w in match]  # Add double quotes around each element in match
                line_list_quoted = [f'"{w}"' for w in line_list]  # Add double quotes around each element in line_list
                word = '{{"url": "{url}", "content": {{"error": "Probably None", "status": {status}, "word_count": {count}, "word": [{words}], "raw_response.content": [{lines}]}}}},'.format(
                    url=url, status=resp.status, count=len(match), words=", ".join(word_list),
                    lines=", ".join(line_list_quoted))
                f5 = open("all_web.json", "a", encoding="UTF-8")
                print(word, file=f5)
                f5.close()
            except:
                word = f'{{"url": "{url}", "content": {{"error": "Probably None", "status": {resp.status}, "word_count": {len(match)}, "word": [], "raw_response.content": []}}}},'
                f5 = open("all_web.json", "a", encoding="UTF-8")
                print(word, file=f5)
                f5.close()

            if len(match) > 0 and match != ['exif', 'ii', 'ducky']:
                # using finger-print method to detect similarity
                three_gram = [' '.join(match[i:i + 3]) for i in range(len(match) - 2)]
                three_gram_hash_values = [sum(ord(t) for t in i) for i in three_gram]

                mod3 = {i for i in three_gram_hash_values if i % 4 == 0 or i % 5 == 0}
                if len(mod3) != 0:
                    if similarity(mod3):
                        return list()

                    # update page's word_count to len of word list
                    word_count = len(match)
                    # if current page's word count > the one in longest_page, update longest_page to wordcount and url of current page
                    if word_count > longest_page["word-count"]:
                        longest_page["url"] = resp.url
                        longest_page["word-count"] = word_count

                finger_prints[url] = mod3

            ### URL retrieval
            parser = etree.HTMLParser()
            tree = etree.HTML(resp.raw_response.content, parser)

            f1 = open("word_list.txt", "a", encoding="UTF-8")
            for each_word in match:
                print(each_word, file=f1)
            f1.close()

            # getting only the hyperlinks from url
            for link in tree.xpath('//a | //img'):
                relative_url = link.get('href') or link.get('src')

                # statement to ignore urls that are #
                if relative_url and relative_url.startswith('#'):
                    continue
                parsed_url = urlparse(relative_url)

                # converting relative urls to absolute URL
                if parsed_url.netloc == '' and parsed_url.scheme == '':
                    parsed_url = urlparse(url)
                    net_loc = parsed_url.netloc
                    relative_url = net_loc + parsed_url.path
                    parsed_url = urlparse(relative_url)

                # checking to see if hyperlink has required properties of URLs
                if parsed_url.scheme and parsed_url.netloc:
                    # removing fragments from URL
                    defrag, _ = urldefrag(relative_url)
                    if defrag in set_subdomain_pages:
                        continue
                    # looking for subdomains of the domain ics.uci.edu
                    if "ics.uci.edu" in parsed_url.netloc:
                        split_list = parsed_url.netloc.split(".")
                        if split_list[1] == 'ics' and split_list[2] == 'uci' and split_list[3] == 'edu':

                            if defrag not in set_subdomain_pages:
                                # adding subdomains to a dictionary
                                if split_list[0] in subdomain_pages:
                                    subdomain_pages[split_list[0]] = subdomain_pages.get(split_list[0]) + 1
                                else:
                                    subdomain_pages[split_list[0]] = 1
                            set_subdomain_pages.add(defrag)

                            f3 = open("word_list3.txt", "a", encoding="UTF-8")
                            print(defrag, file=f3)
                            f3.close()
                    urls.append(defrag)
            urls = list(dict.fromkeys(urls))

            try:
                tag_parser = etree.HTMLParser()
                tag_tree = etree.HTML(resp.raw_response.content, tag_parser)
                # counting the number of tags in the hmtl file of the url
                num_tags = Counter()
                num_tags.update(x.tag for x in tag_tree.iter())
                sum_tags = sum(num_tags.values())

                f1 = open("url_tag_word.txt", "a", encoding="UTF-8")
                print(f'"{url}", {sum_tags}, {len(match)}', file=f1)
                f1.close()
            except etree.Error as e:
                word = f'{{"url": "{url}", "content": {{"error_at_tag": "etree error", "status": 200, "word_count": -1, "word": [], "raw_response.content": []}}}}, '
                f5 = open("all_web.json", "a", encoding="UTF-8")
                print(word, file=f5)
                f5.close()
            except Exception as e:
                word = f'{{"url": "{url}", "content": {{"error_at_tag": "{e}", "status": 200, "word_count": -1, "word": [], "raw_response.content": []}}}}, '
                f5 = open("all_web.json", "a", encoding="UTF-8")
                print(word, file=f5)
                f5.close()

            return urls
        # else statement for if the status of url isn't 200
        else:
            word = f'{{"url": "{url}", "content": {{"error": "other status code", "status": {resp.status}, "word_count": -1, "word": [], "raw_response.content": []}}}}, '
            f5 = open("all_web.json", "a", encoding="UTF-8")
            print(word, file=f5)
            f5.close()
            return list()
    # catching and handling etree.Error error
    except etree.Error as e:
        word = f'{{"url": "{url}", "content": {{"error": "etree error", "status": 200, "word_count": -1, "word": [], "raw_response.content": []}}}}, '
        f5 = open("all_web.json", "a", encoding="UTF-8")
        print(word, file=f5)
        f5.close()
        return list()
    # catching and handling Exception error
    except Exception as e:
        word = f'{{"url": "{url}", "content": {{"error": "{e}", "status": 200, "word_count": -1, "word": [], "raw_response.content": []}}}}, '
        f5 = open("all_web.json", "a", encoding="UTF-8")
        print(word, file=f5)
        f5.close()
        return list()

# function to handle all data collected and put them into a file to obtain the information to write the report
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
    while len(most_common_words) < 50 and len(sorted_frequented) != 0:
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

    all_unique = open("valid_urls.txt", "r")
    valid_unique = open("all_links_found.txt", "r")
    print(f"\nAll unique found: {sum([1 for i in all_unique])}. All unique valid found: {sum([1 for i in valid_unique])}", file=word_list_write)

    all_unique.close()
    valid_unique.close()

    # adding all the subdomains of ics.uci.edu and the number of unique pages in that subdomain into a file
    f7 = open("subdomains_ics_uci_edu.txt", "a", encoding="UTF-8")
    for i, j in sorted(subdomain_pages.items()):
        url = "https://" + i + ".ics.uci.edu/"
        word = url + " , " + str(j)
        print(word, file=f7)
    f7.close()

    word_list_write.close()

# function to determine if url is valid to crawl
def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    # adding urls into file to obtain all urls discovered(the url may or may not be valid)
    if url in discovered_set_pages:
        return False
    else:
        discovered_set_pages.add(url)
        f2 = open("all_links_found.txt", "a", encoding="UTF-8")
        # for each_word in discovered_set_pages:
        print(url, file=f2)
        f2.close()
    try:
        # parsing through url to determine where they are in the right domain
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

        # checking to see if url has a file extension for a html file
        if re.match(r".*\.(css|js|bmp|gif|jpe?g|ico|png|tiff?|mid|mp2|mp3|mp4|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf|ppsx|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1|thmx|mso|arff|rtf|jar|csv|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.query.lower()):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico|png|tiff?|mid|mp2|mp3|mp4|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf|ppsx|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1|thmx|mso|arff|rtf|jar|csv|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except:
        print(parsed)
        raise


if __name__ == "__main__":
    extract_next_links("https://webscraper.io/test-sites/e-commerce/allinone", download("https://webscraper.io/test-sites/e-commerce/allinone"))
