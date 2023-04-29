from urllib.parse import urlparse, urlunparse, urldefrag


if __name__ == '__main__':
    parsed = urlparse('https://www.stat.uci.edu/')
    print(dir(parsed))