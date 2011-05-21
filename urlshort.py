#!/usr/bin/python

import web
import re
import shelve
import hashlib
import base64
from random import choice

SHELVE_FILENAME =  'shelfshorturl.bg'
SERVICE_URL = "http://localhost:8080"
ADMIN = '/g'
PREFIXDEF = 'g' 
LENGTH = 4
STATIC_DIR = "/static"

urls = (
    "/",                "Home",
    ADMIN +"/done/(.*)", "AdminDone",
    ADMIN,              "Admin",
    "/favicon.ico",     "Favicon",
    ADMIN +"/api",           "GET_API",
    "/gs(.*)",            "RedirectToOthers",
    "/g([0-9].*)",           "Trac"
)


#Messages
HOME_MESSAGE = '''Welcome to URL shortenner. 
		/admin to get controls'''
FAIL_MESSAGE = 'Redirection failed, verify your link...'  # Messages

app = web.application(urls, globals())

# Forms a hash of the url and appends the short code with a predefined character.
def random_shortcut(mylink, length=5):
    hashed = hashlib.sha256()
    hashed.update(mylink)
    encoded_base64 = base64.b64encode(hashed.hexdigest(),"ym")
    encoded_short = encoded_base64[:LENGTH]
    return encoded_short

def prepend_http_if_required(link):
    if (re.match("(^)https://", link, re.IGNORECASE)):
	return link
    elif not (re.match("(^)http://", link, re.IGNORECASE)):
        link = "http://" + link
    return link

class Home:
    def GET(self):
	web.header("Content-Type","text/html; charset=utf-8")
        return HOME_MESSAGE

class Trac:
    def GET(self, number):
	print "got a number"
        return "Whatever you want to do with nummeric's"

class Favicon:
    def GET(self):
	print "trying to return favicon"
        return web.seeother(STATIC_DIR + "/favicon.ico")

class RedirectToOthers:
    def GET(self, short_name):
        storage = shelve.open(SHELVE_FILENAME)                 
        short_name = str(short_name) # shelve does not allow unicode keys
        if storage.has_key(short_name):
            response = web.redirect(storage[short_name])
        else:
            response = FAIL_MESSAGE
        storage.close() 
        return response  

class Admin:
    def GET(self):
	web.header("Content-Type","text/html; charset=utf-8")
        admin_form = web.form.Form(
            web.form.Textbox("url",     description="Long URL"),
            web.form.Textbox("shortcut",description="(optional) Your own short word"),
        )
        admin_template = web.template.Template("""$def with(form)
        <!DOCTYPE HTML>
        <html lang="en">
          <head>
            <meta charset=utf-8>
            <title>URL shortener administration</title>
          </head>
          <body onload="document.getElementById('url').focus()">
            <header><h1>Admin</h1></header>
            <form method="POST" action=/g>
              $:form.render()
              <input type="submit" value="Shorten this long URL">
            </form>
          </body>
        </html>
        """)
        return admin_template(admin_form())

    def POST(self):
        data = web.input()
        data.url = prepend_http_if_required(data.url)
	if str(data.shortcut):
		data.shortcut = "g/" + str(data.shortcut)
        shortcut = str(data.shortcut) or random_shortcut(data.url)
        storage = shelve.open(SHELVE_FILENAME)
        if not data.url:
            response = web.badrequest()
        elif storage.has_key(shortcut):
            response = web.seeother(ADMIN+'/done/'+shortcut)
	else :
            storage[shortcut] = data.url
            response = web.seeother(SERVICE_URL+ADMIN+'/done/'+shortcut)
        storage.close()
        return response

class GET_API:
    def GET(self):
	variables = web.input()
	if 'url' in variables:
		long_url = variables.url
	else:
		return "No URL Specified"
	web.header("Content-Type","text/html; charset=utf-8")
        long_url = prepend_http_if_required(long_url)
        short_url = random_shortcut(long_url)
	if 'title' in variables:
		title = variables.title
		uniqueTitle = short_url + title
        storage = shelve.open(SHELVE_FILENAME)
        if storage.has_key(short_url):
            response = SERVICE_URL + '/gs' + short_url
        else:
            storage[short_url] = long_url
            response = SERVICE_URL + '/gs' + short_url
        return response

class AdminDone:
    def GET(self, short_name):
	web.header("Content-Type","text/html; charset=utf-8")
        admin_done_template = web.template.Template("""$def with(new_url)
        <!DOCTYPE HTML>
        <html lang="en">
          <head>
            <meta charset=utf-8>
            <title>URL shortener administration</title>
          </head>
          <body>
            <header><h1>Done!</h1></header>
            <p>You created: <a href=$new_url>$new_url</a> </p>
          </body>
        </html>
        """)
        return admin_done_template(SERVICE_URL + '/gs' + short_name)

if __name__ == "__main__":
    app.run()
