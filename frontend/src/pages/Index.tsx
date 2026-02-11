import { useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { ChatSidebar } from "@/components/ChatSidebar";
import { ChatPanel } from "@/components/ChatPanel";
import { Loader2 } from "lucide-react";

export default function Index() {
  const { user, loading } = useAuth();
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [language, setLanguage] = useState("en");

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!user) return <Navigate to="/login" replace />;

  return (
    <div className="flex h-screen bg-background">
      <ChatSidebar
        activeConversationId={activeConversationId}
        onSelectConversation={setActiveConversationId}
        onNewConversation={() => setActiveConversationId(null)}
        language={language}
        onLanguageChange={setLanguage}
      />
      <main className="flex-1">
        <ChatPanel
          conversationId={activeConversationId}
          language={language}
          onConversationCreated={setActiveConversationId}
        />
      </main>
    </div>
  );
}
