import tornado
import tornado.web
import tornado.websocket
import tornado.gen
import tornado.ioloop
import tornado.httpserver

import uuid
import signal

import tornadoredis
import redis
import time

redis_sync = redis.Redis(host="localhost", port=6379)
channel = None


class MainHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        self.redis = None
        self.channel = None
        self.identifier = str(uuid.uuid4())
        self.should_publish = False
        super(MainHandler, self).__init__(*args, **kwargs)

    def initialize(self):
        self.redis = tornadoredis.Client()
        self.redis.connect()


    @tornado.web.asynchronous
    @tornado.gen.engine
    def open(self):
        global channel

        if channel:
            self.channel = channel
            channel = None
            self.should_publish = True
        else:
            channel = str(uuid.uuid4())
            self.channel = channel
            self.should_publish = False

        print "Connected", self.identifier

        self.redis.subscribe([self.channel], self.on_subscribe_successful)

    def on_subscribe_successful(self, successful):
        if successful:
            self.redis.listen(callback=self.on_subscribe_message, exit_callback=self.on_subscribe_exit)
        else:
            print("On Finish")
            self.close()

    def on_subscribe_message(self, message):
        """Called on pubsub messages."""
        if message.kind == 'message':
            other_identifier, real_message = message.body[:36], message.body[36:]
            if other_identifier != self.identifier:
                print "Receive", real_message
                self.write_message(real_message)
        elif message.kind == 'subscribe':
            if self.should_publish:
                redis_sync.publish(self.channel, str(uuid.uuid4())+"200")

    def on_subscribe_exit(self, state):
        self.close()

    def on_message(self, message):
        total_message = self.identifier+message
        print "Send", message
        redis_sync.publish(self.channel, total_message)

    def check_origin(self, origin):
        return True


### SIGNAL HANDLERS


def sig_handler(sig, frame):
    tornado.ioloop.IOLoop.instance().add_callback_from_signal(shutdown)


def shutdown():
    server.stop()

    io_loop = tornado.ioloop.IOLoop.instance()

    deadline = time.time() + 2

    def stop_loop():
        now = time.time()
        if now < deadline and (io_loop._callbacks or io_loop._timeouts):
            io_loop.add_timeout(now + 1, stop_loop)
        else:
            io_loop.stop()

    stop_loop()

for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT]:
    signal.signal(sig, sig_handler)


def make_app():
    return tornado.web.Application([(r'/', MainHandler)], debug=True)


def main():
    global server
    application = make_app()

    server = tornado.httpserver.HTTPServer(application, xheaders=True)
    server.listen(5000)

    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
