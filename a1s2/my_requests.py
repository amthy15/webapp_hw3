import socket
import ssl
from dataclasses import dataclass
import time
from bs4 import BeautifulSoup
import logging
import threading

@dataclass
class GetRequest:
    host: str
    endpoint: str

    def header(self):
        ### Define default header format ###
        header = """GET {e} HTTP/1.1\r
Host: {h}\r
Accept: */*\r
Accept-Language: en\r
Connection: close\r
\r
"""

        ### Format header data ###
        headers = header.format(
            e = self.endpoint,
            h = self.host,
        )
        ### Return header string ###
        return headers

def recv_timeout(the_socket,timeout=2):
    #make socket non blocking
    the_socket.setblocking(0)
    #total data partwise in an array
    total_data=b'';
    data=b'';
    #beginning time
    begin=time.time()
    while 1:
        #if you got some data, then break after timeout
        if total_data and time.time()-begin > timeout:
            break
        #if you got no data at all, wait a little longer, twice the timeout
        elif time.time()-begin > timeout*2:
            break
        #recv something
        try:
            data = the_socket.recv(8192)
            if data:
                total_data.append(data.decode('utf-8'))
                #change the beginning time for measurement
                begin=time.time()
            else:
                #sleep for sometime to indicate a gap
                time.sleep(0.1)
        except:
            pass
    #join all parts to make final string
    return b''.join(total_data)


"""
requests adjacent tool, take in header object and send HTTPS request
"""
def send_get_request(host: str, req: GetRequest):
    payload = req.header()
    print(payload)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.create_default_context()
    sock = context.wrap_socket(sock, server_hostname = host)
    sock.connect((host, 443))
    sock.sendall(payload.encode())
    print("message sent successfully")
    out = recv_timeout(sock)
    return out

### Step 2 ###
def get_image_src():
    sources = []
    request = GetRequest("www.rit.edu",
                         "/computing/directory?term_node_tid_depth=4919")
    out = send_get_request("www.rit.edu", request)
    soup = BeautifulSoup(out, 'html.parser')
    for i in soup.find_all('img', class_ = "card-img-top"):
        sources.append(str(i.get('data-src'))[21:])

    return sources

def download_image(endpoint: str, fname: str):
    request = GetRequest("www.rit.edu", endpoint)
    reply = send_get_request("www.rit.edu", request)
    headers =  reply.split(b'\r\n\r\n')[0]
    image = reply[len(headers)+4:]

    # save image
    f = open(fname, 'wb')
    f.write(image)
    f.close()

def a1s2():
    sources = get_image_src()
    name_iterator = 0
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    threads = list()
    for i in sources:
        name = "image{iter}.png".format(iter=name_iterator)
        logging.info("Main    : create and start thread %d.", i)
        x = threading.Thread(target=download_image, args=(i, name))
        threads.append(x)
        x.start()
        name_iterator+=1

    for i, thread in enumerate(threads):
        logging.info("Main    : before joining thread %d.", i)
        thread.join()
        logging.info("Main    : thread %d done", i)

a1s2()
