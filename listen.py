import socket
import threading
try:
    import socketserver
except ImportError:
    import SocketServer as socketserver
import subprocess
from brightness import warning, set_brightness


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        cur_thread = threading.current_thread()
        self.request.sendall('YO {}\r\n'.format(cur_thread.name))
        while True:
            raw = self.request.recv(1024)
            if raw == '\x04':
                break
            data = str(raw).strip()
            # subprocess.check_call(['/usr/local/bin/screenbrightness', data.strip()])
            response = 'wat?'
            if data.lower() == 'w':
                self.request.sendall('!!BEGIN WARNING!!\r\n')
                warning()
                response = "WARNING ENDED\r\n"
            else:
                try:
                    set_brightness(float(data))
                    response = "set_brightness: {}\r\n".format(data)
                except ValueError:
                    pass
            self.request.sendall(response)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(bytes(message, 'ascii'))
        response = str(sock.recv(1024), 'ascii')
        print("Received: {}".format(response))
    finally:
        sock.close()

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "0.0.0.0", 8000

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    # server_thread.daemon = True
    server_thread.start()
