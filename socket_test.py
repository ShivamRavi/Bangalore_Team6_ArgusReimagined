import socket

def test_ipv6():
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    s.settimeout(5)
    try:
        s.connect(('::1', 9200))
        s.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        data = s.recv(4096)
        print('Received', data[:200])
    except Exception as e:
        print('Error', e)
    finally:
        s.close()

if __name__ == '__main__':
    test_ipv6()
