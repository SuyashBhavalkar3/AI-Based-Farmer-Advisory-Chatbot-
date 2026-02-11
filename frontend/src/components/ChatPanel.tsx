import { useEffect, useRef, useState } from "react";
import { Send, Upload, Loader2, Leaf } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useAuth } from "@/hooks/useAuth";
import { conversationsAPI, advisoryAPI } from "@/services/api";
import { useToast } from "@/hooks/use-toast";
import ReactMarkdown from "react-markdown";
import { cn } from "@/lib/utils";

interface Message {
  id: number;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

interface ChatPanelProps {
  conversationId: string | null;
  language: string;
  onConversationCreated: (id: string) => void;
}

const STARTER_QUESTIONS = [
  "What government schemes are available for small farmers?",
  "How does Pradhan Mantri Fasal Bima Yojana work?",
  "What are the rules for agricultural land transfer?",
  "How can I apply for Kisan Credit Card?",
];

export function ChatPanel({ conversationId, language, onConversationCreated }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { user } = useAuth();
  const { toast } = useToast();

  // Fetch messages when conversation ID changes
  useEffect(() => {
    if (!conversationId) {
      setMessages([]);
      return;
    }
    const fetchMessages = async () => {
      try {
        setLoadingMessages(true);
        const response = await conversationsAPI.get(parseInt(conversationId));
        setMessages(response.messages || []);
      } catch (error) {
        console.error("Failed to fetch messages:", error);
        setMessages([]);
      } finally {
        setLoadingMessages(false);
      }
    };
    fetchMessages();
  }, [conversationId]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const createConversation = async (): Promise<number> => {
    try {
      const response = await conversationsAPI.create("New Conversation", language);
      const newConvId = response.id;
      onConversationCreated(newConvId.toString());
      return newConvId;
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create conversation",
        variant: "destructive",
      });
      throw error;
    }
  };

  const sendMessage = async (text: string, file?: File) => {
    if (!text.trim() && !file) return;
    
    console.log("[CHAT] sendMessage called with:", { text, hasFile: !!file });
    setIsLoading(true);

    try {
      const convId =
        conversationId ? parseInt(conversationId) : await createConversation();

      console.log("[CHAT] Using conversation ID:", convId);

      // Add user message to UI immediately
      const userMessage: Message = {
        id: Date.now(),
        role: "user",
        content: text,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setInput("");

      // Call API to get advisory response
      console.log("[CHAT] Calling advisoryAPI.ask with:", {
        question: text,
        conversationId: convId,
        language: language
      });
      
      let response;
      if (file) {
        console.log("[CHAT] Using askWithDocument");
        response = await advisoryAPI.askWithDocument(text, convId, language, file);
      } else {
        console.log("[CHAT] Using ask");
        response = await advisoryAPI.ask(text, convId, language);
      }

      console.log("[CHAT] Got response:", response);
      console.log("[CHAT] Response structure:", {
        hasData: !!response?.data,
        hasResponse: !!response?.data?.response,
        responseValue: response?.data?.response || response?.response
      });

      // Add assistant message to UI
      const assistantMessage: Message = {
        id: Date.now() + 1,
        role: "assistant",
        content: response.data?.response || response.response || "No response",
        created_at: new Date().toISOString(),
      };
      console.log("[CHAT] Adding assistant message:", assistantMessage);
      setMessages((prev) => [...prev, assistantMessage]);

      // Refresh conversation to get all messages from server
      if (conversationId) {
        const updatedConv = await conversationsAPI.get(convId);
        setMessages(updatedConv.messages || []);
      }
    } catch (error: any) {
      const errorMessage = error?.message || "Failed to send message";
      console.error("[CHAT] Error details:", error);
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
      console.error("Send message error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    const text = input;
    sendMessage(text);
  };

  const handlePdfUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith(".pdf")) {
      toast({
        title: "Invalid file",
        description: "Please upload a PDF file.",
        variant: "destructive",
      });
      return;
    }

    // Validate file size (limit to 50MB)
    const maxSizeMB = 50;
    if (file.size > maxSizeMB * 1024 * 1024) {
      toast({
        title: "File too large",
        description: `Please upload a PDF smaller than ${maxSizeMB}MB`,
        variant: "destructive",
      });
      return;
    }

    setIsUploading(true);
    try {
      const message = `I uploaded a PDF: ${file.name}. Please analyze it.`;
      await sendMessage(message, file);
      toast({
        title: "Success",
        description: "PDF uploaded and analyzed successfully",
      });
    } catch (error: any) {
      toast({
        title: "Upload failed",
        description: error?.message || "Failed to upload PDF",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Empty state - no conversation
  if (!conversationId && messages.length === 0) {
    return (
      <div className="flex h-full flex-col">
        <div className="flex flex-1 flex-col items-center justify-center gap-6 p-8">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
            <Leaf className="h-8 w-8 text-primary" />
          </div>
          <div className="text-center">
            <h2 className="text-xl font-semibold text-foreground">
              Farmer Legal & Policy Assistant
            </h2>
            <p className="mt-2 text-sm text-muted-foreground">
              Ask about government schemes, crop insurance, subsidies, and land laws
            </p>
          </div>
          <div className="grid w-full max-w-lg gap-2">
            {STARTER_QUESTIONS.map((q) => (
              <button
                key={q}
                onClick={() => {
                  setInput(q);
                }}
                className="rounded-lg border border-border bg-card p-3 text-left text-sm text-card-foreground transition-colors hover:bg-accent"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
        <div className="border-t border-border p-4">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <input
              type="file"
              ref={fileInputRef}
              accept=".pdf"
              onChange={handlePdfUpload}
              className="hidden"
            />
            <Button
              type="button"
              variant="outline"
              size="icon"
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
            >
              <Upload className="h-4 w-4" />
            </Button>
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about agriculture policies, schemes, laws..."
              className="min-h-[40px] max-h-[120px] resize-none"
              rows={1}
            />
            <Button
              type="submit"
              size="icon"
              disabled={!input.trim() || isLoading}
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      <ScrollArea className="flex-1 p-4" ref={scrollRef as any}>
        <div className="mx-auto max-w-2xl space-y-4">
          {loadingMessages ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          ) : messages.length === 0 ? (
            <div className="flex items-center justify-center py-8 text-sm text-muted-foreground">
              No messages yet. Start by typing a question below.
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={cn("flex", msg.role === "user" ? "justify-end" : "justify-start")}
              >
                <div
                  className={cn(
                    "max-w-[80%] rounded-lg px-4 py-3 text-sm",
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-card text-card-foreground border border-border"
                  )}
                >
                  {msg.role === "assistant" ? (
                    <div className="prose prose-sm dark:prose-invert max-w-none">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  ) : (
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  )}
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex justify-start">
              <div className="rounded-lg border border-border bg-card px-4 py-3">
                <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      <div className="border-t border-border p-4">
        <form onSubmit={handleSubmit} className="mx-auto flex max-w-2xl gap-2">
          <input
            type="file"
            ref={fileInputRef}
            accept=".pdf"
            onChange={handlePdfUpload}
            className="hidden"
          />
          <Button
            type="button"
            variant="outline"
            size="icon"
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
          >
            <Upload className="h-4 w-4" />
          </Button>
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about agriculture policies, schemes, laws..."
            className="min-h-[40px] max-h-[120px] resize-none"
            rows={1}
          />
          <Button type="submit" size="icon" disabled={!input.trim() || isLoading}>
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </form>
      </div>
    </div>
  );
}
