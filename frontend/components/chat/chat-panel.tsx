"use client";
import { useState, useRef, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { useDashboardStore } from "@/stores/dashboard";
import { MessageSquare, Send, Sparkles, ExternalLink, X } from "lucide-react";
import type { Citation } from "@/types/api";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
}

export function ChatPanel() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const { selectedCompanyId, chatOpen, toggleChat, companies } = useDashboardStore();

  const selectedCompany = companies.find((c) => c.id === selectedCompanyId);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const res = await api.chat(userMsg, selectedCompanyId || undefined);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.answer, citations: res.citations },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, I encountered an error. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const quickQuestions = [
    "Why did the ESG score change?",
    "What are the latest environmental risks?",
    "Explain the last score drop",
    "What governance issues exist?",
  ];

  if (!chatOpen) {
    return (
      <Button
        onClick={toggleChat}
        className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg z-50"
        size="icon"
      >
        <MessageSquare className="w-6 h-6" />
      </Button>
    );
  }

  return (
    <div className="w-80 border-l border-gray-200 bg-white flex flex-col h-screen sticky top-0">
      <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-emerald-600 to-teal-600 text-white">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4" />
          <h3 className="text-sm font-semibold">ESG AI Assistant</h3>
        </div>
        <Button variant="ghost" size="icon" onClick={toggleChat} className="text-white hover:bg-white/20 h-8 w-8">
          <X className="w-4 h-4" />
        </Button>
      </div>

      {selectedCompany && (
        <div className="px-4 py-2 bg-gray-50 border-b">
          <p className="text-xs text-gray-500">
            Analyzing: <span className="font-medium text-gray-700">{selectedCompany.name}</span>
          </p>
        </div>
      )}

      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {messages.length === 0 && (
            <div className="space-y-3 pt-4">
              <p className="text-xs text-gray-400 text-center">Ask me about ESG risks and scores</p>
              {quickQuestions.map((q) => (
                <button
                  key={q}
                  onClick={() => {
                    setInput(q);
                    setTimeout(() => sendMessage(), 100);
                  }}
                  className="w-full text-left text-xs p-2.5 rounded-lg border border-gray-200 hover:bg-emerald-50 hover:border-emerald-200 transition-colors text-gray-600"
                >
                  {q}
                </button>
              ))}
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-[90%] rounded-lg px-3 py-2 text-sm ${
                  msg.role === "user"
                    ? "bg-emerald-600 text-white"
                    : "bg-gray-100 text-gray-800"
                }`}
              >
                <p className="whitespace-pre-wrap text-xs leading-relaxed">{msg.content}</p>
                {msg.citations && msg.citations.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-gray-200 space-y-1">
                    <p className="text-[10px] font-semibold text-gray-500">Sources:</p>
                    {msg.citations.map((c) => (
                      <div key={c.idx} className="flex items-start gap-1">
                        <Badge variant="outline" className="text-[10px] flex-shrink-0 mt-0.5">
                          {c.idx}
                        </Badge>
                        <div className="min-w-0">
                          <p className="text-[10px] text-gray-600 truncate">{c.title}</p>
                          {c.url && (
                            <a
                              href={c.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-[10px] text-emerald-600 hover:underline flex items-center gap-0.5"
                            >
                              <ExternalLink className="w-2.5 h-2.5" />
                              Source
                            </a>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-lg px-4 py-3">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.15s]" />
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.3s]" />
                </div>
              </div>
            </div>
          )}
          <div ref={scrollRef} />
        </div>
      </ScrollArea>

      <div className="p-3 border-t">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            sendMessage();
          }}
          className="flex gap-2"
        >
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about ESG risks..."
            className="text-xs h-9"
            disabled={loading}
          />
          <Button type="submit" size="icon" className="h-9 w-9 flex-shrink-0" disabled={loading || !input.trim()}>
            <Send className="w-4 h-4" />
          </Button>
        </form>
      </div>
    </div>
  );
}
