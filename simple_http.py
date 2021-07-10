import time
import logging
import traceback
from cryptography.fernet import Fernet

f = Fernet('yHwFlf0AdgEQyPQetKUvkf9kEEasmNVzAglDd2N_Mvo=')

def recv_http_message(sock):
    buffer = b''
    while b'\r\n\r\n' not in buffer:
        buffer += sock.recv(1024)
    
    buffer = buffer.decode()
    headers = parse_headers(buffer)
    i = buffer.index('\r\n\r\n')
    if not headers: return None
    if 'Content-Length' in headers:
        content_length = int(headers['Content-Length'])
        sock.recv(content_length - (len(buffer) - i - 4))
    print(buffer)
    return headers
      

def make_request(addr_type, addr, port):
    print('make_request', addr_type, addr, port)
    addr_enc = f.encrypt(addr.encode()).decode()
    port_enc = f.encrypt(str(port).encode()).decode()
    return 'GET / HTTP/1.1\r\n' + \
        f'Type: {addr_type}\r\n' + \
        f'X-TOKEN-A: {addr_enc}\r\n' + \
        f'X-TOKEN-P: {port_enc}\r\n\r\n'


def make_empty_response():
    return 'HTTP/1.1 200 OK\r\n' + \
        'Content-Type:text/html\r\n\r\n' + \
        '<h1>Hey there!</h1>'


def make_response(addr, port):
    print('make_response', addr, port)
    try:
        addr_enc = f.encrypt(addr.encode()).decode()
        port_enc = f.encrypt(str(port).encode()).decode()

        html = '<h1>Hey there!</h1>'
        # html = ''
    
        return 'HTTP/1.1 200 OK\r\n' + \
            f'X-TOKEN-A: {addr_enc}\r\n' + \
            f'X-TOKEN-P: {port_enc}\r\n' + \
            f'Content-Length: {len(html)}\r\n' + \
            'Content-Type: text/html\r\n\r\n' + \
            html

    except Exception as e:
        # logging.error(e)
        traceback.print_exc()
        return make_empty_response()


def parse_headers(header_str):
    headers = header_str.split('\r\n\r\n')[0]
    lines = headers.split('\r\n')[1:]
    parsed = {}
  
    for line in lines:
        if ':' in line:
            i = line.index(':')
            key = line[:i].strip()
            value = line[i+1:].strip()
            parsed[key] = value
  
    if 'X-TOKEN-A' not in parsed: return None
    if 'X-TOKEN-P' not in parsed: return None

    try:
        parsed['X-TOKEN-A'] = f.decrypt(parsed['X-TOKEN-A'].encode()).decode()
        parsed['X-TOKEN-P'] = int(f.decrypt(parsed['X-TOKEN-P'].encode()).decode())
    except Exception as e:
        # logging.error(e)
        traceback.print_exc()
        return None

    print('parsed:', parsed)
    return parsed 
