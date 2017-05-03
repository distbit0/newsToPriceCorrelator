import sys
import os

class HTMLHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(BEE_PATH + "/beehtml.html")

class JSHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(BEE_PATH + "/beejs.js")

class CSSHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header('Content-Type', 'text/css')
        self.render(BEE_PATH + "/beecss.css")


class homeHandler(tornado.web.RequestHandler):
    # This routing table directs off to the services to support the UI.
    # Route to the appropriate function, passing in parameters as required.
    def get(self):
        beePassword = open(Orig_BEE_PATH + "/backend/password.txt").read().strip()
        if self.get_argument("password", "") == beePassword:
            if self.get_argument("function", "") == "getProfileTextFile":
                self.write(beeServices.getProfileTextFile(self.get_argument("profileName", ""), self.get_argument("newLineChar", "<br>")))
        else:
            self.write("Invalid Password")

    def post(self):
        beePassword = open(Orig_BEE_PATH + "/backend/password.txt").read().strip()
        arguments = {}
        for NVP in self.request.body.decode('utf-8').split("&"):
            name, value = NVP.split("=")
            arguments[name] = value

        if arguments["password"] == beePassword:
            if arguments["function"] == "getProfileNameList":
                self.write(beeServices.getProfileNameList())                                    # INPUT: No params
            elif arguments["function"] == "getProfileDetails":
                self.write(beeServices.getProfileDetails(arguments["profileName"]))     # INPUT: string of profileName

            elif arguments["function"] == "getExchangeList":
                self.write(beeServices.getExchangeList())                                  # use usd FOR THE TIME BEING

            elif arguments["function"] == "updateProfile":
                self.write(beeServices.updateProfile(arguments["profileDetails"]))      # INPUT: JSON profileDetails

            elif arguments["function"] == "deleteProfile":
                self.write(beeServices.deleteProfile(arguments["profileName"]))         # INPUT: string of profileName

            elif arguments["function"] == "getProfileStats":
                self.write(beeServices.getProfileStats(arguments["profileName"]))       # INPUT: string of profileName

            elif arguments["function"] == "getProfileStatsText":
                self.write(beeServices.getProfileStatsText(arguments["profileName"]))    # INPUT: string of profileName

            elif arguments["function"] == "statstEngine":
                self.write(beeServices.statsEngine(arguments["action"]))                   #starts and stops stats engine

            elif arguments["function"] == "getExchangeDetails":
                self.write(beeServices.getExchangeDetails(arguments["exchangeName"]))
            elif arguments["function"] == "getAveragePrice":
                self.write(beeServices.getCurrentPrice(arguments["exchanges"]))
        else:
            self.write("Invalid Password")


application = tornado.web.Application([
    (r"/beeServices/", homeHandler),
    (r"/", HTMLHandler),
    (r"/beejs.js", JSHandler),
    (r"/beecss.css", CSSHandler),
    (r'/webfavicon.ico()', tornado.web.StaticFileHandler, {'path': BEE_PATH + '/favicon.ico'}),
    (r"/ShareTech.ttf()", tornado.web.StaticFileHandler, {'path': BEE_PATH + '/ShareTech.ttf'}),
    (r"/bee.gif()", tornado.web.StaticFileHandler, {'path': BEE_PATH + '/bee.gif'}),
    (r"/beeBackground.jpg()", tornado.web.StaticFileHandler, {'path': BEE_PATH + '/beeBackground.jpg'}),
    (r"/documentationIcon.png()", tornado.web.StaticFileHandler, {'path': BEE_PATH + '/documentationIcon.png'}),
    (r"/improvementsIcon.png()", tornado.web.StaticFileHandler, {'path': BEE_PATH + '/improvementsIcon.png'}),
    (r"/maximiseIcon.png()", tornado.web.StaticFileHandler, {'path': BEE_PATH + '/maximiseIcon.png'}),
    (r"/minimiseIcon.png()", tornado.web.StaticFileHandler, {'path': BEE_PATH + '/minimiseIcon.png'}),
    (r"/priceIcon.png()", tornado.web.StaticFileHandler, {'path': BEE_PATH + '/priceIcon.png'}),
    (r"/refreshIcon.png()", tornado.web.StaticFileHandler, {'path': BEE_PATH + '/refreshIcon.png'}),
], ssl_options={
    "certfile": os.path.join(Orig_BEE_PATH + "/ssl/cert.pem"),
    "keyfile": os.path.join(Orig_BEE_PATH + "/ssl/privkey.pem"),
})

http_server = tornado.httpserver.HTTPServer(application, ssl_options={
    "certfile": os.path.join(Orig_BEE_PATH + "/ssl/cert.pem"),
    "keyfile": os.path.join(Orig_BEE_PATH + "/ssl/privkey.pem"),
})


if True:
	http_server.listen(port)
	tornado.ioloop.IOLoop.instance().start()
