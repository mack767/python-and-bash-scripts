import socket
import ssl
import threading
import time
from queue import Queue

TARGET = "127.0.0.1"
PORTS = range(20, 1025)
TIMEOUT = 2
RATE_LIMIT = 0.1  # seconds between scans


def reverse_dns(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return "No PTR record"


def tcp_scan(port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        result = sock.connect_ex((TARGET, port))
        if result == 0:
            print(f"[+] TCP Port {port} OPEN")
            banner_grab(sock, port)
            detect_ssl(port)
        sock.close()
    except Exception as e:
        print(f"[!] TCP Error on port {port}: {e}")


def udp_scan(port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(TIMEOUT)
        sock.sendto(b"Hello", (TARGET, port))
        try:
            data, _ = sock.recvfrom(1024)
            print(f"[+] UDP Port {port} OPEN | Response: {data}")
        except socket.timeout:
            print(f"[?] UDP Port {port} OPEN|FILTERED (No response)")
        sock.close()
    except Exception as e:
        print(f"[!] UDP Error on port {port}: {e}")


def banner_grab(sock, port):
    try:
        sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
        banner = sock.recv(1024)
        print(f"[+] Banner on port {port}: {banner.decode(errors='ignore').strip()}")
    except:
        pass


def detect_ssl(port):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((TARGET, port), timeout=TIMEOUT) as sock:
            with context.wrap_socket(sock, server_hostname=TARGET) as ssock:
                print(f"[+] SSL/TLS detected on port {port}")
    except:
        pass


def worker():
    while not queue.empty():
        port = queue.get()
        tcp_scan(port)
        udp_scan(port)
        time.sleep(RATE_LIMIT)
        queue.task_done()


print(f"Scanning target: {TARGET}")
print(f"Reverse DNS: {reverse_dns(TARGET)}")

queue = Queue()

for port in PORTS:
    queue.put(port)

for _ in range(10):
    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()

queue.join()
print("Scan completed.")