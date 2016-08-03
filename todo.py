import os.path

import base64
import uuid
import psycopg2
import momoko

import tornado
import tornado.httpserver
import tornado.ioloop
from tornado import web
from tornado import gen


from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", AllLists),
            (r"/create/", CreateLists),
        ]
        settings = dict(
            todo_title=u"ToDo",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            cookie_secret=base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
            login_url="/auth/login",
            debug=True,
        )

        super(Application, self).__init__(handlers, **settings)

        ioloop = tornado.ioloop.IOLoop.instance()
        self.db = momoko.Pool(
            dsn='dbname=todo user=root password=````` '
                'host=localhost port=5432',
            size=1,
            ioloop=ioloop,
            cursor_factory=psycopg2.extras.RealDictCursor
        )

        future = self.db.connect()
        ioloop.add_future(future, lambda f: ioloop.stop())
        ioloop.start()
        future.result()


class BaseHandler(web.RequestHandler):
    @property
    def db(self):
        return self.application.db


class AllLists(BaseHandler):
    @gen.coroutine
    def get(self):
        lists = yield self.db.execute("SELECT * FROM lists ORDER BY published DESC LIMIT 5")
        if not lists:
            self.redirect("/create")
            return
        self.render("home.html", lists=lists.fetchall())


class CreateLists(BaseHandler):
    def get(self):
        self.render("create.html")

    def post(self):
        title = self.get_argument("title")
        description = self.get_argument("description")
        self.db.execute(
            "INSERT INTO lists (title, description, published, updated) VALUES ('{0}','{1}',now(),now())"
            .format(title, description)
        )
        self.redirect('/')

if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

