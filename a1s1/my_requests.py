import socket
import ssl
from dataclasses import dataclass
import time
from bs4 import BeautifulSoup
import re
import csv

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

def a1s1():
    request = GetRequest("www.rit.edu",
                         "/study/computing-security-bs")
    out = send_get_request("www.rit.edu", request)
    soup = BeautifulSoup(out, 'html.parser')
    with open('classes.csv', mode='w') as class_file:
        csv_writer = csv.writer(class_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for i in soup.find("curriculum").find_all("tr", class_ = "hidden-row"):
            course_num_raw = i.find("td")
            course_num = course_num_raw.contents
            course_num_str = str(course_num).replace("\\xa0", "")
            regexp = re.compile(r'[A-Z][A-Z][A-Z][A-Z]-[0-9][0-9][0-9]')
            if regexp.search(course_num_str):
                course_name = i.find("div", class_ = "course-name").contents
                course_name_str = str(course_name).replace("\\xa0", "")
                csv_writer.writerow([course_num_str[2:len(course_num_str)-2],
                                     course_name_str[2:len(course_name_str)-2]])
            else:
                pass

a1s1()

