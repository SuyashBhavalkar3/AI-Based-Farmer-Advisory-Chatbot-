import { useEffect, useState } from "react";
import { Plus, MessageSquare, LogOut, Wheat } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ThemeToggle } from "./ThemeToggle";
import { useAuth } from "@/hooks/useAuth";
import { conversationsAPI } from "@/services/api";
import { cn } from "@/lib/utils";

interface Conversation {
  id: number;
  title: string;
  updated_at: string;
}

interface ChatSidebarProps {
  activeConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onNewConversation: () => void;
  language: string;
  onLanguageChange: (lang: string) => void;
}

export function ChatSidebar({
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  language,
  onLanguageChange,
}: ChatSidebarProps) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const { signOut } = useAuth();

  const fetchConversations = async () => {
    try {
      setLoading(true);
      const response = await conversationsAPI.list();
      setConversations(response.conversations || []);
    } catch (error) {
      console.error("Failed to fetch conversations:", error);
      setConversations([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConversations();
    // Poll for new conversations every 5 seconds
    const interval = setInterval(fetchConversations, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex h-full w-64 flex-col border-r border-border bg-sidebar-background">
      <div className="flex items-center justify-between border-b border-sidebar-border p-3">
        <h2 className="text-sm font-semibold text-sidebar-foreground">Conversations</h2>
        <ThemeToggle />
      </div>

      <div className="p-3">
        <Button onClick={onNewConversation} className="w-full gap-2" size="sm">
          <Plus className="h-4 w-4" />
          New Conversation
        </Button>
      </div>

      <ScrollArea className="flex-1 px-2">
        {loading ? (
          <div className="flex items-center justify-center py-4 text-sm text-muted-foreground">
            Loading...
          </div>
        ) : conversations.length === 0 ? (
          <div className="flex items-center justify-center py-4 text-sm text-muted-foreground">
            No conversations yet
          </div>
        ) : (
          conversations.map((conv) => (
            <button
              key={conv.id}
              onClick={() => onSelectConversation(conv.id.toString())}
              className={cn(
                "mb-1 flex w-full items-center gap-2 rounded-md px-3 py-2 text-left text-sm transition-colors",
                activeConversationId === conv.id.toString()
                  ? "bg-sidebar-accent text-sidebar-accent-foreground"
                  : "text-sidebar-foreground hover:bg-sidebar-accent/50"
              )}
            >
              <MessageSquare className="h-4 w-4 shrink-0" />
              <span className="truncate">{conv.title}</span>
            </button>
          ))
        )}
      </ScrollArea>

      <div className="space-y-2 border-t border-sidebar-border p-3">
        <Select value={language} onValueChange={onLanguageChange}>
          <SelectTrigger className="h-8 text-xs">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="en">English</SelectItem>
            <SelectItem value="hi">हिन्दी (Hindi)</SelectItem>
            <SelectItem value="mr">मराठी (Marathi)</SelectItem>
          </SelectContent>
        </Select>
        <Link to="/schemes" className="w-full">
          <Button variant="ghost" size="sm" className="w-full justify-start gap-2 text-muted-foreground hover:bg-green-50 dark:hover:bg-emerald-900/30 hover:text-green-700 dark:hover:text-green-400 transition-colors">
            <Wheat className="h-4 w-4" />
            Schemes
          </Button>
        </Link>
        <Button variant="ghost" size="sm" className="w-full justify-start gap-2 text-muted-foreground hover:bg-red-50 dark:hover:bg-red-900/30 hover:text-red-700 dark:hover:text-red-400 transition-colors" onClick={signOut}>
          <LogOut className="h-4 w-4" />
          Sign Out
        </Button>
      </div>
    </div>
  );
}
