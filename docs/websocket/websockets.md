# Part 11: WebSockets

---

## Chapter 1: Real-Time Chat with WebSockets

### 1. Introduction
WebSockets establish a persistent, low-latency, bi-directional communication channel between a client and a server over a single TCP connection, replacing traditional HTTP polling.

### 2. Concept Explanation
* **Why it exists**: Traditional HTTP is unidirectional (client requests, server responds). Real-time apps like chats require the server to push updates to the client instantly without waiting for a request.
* **When to use it**: Live chat rooms, collaborative document editing, real-time financial dashboards, system log monitors.
* **When NOT to use it**: Simple CRUD REST applications where client interactions are transactional and episodic.
* **Advantages**: Bi-directional streaming, low payload overhead (no HTTP headers are sent after connection handshake), real-time updates.
* **Disadvantages**: Harder to scale horizontally (requires a message broker like Redis Pub/Sub to sync connections across servers), firewall blocks can interrupt connections.
* **Industry Use Cases**: Messaging channels, multiplayer gaming, live notifications.

### 3. Architecture Explanation
The application manages connections using a connection manager class, storing active websocket connections and broadcasting messages to all connected clients.
```
Client 1 ---\
Client 2 ----> [ ConnectionManager ] ---> Broadcasts message to all clients
Client 3 ---/
```

### 4. Visual Workflow
```
Client ---> HTTP Handshake (Upgrade: websocket) ---> Connection Accepted ---> Persistent TCP Session
```

### 5. Real-World Scenario
A customer support portal needs a chat backend where administrators and customers can exchange messages instantly in a shared chat room.

### 6. Step-by-Step Implementation
1. Define a class to manage active WebSocket connections.
2. Implement route endpoints with the `WebSocket` and `WebSocketDisconnect` objects.
3. Build broadcast functions to route messages to all active connections.

### 7. Source Code Examples
```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI(title="Real-Time Chat Application")

# Connection Manager to keep track of active WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Simple web interface for testing
@app.get("/")
async def get():
    html_content = """
    <!DOCTYPE html>
    <html>
        <head><title>Chat</title></head>
        <body>
            <h1>FastAPI WebSocket Chat</h1>
            <input type="text" id="messageText" autocomplete="off"/>
            <button onclick="sendMessage()">Send</button>
            <ul id='messages'></ul>
            <script>
                var ws = new WebSocket("ws://localhost:8000/ws/chat");
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages');
                    var message = document.createElement('li');
                    var content = document.createTextNode(event.data);
                    message.appendChild(content);
                    messages.appendChild(message);
                };
                function sendMessage() {
                    var input = document.getElementById("messageText");
                    ws.send(input.value);
                    input.value = '';
                }
            </script>
        </body>
    </html>
    """
    return HTMLResponse(html_content)

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Wait for message from client
            data = await websocket.receive_text()
            # Broadcast message to everyone
            await manager.broadcast(f"Client: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A client left the chat room.")
```

### 8. API Testing Examples
Launch the application with Uvicorn and open `http://localhost:8000/` in multiple browser tabs to send messages and verify they are broadcasted in real time.
```bash
uvicorn main:app --reload
```

### 9. Common Mistakes
Forgetting to wrap WebSocket reading loops in `try/except WebSocketDisconnect` blocks, leaving broken connections in memory and causing memory leaks.

### 10. Best Practices
Set up connection limits and add heartbeats (ping/pong) to clean up stale connections. In production, use Redis Pub/Sub to scale WebSockets across multiple server nodes.

### 11. Interview Questions
* **Q: How do you scale WebSockets horizontally across multiple servers?**
  * *A*: Since WebSockets keep a persistent connection open to a specific server, you must use a message broker like Redis Pub/Sub. When a server receives a message, it publishes it to Redis, which broadcasts it to all other servers to send to their connected clients.

### 12. Chapter Summary
WebSockets support persistent, bi-directional, real-time messaging. Managing connections with a centralized class ensures they are accepted and cleaned up correctly.

### 13. Practice Exercises
Add username parameters to `/ws/chat/{username}` to include sender names in broadcasted chat messages.
