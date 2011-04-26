#!/usr/bin/python

import web
import shelve
import hashlib
from random import choice

SHELVE_FILENAME =  'shelfshorturl.bg'
POST_REDIRECT_URL = 'http://localhost:8080/%s/'
SERVICE_URL = "http://localhost:8080/"
ADMIN = '/admin'

urls = (
    ADMIN,              "Admin",
    ADMIN+"/done/(.*)", "AdminDone",
    "/",                "Home",
    "/favicon(.*)",     "Favicon",
    "/(.*)",           "RedirectToOthers",
)

#Messages
HOME_MESSAGE = '''Welcome to URL shortenner. 
		/admin to get controls'''
FAIL_MESSAGE = 'Redirection failed, verify your link...'  # Messages

app = web.application(urls, globals())

# Forms a hash of the url and appends the short code with a predefined character.
def random_shortcut(mylink, length=8):
    predef = "g"
    hashed = hashlib.sha1()
    hashed.update(mylink)
    digested_short = predef + hashed.hexdigest()[:length]
    return digested_short

class Home:
    def GET(self):
        return HOME_MESSAGE

class Favicon:
    def GET(self, icon_name):
        return None

class RedirectToOthers:
    def GET(self, short_name):
        storage = shelve.open(SHELVE_FILENAME)                 
        short_name = str(short_name) # shelve does not allow unicode keys
        if storage.has_key(short_name):
            response = web.redirect(storage[short_name])
        else:
            response = FAIL_MESSAGE
        storage.close() 
        print response
        return response  

class Admin:
    def GET(self):
        admin_form = web.form.Form(
            web.form.Textbox("url",     description="Long URL"),
            web.form.Textbox("shortcut",description="Your own shortcut"),
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
            <form method="POST" action="/admin">
              $:form.render()
              <input type="submit" value="Shorten this long URL">
            </form>
          </body>
        </html>
        """)
        return admin_template(admin_form())

    def POST(self):
        data = web.input()
        shortcut = str(data.shortcut) or random_shortcut(data.url)
        storage = shelve.open(SHELVE_FILENAME)
        if storage.has_key(shortcut) or not data.url:
            response = web.badrequest()
        else:
            storage[shortcut] = data.url
            response = web.seeother(ADMIN+'/done/'+shortcut)
        storage.close()
        return response

class AdminDone:
    def GET(self, short_name):
        admin_done_template = web.template.Template("""$def with(new_url)
        <!DOCTYPE HTML>
        <html lang="en">
          <head>
            <meta charset=utf-8>
            <title>URL shortener administration</title>
          </head>
          <body>
            <header><h1>Done!</h1></header>
            <p>You created: $new_url</p>
          </body>
        </html>
        """)
        return admin_done_template(SERVICE_URL+short_name)

if __name__ == "__main__":
    app.run()
