import re
from lxml import html
from urllib.parse import urlparse

from utils.download import download


def scraper(url:str, resp) -> list:
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

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
        # tree = etree.parse(StringIO(resp.raw_response.content), root)
        # result = etree.tostring(tree.getroot(), pretty_print=True, method="html")
        line_list = tree.xpath("//text()")
        # grabs all the text on the website
        # ++could use improvement as to which body to grab from

        words = ' '.join(line_list)
        print(re.findall('[a-zA-Z0-9]+[^((\\n|\\t)*)]', words))
        # basically the same functionality as project1 tokenize

        print("\n\n\n")
        return list()
    except:
        print("error")



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