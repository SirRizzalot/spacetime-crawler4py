import re
from lxml import etree
from io import StringIO
from urllib.parse import urlparse, urlunparse, urldefrag, urljoin


from utils.download import download

# dictionary to contain subdomains of ics.uci.edu and number of unique pages in that subdomain
subdomain_pages = {}
unique_urls = list()

def scraper(url:str, resp) -> list:
    links = extract_next_links(url, resp)
    # print([is_valid(link) for link in links])
    #print(len(links))
    if len(links) > 0:
        print("UU ", unique_urls)
        return [link for link in links if is_valid(link)]
    
    return links


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
    urls = list()
    try:
        # crawling URL only if status code is 200
        if resp.status == 200:
            # parsing website
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
                # if url == 'https://www.ics.uci.edu':
                #     print(relative_url, "HERE", parsed_url.netloc, "PARSED", parsed_url)
                # checking to see if hyperlink has required properties of URLs
                #if parsed_url.scheme and parsed_url.netloc:
                    # removing fragments from URL
                    
                #    urls.append(defrag)
                # converting relative urls to absolute URL
                #if parsed_url.netloc == '':
                #print("url ", url + " parsed_url ", parsed_url.path)
                absolute_url = url + parsed_url.path
                absolute_url, _ = urldefrag(absolute_url)
                #print("AU ", absolute_url)
                urls.append(absolute_url)


                # urls.append(relative_url)
            urls = list(dict.fromkeys(urls))
            #print("URLS ", urls)
            #print(len(urls))

            # print(etree.tostring(tree))
            print("\n\n\n")
            # return urls
            #return list()
            return urls
        else:
            print(url, resp.error)
            return list()
    except:
        print("TRIGGERED", url, resp.status)
        return list()



def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        
        parsed = urlparse(url)
        if url not in unique_urls:
            unique_urls.append(url)
        else:
            return False
        if parsed.scheme not in set(["http", "https"]):
            return False
        if not re.match(
                r".+[(\.ics\.uci\.edu)|(\.cs\.uci\.edu)|(\.informatics\.uci\.edu)|(\.stat\.uci\.edu)]", parsed.netloc):
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
    #print("UNIQUE_URLS", unique_urls)