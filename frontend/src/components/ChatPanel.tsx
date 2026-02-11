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
      <div className="flex h-full flex-col bg-gradient-to-b from-white/50 to-green-50/30 dark:from-slate-900/50 dark:to-emerald-900/20">
        <div className="flex flex-1 flex-col items-center justify-center gap-8 p-8">
          <div className="flex h-20 w-20 items-center justify-center rounded-3xl bg-gradient-to-br from-green-500 to-emerald-600 shadow-2xl">
            <Leaf className="h-10 w-10 text-white" />
          </div>
          <div className="text-center max-w-md">
            <h2 className="text-3xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
              Farmer Legal & Policy Assistant
            </h2>
            <p className="mt-3 text-base text-gray-600 dark:text-gray-300 leading-relaxed">
              Ask about government schemes, crop insurance, subsidies, and land laws
            </p>
          </div>
          <div className="grid w-full max-w-lg gap-3">
            {STARTER_QUESTIONS.map((q, idx) => (
              <button
                key={q}
                onClick={() => {
                  setInput(q);
                }}
                className="group rounded-xl border-2 border-green-200 dark:border-emerald-800 bg-white dark:bg-slate-800/50 p-4 text-left text-sm font-medium text-gray-800 dark:text-gray-200 transition-all hover:border-green-500 hover:bg-green-50 dark:hover:bg-emerald-900/30 hover:shadow-lg hover:-translate-y-1 transform"
                style={{
                  animation: `slideIn 0.5s ease-out ${idx * 0.1}s backwards`
                }}
              >
                <p className="group-hover:text-green-700 dark:group-hover:text-green-400 transition-colors">{q}</p>
              </button>
            ))}
          </div>
        </div>
        <div className="border-t-2 border-green-100 dark:border-emerald-900/30 bg-white dark:bg-slate-900/50 backdrop-blur p-4">
          <form onSubmit={handleSubmit} className="flex gap-2 max-w-4xl mx-auto">
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
              className="border-2 border-green-200 dark:border-emerald-800 hover:border-green-500 hover:bg-green-50 dark:hover:bg-emerald-900/30 rounded-lg"
            >
              <Upload className="h-5 w-5 text-green-600" />
            </Button>
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about agriculture policies, schemes, laws..."
              className="min-h-[45px] max-h-[120px] resize-none border-2 border-green-200 dark:border-emerald-800 rounded-lg focus:border-green-500 focus:ring-2 focus:ring-green-200 dark:focus:ring-green-900 transition-all px-4 py-3"
              rows={1}
            />
            <Button
              type="submit"
              size="icon"
              disabled={!input.trim() || isLoading}
              className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white rounded-lg shadow-lg hover:shadow-xl transition-all"
            >
              {isLoading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <Send className="h-5 w-5" />
              )}
            </Button>
          </form>
        </div>
        <style>{`
          @keyframes slideIn {
            from {
              opacity: 0;
              transform: translateY(20px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col bg-gradient-to-b from-white/40 to-green-50/20 dark:from-slate-900/40 dark:to-emerald-900/10">
      <ScrollArea className="flex-1 p-6" ref={scrollRef as any}>
        <div className="mx-auto max-w-3xl space-y-5">
          {loadingMessages ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-6 w-6 animate-spin text-green-600" />
            </div>
          ) : messages.length === 0 ? (
            <div className="flex items-center justify-center py-12 text-sm text-gray-500 dark:text-gray-400">
              No messages yet. Start by typing a question below.
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div
                key={msg.id}
                className={cn("flex gap-4 animate-fadeIn", msg.role === "user" ? "justify-end" : "justify-start")}
                style={{
                  animation: `fadeIn 0.3s ease-out`
                }}
              >
                {msg.role === "assistant" && (
                  <div className="flex-shrink-0 flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-green-500 to-emerald-600">
                    <Leaf className="h-4 w-4 text-white" />
                  </div>
                )}
                <div
                  className={cn(
                    "max-w-[85%] rounded-2xl px-5 py-4 text-sm shadow-md transition-all hover:shadow-lg",
                    msg.role === "user"
                      ? "bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-3xl rounded-br-sm"
                      : "bg-white dark:bg-slate-800/80 text-gray-900 dark:text-gray-100 border-2 border-green-100 dark:border-emerald-900/50 rounded-3xl rounded-tl-sm"
                  )}
                >
                  {msg.role === "assistant" ? (
                    <div className="prose prose-sm dark:prose-invert max-w-none text-gray-900 dark:text-gray-100 prose-p:m-0 prose-li:m-0 prose-ul:m-0 prose-ol:m-0">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  ) : (
                    <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                  )}
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex justify-start gap-4 animate-fadeIn">
              <div className="flex-shrink-0 flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-green-500 to-emerald-600">
                <Leaf className="h-4 w-4 text-white" />
              </div>
              <div className="rounded-2xl rounded-tl-sm border-2 border-green-100 dark:border-emerald-900/50 bg-white dark:bg-slate-800/80 px-5 py-4">
                <Loader2 className="h-5 w-5 animate-spin text-green-600" />
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      <div className="border-t-2 border-green-100 dark:border-emerald-900/30 bg-white dark:bg-slate-900/50 backdrop-blur p-4">
        <form onSubmit={handleSubmit} className="mx-auto max-w-3xl flex gap-3">
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
            className="border-2 border-green-200 dark:border-emerald-800 hover:border-green-500 hover:bg-green-50 dark:hover:bg-emerald-900/30 rounded-lg h-11 w-11 flex-shrink-0 transition-all"
          >
            <Upload className="h-5 w-5 text-green-600" />
          </Button>
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about agriculture policies, schemes, laws..."
            className="min-h-[45px] max-h-[120px] resize-none border-2 border-green-200 dark:border-emerald-800 rounded-lg focus:border-green-500 focus:ring-2 focus:ring-green-200 dark:focus:ring-green-900 transition-all px-4 py-3 dark:bg-slate-800/50"
            rows={1}
          />
          <Button 
            type="submit" 
            size="icon" 
            disabled={!input.trim() || isLoading}
            className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white rounded-lg shadow-lg hover:shadow-xl transition-all h-11 w-11 flex-shrink-0"
          >
            {isLoading ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <Send className="h-5 w-5" />
            )}
          </Button>
        </form>
      </div>
      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
}
