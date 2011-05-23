import re
import urllib2
import lxml.html

def read_url(url, until=None, chunk=100):
    try:
        response = urllib2.urlopen(url)
    except urllib2.URLError:
        return u''

    if until:
        next, data, trunk_at = True, '', None
        while next:
            next = response.read(chunk)
            data += next
            until_match = re.search(until, data, re.IGNORECASE)
            if until_match:
                response.close()
                data = unicode(data, 'utf-8')
                return data[:data.find(until) + len(until)]
    else:
        data = response.read()
    return unicode(data, encoding)

d = read_url('http://python.org/', until='</title>')

stringA = str(d)
stringB = "<title>"
stringC = "</title>"

print re.search(re.escape(stringB)+"(.*?)"+re.escape(stringC),stringA).group(1)
