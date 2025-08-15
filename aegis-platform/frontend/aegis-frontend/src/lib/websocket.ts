// WebSocket client for real-time notifications and updates

import { WebSocketMessage, NotificationUpdate } from '@/types/notifications';

export type WebSocketEventType = 'notification' | 'bulk_operation' | 'system_status' | 'error';

export interface WebSocketClient {
  connect: () => void;
  disconnect: () => void;
  subscribe: (eventType: WebSocketEventType, callback: (data: any) => void) => () => void;
  send: (message: WebSocketMessage) => void;
  isConnected: boolean;
}

class WebSocketService {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 1000; // Start with 1 second
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private listeners: Map<WebSocketEventType, Set<(data: any) => void>> = new Map();
  private connectionPromise: Promise<void> | null = null;
  private isConnecting = false;

  constructor() {
    // Use environment variable for WebSocket URL, fallback to localhost
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = import.meta.env.VITE_WS_URL || `${wsProtocol}//${window.location.host}/ws`;
    this.url = wsHost;
    
    // Initialize listener sets
    this.listeners.set('notification', new Set());
    this.listeners.set('bulk_operation', new Set());
    this.listeners.set('system_status', new Set());
    this.listeners.set('error', new Set());
  }

  async connect(): Promise<void> {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return Promise.resolve();
    }

    if (this.isConnecting && this.connectionPromise) {
      return this.connectionPromise;
    }

    this.isConnecting = true;
    this.connectionPromise = new Promise((resolve, reject) => {
      try {
        console.log('🔌 Connecting to WebSocket:', this.url);
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('✅ WebSocket connected');
          this.reconnectAttempts = 0;
          this.reconnectInterval = 1000;
          this.isConnecting = false;
          this.startHeartbeat();
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('❌ Error parsing WebSocket message:', error);
            this.notifyListeners('error', { error: 'Invalid message format' });
          }
        };

        this.ws.onclose = (event) => {
          console.log('🔌 WebSocket disconnected:', event.code, event.reason);
          this.isConnecting = false;
          this.stopHeartbeat();
          
          if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect();
          }
        };

        this.ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          this.isConnecting = false;
          this.notifyListeners('error', { error: 'Connection failed' });
          reject(error);
        };

        // Timeout for connection
        setTimeout(() => {
          if (this.ws?.readyState !== WebSocket.OPEN) {
            this.ws?.close();
            this.isConnecting = false;
            reject(new Error('WebSocket connection timeout'));
          }
        }, 10000);

      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });

    return this.connectionPromise;
  }

  disconnect(): void {
    console.log('🔌 Disconnecting WebSocket');
    this.stopHeartbeat();
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    this.reconnectAttempts = this.maxReconnectAttempts; // Prevent auto-reconnect
  }

  subscribe(eventType: WebSocketEventType, callback: (data: any) => void): () => void {
    const listeners = this.listeners.get(eventType);
    if (listeners) {
      listeners.add(callback);
    }

    // Return unsubscribe function
    return () => {
      const listeners = this.listeners.get(eventType);
      if (listeners) {
        listeners.delete(callback);
      }
    };
  }

  send(message: WebSocketMessage): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(message));
      } catch (error) {
        console.error('❌ Error sending WebSocket message:', error);
        this.notifyListeners('error', { error: 'Failed to send message' });
      }
    } else {
      console.warn('⚠️ WebSocket not connected, cannot send message');
      this.notifyListeners('error', { error: 'Not connected' });
    }
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  private handleMessage(message: WebSocketMessage): void {
    console.log('📨 Received WebSocket message:', message.type);
    
    switch (message.type) {
      case 'notification_update':
        this.notifyListeners('notification', message.payload);
        break;
      case 'bulk_operation_progress':
        this.notifyListeners('bulk_operation', message.payload);
        break;
      case 'system_status':
        this.notifyListeners('system_status', message.payload);
        break;
      default:
        console.warn('⚠️ Unknown message type:', message.type);
    }
  }

  private notifyListeners(eventType: WebSocketEventType, data: any): void {
    const listeners = this.listeners.get(eventType);
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`❌ Error in ${eventType} listener:`, error);
        }
      });
    }
  }

  private scheduleReconnect(): void {
    this.reconnectAttempts++;
    const delay = Math.min(this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1), 30000);
    
    console.log(`🔄 Scheduling reconnect attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${delay}ms`);
    
    setTimeout(() => {
      if (this.reconnectAttempts <= this.maxReconnectAttempts) {
        this.connect().catch(error => {
          console.error('❌ Reconnect failed:', error);
        });
      }
    }, delay);
  }

  private startHeartbeat(): void {
    // Send ping every 30 seconds to keep connection alive
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected) {
        this.send({
          type: 'system_status',
          payload: { type: 'ping' },
          timestamp: new Date().toISOString()
        });
      }
    }, 30000);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }
}

// Export singleton instance
export const webSocketService = new WebSocketService();

// Hook-friendly interface
export const useWebSocket = (): WebSocketClient => {
  return {
    connect: () => webSocketService.connect(),
    disconnect: () => webSocketService.disconnect(),
    subscribe: (eventType, callback) => webSocketService.subscribe(eventType, callback),
    send: (message) => webSocketService.send(message),
    isConnected: webSocketService.isConnected
  };
};