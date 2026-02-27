import type { LiveUpdate } from "@/types/api";

type MessageHandler = (data: LiveUpdate) => void;

class WSClient {
  private ws: WebSocket | null = null;
  private handlers: Set<MessageHandler> = new Set();
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private url: string = "";

  connect(token: string) {
    const wsBase = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000")
      .replace("http://", "ws://")
      .replace("https://", "wss://");
    this.url = `${wsBase}/v1/ws/live?token=${token}`;
    this._connect();
  }

  private _connect() {
    if (this.ws?.readyState === WebSocket.OPEN) return;

    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      console.log("[WS] Connected");
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "pong") return;
        this.handlers.forEach((h) => h(data));
      } catch { /* ignore parse errors */ }
    };

    this.ws.onclose = () => {
      console.log("[WS] Disconnected, reconnecting in 3s...");
      this.reconnectTimer = setTimeout(() => this._connect(), 3000);
    };

    this.ws.onerror = () => {
      this.ws?.close();
    };
  }

  subscribe(handler: MessageHandler) {
    this.handlers.add(handler);
    return () => this.handlers.delete(handler);
  }

  disconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.ws?.close();
    this.ws = null;
    this.handlers.clear();
  }

  sendPing() {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send("ping");
    }
  }
}

export const wsClient = new WSClient();
