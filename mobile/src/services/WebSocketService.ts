// @ts-nocheck
import io from 'socket.io-client';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.listeners = {};
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  connect = (url) => {
    try {
      this.socket = io(url, {
        transports: ['websocket'],
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionAttempts: this.maxReconnectAttempts,
        timeout: 20000,
      });

      this.socket.on('connect', () => {
        console.log('WebSocket bağlantısı kuruldu');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.emit('connection_status', { connected: true });
      });

      this.socket.on('disconnect', (reason) => {
        console.log('WebSocket bağlantısı kesildi:', reason);
        this.isConnected = false;
        this.emit('connection_status', { connected: false, reason });
      });

      this.socket.on('connect_error', (error) => {
        console.error('WebSocket bağlantı hatası:', error);
        this.reconnectAttempts++;
        this.emit('connection_error', { error, attempts: this.reconnectAttempts });
      });

      this.socket.on('initial_earthquakes', (data) => {
        console.log('Geçmiş depremler alındı:', data);
        this.emit('initial_earthquakes', data);
      });

      this.socket.on('initial_predictions', (data) => {
        console.log('Geçmiş tahminler alındı:', data);
        this.emit('initial_predictions', data);
      });

      this.socket.on('earthquake_update', (earthquake) => {
        console.log('Yeni deprem:', earthquake);
        this.emit('earthquake_update', earthquake);
      });

      this.socket.on('prediction_result', (prediction) => {
        console.log('Deprem tahmini:', prediction);
        this.emit('prediction_result', prediction);
      });

      this.socket.on('error', (error) => {
        console.error('Socket hatası:', error);
        this.emit('socket_error', error);
      });

    } catch (error) {
      console.error('WebSocket bağlantı kurma hatası:', error);
      this.emit('connection_error', { error });
    }
  };

  disconnect = () => {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
    }
  };

  on = (event, callback) => {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
  };

  off = (event, callback) => {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    }
  };

  emit = (event, data) => {
    if (this.listeners[event]) {
      this.listeners[event].forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Event callback error for ${event}:`, error);
        }
      });
    }
  };

  sendMessage = (event, data) => {
    if (this.socket && this.isConnected) {
      this.socket.emit(event, data);
    } else {
      console.warn('WebSocket bağlantısı yok, mesaj gönderilemedi');
    }
  };

  getConnectionStatus = () => {
    return this.isConnected;
  };
}

export default new WebSocketService();