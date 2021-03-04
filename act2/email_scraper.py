import socket
import ssl
from dataclasses import dataclass
import time
from bs4 import BeautifulSoup
import logging
import threading
import csv
import re
from collections import deque

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
    total_data=[];
    data='';
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
    return ''.join(total_data)


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

def get_hosts():
    with open('companies.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        addresses = []
        for row in spamreader:
            address = row[len(row)-1].split(",")[1]
            if(address[-1] == '/'):
                addresses.append(address[:-1])
            else:
                addresses.append(address)
    hosts = []
    for i in addresses:
        host = i.split("//")[1]
        if not re.search("www", host):
            fixed_host = "www."+host
            hosts.append(fixed_host)
        else:
            hosts.append(host)
    return hosts



def scrape_emails(hosts):
    request = GetRequest(hosts[1], "/")
    out = send_get_request(hosts[1], request)
    soup = BeautifulSoup(out, 'html.parser')
    for a in soup.find_all("a"):
        href = a.attrs.get('href')
        if not (re.search("://", str(href))) and str(href).startswith('/'):
            print("stub: {url}".format(url = href))

def act2():
    hosts = get_hosts()
    scrape_emails(hosts)

act2()

"""
def act2():
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    threads = list()
    for i in sources:
        logging.info("Main    : create and start thread %d.", i)
        x = threading.Thread(target=download_image, args=(i, name))
        threads.append(x)
        x.start()
        name_iterator+=1

    for i, thread in enumerate(threads):
        logging.info("Main    : before joining thread %d.", i)
        thread.join()
        logging.info("Main    : thread %d done", i)
"""
