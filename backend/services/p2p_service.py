import asyncio
import socket
import json
from config import P2P_ENABLED, P2P_BROADCAST_PORT, P2P_BOOK_PORT
from services.identity import generate_user_id

class P2PService:
    def __init__(self, db_session):
        self.user_id = generate_user_id()
        self.db = db_session
        self.peers = {}
        self.running = False
        
    async def start(self):
        if not P2P_ENABLED:
            return
            
        self.running = True
        await asyncio.gather(
            self.broadcast_loop(),
            self.listen_broadcast(),
            self.serve_books()
        )
        
    async def stop(self):
        self.running = False
        
    async def broadcast_loop(self):
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                
                message = json.dumps({
                    "type": "discovery",
                    "user_id": self.user_id,
                    "port": P2P_BOOK_PORT
                })
                
                sock.sendto(message.encode(), ('<broadcast>', P2P_BROADCAST_PORT))
                sock.close()
                
            except Exception as e:
                print(f"Broadcast error: {e}")
                
            await asyncio.sleep(30)
            
    async def listen_broadcast(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', P2P_BROADCAST_PORT))
        
        while self.running:
            try:
                data, addr = sock.recvfrom(4096)
                message = json.loads(data.decode())
                
                if message["user_id"] != self.user_id:
                    self.peers[message["user_id"]] = addr[0]
                    
            except Exception as e:
                print(f"Listen error: {e}")
                
        sock.close()
        
    async def serve_books(self):
        server = await asyncio.start_server(
            self.handle_client, '0.0.0.0', P2P_BOOK_PORT
        )
        
        async with server:
            await server.serve_forever()
            
    async def handle_client(self, reader, writer):
        try:
            data = await reader.read(4096)
            request = json.loads(data.decode())
            
            if request["action"] == "get_books":
                from services.book_builder import get_all_books
                books = get_all_books(self.db)
                books_data = [{
                    "id": b.id,
                    "title": b.title,
                    "description": b.description,
                    "chapter_count": len(b.chapters) if hasattr(b, 'chapters') else 0
                } for b in books]
                
                writer.write(json.dumps(books_data).encode())
                await writer.drain()
                
            elif request["action"] == "get_book":
                from services.book_builder import get_book, get_book_chapters
                book = get_book(self.db, request["book_id"])
                if book:
                    chapters = get_book_chapters(self.db, book.id)
                    book_data = {
                        "id": book.id,
                        "title": book.title,
                        "description": book.description,
                        "outline": book.outline,
                        "chapters": [{"index": c.index, "title": c.title, "content": c.content} for c in chapters]
                    }
                    writer.write(json.dumps(book_data).encode())
                    await writer.drain()
                    
        except Exception as e:
            print(f"Handle client error: {e}")
        finally:
            writer.close()
            
    async def sync_book(self, peer_ip: str, book_id: str) -> dict:
        try:
            reader, writer = await asyncio.open_connection(peer_ip, P2P_BOOK_PORT)
            
            request = {"action": "get_book", "book_id": book_id}
            writer.write(json.dumps(request).encode())
            await writer.drain()
            
            data = await reader.read(65536)
            book_data = json.loads(data.decode())
            writer.close()
            
            return book_data
            
        except Exception as e:
            print(f"Sync book error: {e}")
            return None
            
    def get_peers(self):
        return [{"id": pid, "ip": ip} for pid, ip in self.peers.items()]
