import asyncio
import socket

async def scan_port(host, port, timeout=1):
    """Scan a single TCP port asynchronously."""
    try:
        conn = asyncio.open_connection(host, port)
        reader, writer = await asyncio.wait_for(conn, timeout=timeout)
        
        # Optional: Banner grabbing
        try:
            writer.write(b"\n")
            await writer.drain()
            banner = await asyncio.wait_for(reader.read(100), timeout=1)
            banner = banner.decode(errors="ignore").strip()
        except:
            banner = "No banner"
        
        print(f"[OPEN] {host}:{port} - {banner}")
        writer.close()
        await writer.wait_closed()
    except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
        pass  # Port closed or filtered

async def main():
    host = "scanme.nmap.org"  # Example target
    ports = range(20, 1025)   # Common ports
    tasks = [scan_port(host, port) for port in ports]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
