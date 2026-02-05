/**
 * WebSocket client for real-time chat
 */

class WebSocketClient {
  constructor() {
    this.ws = null;
    this.messageCallbacks = [];
    this.statusCallbacks = [];
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 2000;
  }

  connect(url = 'ws://localhost:8000/ws/chat') {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log('WebSocket: Already connected');
      return;
    }

    console.log('WebSocket: Connecting to', url);
    try {
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        console.log('WebSocket: Connected successfully ✅');
        this.reconnectAttempts = 0;
        this.notifyStatus('connected');
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('WebSocket: Message received -', data.type || 'response');
          this.messageCallbacks.forEach(callback => callback(data));
        } catch (error) {
          console.error('WebSocket: Parse error -', error.message);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket: Connection error ❌');
        this.notifyStatus('error');
      };

      this.ws.onclose = () => {
        console.log('WebSocket: Connection closed');
        this.notifyStatus('closed');
        this.attemptReconnect(url);
      };
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      this.notifyStatus('error');
    }
  }

  attemptReconnect(url) {
    // Don't auto-reconnect, let user manually toggle
    console.log('WebSocket: Connection lost. Toggle to REST API or retry later.');
    this.notifyStatus('failed');
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.error('WebSocket is not connected');
      throw new Error('WebSocket is not connected');
    }
  }

  sendMessage(question, userId, sessionId) {
    console.log('WebSocket: Sending message');
    this.send({
      question,
      user_id: userId,
      session_id: sessionId
    });
  }

  onMessage(callback) {
    this.messageCallbacks.push(callback);
  }

  onStatus(callback) {
    this.statusCallbacks.push(callback);
  }

  clearCallbacks() {
    this.messageCallbacks = [];
    this.statusCallbacks = [];
    console.log('WebSocket: Callbacks cleared');
  }

  disconnect() {
    if (this.ws) {
      console.log('WebSocket: Disconnecting...');
      this.ws.close();
      this.ws = null;
      console.log('WebSocket: Disconnected ✅');
    }
  }

  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN;
  }
}

// Export singleton instance
export const wsClient = new WebSocketClient();

export default WebSocketClient;
