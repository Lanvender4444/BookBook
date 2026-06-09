import asyncio
import json
import secrets
import time
from datetime import datetime, timedelta
from database import SessionLocal
from config import P2P_PORT, P2P_MAGIC, P2P_APP_ID, P2P_VERSION
from services.identity import generate_user_id
from models import ShareToken


class P2PService:
    PROTOCOL_VERSION = "1"
    
    def __init__(self):
        self.user_id = generate_user_id()
        self.server = None
        self.running = False
        self._handshake_buffer = b""
    
    async def start(self):
        self.running = True
        await self._start_server()
    
    async def stop(self):
        self.running = False
        if self.server:
            self.server.close()
            await self.server.wait_closed()
    
    async def _start_server(self):
        self.server = await asyncio.start_server(
            self._handle_connection, '0.0.0.0', P2P_PORT
        )
        async with self.server:
            await self.server.serve_forever()
    
    async def _handle_connection(self, reader, writer):
        addr = writer.get_extra_info('peername')
        try:
            handshake_data = await asyncio.wait_for(reader.read(4096), timeout=10)
            handshake = json.loads(handshake_data.decode())
            
            if handshake.get("magic") != P2P_MAGIC:
                writer.write(json.dumps({"status": "error", "message": "invalid magic"}).encode())
                await writer.drain()
                writer.close()
                return
            
            if handshake.get("app_id") != P2P_APP_ID:
                writer.write(json.dumps({"status": "error", "message": "invalid app_id"}).encode())
                await writer.drain()
                writer.close()
                return
            
            peer_id = handshake.get("peer_id", "")
            version = handshake.get("version", "0")
            
            response = {
                "magic": P2P_MAGIC,
                "app_id": P2P_APP_ID,
                "version": P2P_VERSION,
                "peer_id": self.user_id,
                "status": "ok"
            }
            writer.write(json.dumps(response).encode())
            await writer.drain()
            
            request_data = await asyncio.wait_for(reader.read(65536), timeout=30)
            request = json.loads(request_data.decode())
            
            action = request.get("action")
            
            if action == "list_books":
                await self._handle_list_books(writer)
            elif action == "get_book":
                await self._handle_get_book(writer, request)
            elif action == "verify_share":
                await self._handle_verify_share(writer, request)
            else:
                writer.write(json.dumps({"status": "error", "message": "unknown action"}).encode())
                await writer.drain()
                
        except asyncio.TimeoutError:
            try:
                writer.write(json.dumps({"status": "error", "message": "timeout"}).encode())
                await writer.drain()
            except:
                pass
        except Exception as e:
            pass
        finally:
            try:
                writer.close()
            except:
                pass
    
    async def _handle_list_books(self, writer):
        from services.book_builder import get_all_books
        db = SessionLocal()
        try:
            books = get_all_books(db)
            books_data = []
            for b in books:
                chapters = []
                if hasattr(b, 'chapters') and b.chapters:
                    chapters = [{"index": c.index, "title": c.title} for c in b.chapters]
                books_data.append({
                    "id": b.id,
                    "title": b.title,
                    "description": b.description,
                    "chapter_count": len(chapters),
                    "author_id": b.author_id,
                    "source": b.source,
                    "language": b.language
                })
            writer.write(json.dumps({"status": "ok", "books": books_data}).encode())
            await writer.drain()
        finally:
            db.close()
    
    async def _handle_get_book(self, writer, request):
        book_id = request.get("book_id")
        from services.book_builder import get_book, get_book_content, get_book_chapters
        
        db = SessionLocal()
        try:
            book = get_book(db, book_id)
            if not book:
                writer.write(json.dumps({"status": "error", "message": "book not found"}).encode())
                await writer.drain()
                return
            
            chapters = get_book_chapters(db, book_id)
            book_data = {
                "status": "ok",
                "book": {
                    "id": book.id,
                    "title": book.title,
                    "description": book.description,
                    "outline": book.outline,
                    "author_id": book.author_id,
                    "source": "p2p",
                    "language": book.language,
                    "chapters": [{"index": c["index"], "title": c["title"], "content": c["content"]} for c in chapters]
                }
            }
            writer.write(json.dumps(book_data, ensure_ascii=False).encode())
            await writer.drain()
        finally:
            db.close()
    
    async def _handle_verify_share(self, writer, request):
        token = request.get("token")
        db = SessionLocal()
        try:
            share = db.query(ShareToken).filter(ShareToken.token == token).first()
            
            if not share:
                writer.write(json.dumps({"status": "error", "message": "invalid token"}).encode())
                await writer.drain()
                return
            
            if share.expires_at and share.expires_at < datetime.now():
                writer.write(json.dumps({"status": "error", "message": "token expired"}).encode())
                await writer.drain()
                return
            
            if share.book_id:
                from services.book_builder import get_book, get_book_chapters
                book = get_book(db, share.book_id)
                if book:
                    chapters = get_book_chapters(db, share.book_id)
                    book_data = {
                        "status": "ok",
                        "book": {
                            "id": book.id,
                            "title": book.title,
                            "description": book.description,
                            "outline": book.outline,
                            "author_id": book.author_id,
                            "source": "p2p",
                            "language": book.language,
                            "chapters": [{"index": c["index"], "title": c["title"], "content": c["content"]} for c in chapters]
                        }
                    }
                    writer.write(json.dumps(book_data, ensure_ascii=False).encode())
                    await writer.drain()
                    share.used_count += 1
                    db.commit()
                    return
            
            writer.write(json.dumps({"status": "error", "message": "book not found"}).encode())
            await writer.drain()
        finally:
            db.close()
    
    def create_share_token(self, book_id: str = None, expires_hours: int = 24) -> dict:
        token = secrets.token_urlsafe(32)
        db = SessionLocal()
        try:
            share = ShareToken(
                token=token,
                book_id=book_id,
                peer_id=self.user_id,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=expires_hours)
            )
            db.add(share)
            db.commit()
            db.refresh(share)
            expires_at = share.expires_at.isoformat() if share.expires_at else None
        finally:
            db.close()
        return {
            "token": token,
            "share_url": f"bookbook://share?token={token}&peer={self.user_id}&v={P2P_VERSION}",
            "expires_at": expires_at
        }
    
    def get_share_info(self, token: str) -> dict:
        db = SessionLocal()
        try:
            share = db.query(ShareToken).filter(ShareToken.token == token).first()
            if not share:
                return None
            if share.expires_at and share.expires_at < datetime.now():
                return None
            return {
                "token": share.token,
                "book_id": share.book_id,
                "peer_id": share.peer_id,
                "created_at": share.created_at.isoformat(),
                "expires_at": share.expires_at.isoformat() if share.expires_at else None,
                "used_count": share.used_count
            }
        finally:
            db.close()
    
    async def connect_to_peer(self, host: str, port: int) -> dict:
        reader, writer = await asyncio.open_connection(host, port)
        
        try:
            handshake = {
                "magic": P2P_MAGIC,
                "app_id": P2P_APP_ID,
                "version": P2P_VERSION,
                "peer_id": self.user_id,
                "timestamp": int(time.time())
            }
            writer.write(json.dumps(handshake).encode())
            await writer.drain()
            
            response_data = await asyncio.wait_for(reader.read(4096), timeout=10)
            response = json.loads(response_data.decode())
            
            if response.get("status") != "ok":
                return {"status": "error", "message": response.get("message", "handshake failed")}
            
            return {"status": "ok", "peer_id": response.get("peer_id")}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def fetch_book_list(self, host: str, port: int = None) -> list:
        if port is None:
            port = P2P_PORT
        
        try:
            reader, writer = await asyncio.open_connection(host, port)
            
            handshake = {
                "magic": P2P_MAGIC,
                "app_id": P2P_APP_ID,
                "version": P2P_VERSION,
                "peer_id": self.user_id,
                "timestamp": int(time.time())
            }
            writer.write(json.dumps(handshake).encode())
            await writer.drain()
            
            response_data = await asyncio.wait_for(reader.read(4096), timeout=10)
            response = json.loads(response_data.decode())
            
            if response.get("status") != "ok":
                writer.close()
                return []
            
            request = {"action": "list_books"}
            writer.write(json.dumps(request).encode())
            await writer.drain()
            
            books_data = await asyncio.wait_for(reader.read(65536), timeout=30)
            result = json.loads(books_data.decode())
            writer.close()
            
            return result.get("books", [])
            
        except Exception as e:
            return []
    
    async def fetch_book(self, host: str, book_id: str, port: int = None) -> dict:
        if port is None:
            port = P2P_PORT
        
        try:
            reader, writer = await asyncio.open_connection(host, port)
            
            handshake = {
                "magic": P2P_MAGIC,
                "app_id": P2P_APP_ID,
                "version": P2P_VERSION,
                "peer_id": self.user_id,
                "timestamp": int(time.time())
            }
            writer.write(json.dumps(handshake).encode())
            await writer.drain()
            
            response_data = await asyncio.wait_for(reader.read(4096), timeout=10)
            response = json.loads(response_data.decode())
            
            if response.get("status") != "ok":
                writer.close()
                return None
            
            request = {"action": "get_book", "book_id": book_id}
            writer.write(json.dumps(request).encode())
            await writer.drain()
            
            book_data = await asyncio.wait_for(reader.read(131072), timeout=60)
            result = json.loads(book_data.decode())
            writer.close()
            
            if result.get("status") == "ok":
                return result.get("book")
            return None
            
        except Exception as e:
            return None
    
    async def fetch_by_share_token(self, host: str, token: str, port: int = None) -> dict:
        if port is None:
            port = P2P_PORT
        
        try:
            reader, writer = await asyncio.open_connection(host, port)
            
            handshake = {
                "magic": P2P_MAGIC,
                "app_id": P2P_APP_ID,
                "version": P2P_VERSION,
                "peer_id": self.user_id,
                "timestamp": int(time.time())
            }
            writer.write(json.dumps(handshake).encode())
            await writer.drain()
            
            response_data = await asyncio.wait_for(reader.read(4096), timeout=10)
            response = json.loads(response_data.decode())
            
            if response.get("status") != "ok":
                writer.close()
                return None
            
            request = {"action": "verify_share", "token": token}
            writer.write(json.dumps(request).encode())
            await writer.drain()
            
            result_data = await asyncio.wait_for(reader.read(131072), timeout=60)
            result = json.loads(result_data.decode())
            writer.close()
            
            if result.get("status") == "ok":
                return result.get("book")
            return None
            
        except Exception as e:
            return None
    
    def get_peers(self):
        return []