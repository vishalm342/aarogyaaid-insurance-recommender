"use client";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface Policy {
  policy_name: string;
  insurer: string;
  [key: string]: string | number | boolean | null;
}

interface Profile {
  full_name?: string;
  [key: string]: string | number | boolean | string[] | null | undefined;
}

export default function Chat() {
  const router = useRouter();
  const bottomRef = useRef<HTMLDivElement>(null);
  
  const [policy, setPolicy] = useState<Policy | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [initialized, setInitialized] = useState(false);

  useEffect(() => {
    if (initialized) return;
    
    const p = sessionStorage.getItem("selected_policy");
    const prof = sessionStorage.getItem("profile");
    
    if (!p) { 
      router.push("/results"); 
      return; 
    }

    try {
      const parsedPolicy: Policy = JSON.parse(p);
      const parsedProfile: Profile = prof ? JSON.parse(prof) : {};
      
      setPolicy(parsedPolicy);
      setProfile(parsedProfile);
      setMessages([{
        role: "assistant",
        content: `Hi ${parsedProfile.full_name ?? ""}! I can answer questions about **${parsedPolicy.policy_name}** by ${parsedPolicy.insurer}. What would you like to know?`
      }]);
      setInitialized(true);
    } catch (e) {
      console.error("Error parsing session storage:", e);
      router.push("/results");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router, initialized]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async () => {
    if (!input.trim() || loading || !policy) return;
    const userMsg = input.trim();
    setInput("");
    setMessages((m) => [...m, { role: "user", content: userMsg }]);
    setLoading(true);
    
    try {
      const sessionId = sessionStorage.getItem("session_id") || "temp-session-id";

      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          message: userMsg,
          profile: profile ?? {},
          recommended_policy: policy?.policy_name ?? "",
          history: messages.slice(-6).map((m) => ({ role: m.role, content: m.content })),
        }),
      });
      
      if (!res.ok) throw new Error("Failed to reach chat backend");
      
      const data = await res.json();
      const reply = data.reply ?? data.response ?? "I could not generate a response.";
      
      setMessages((m) => [...m, { role: "assistant", content: reply }]);
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((m) => [...m, { role: "assistant", content: "Sorry, could not reach the backend. Please try again." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) { 
      e.preventDefault(); 
      send(); 
    }
  };

  if (!initialized) return <div className="min-h-screen bg-[#f7f6f2]" />;

  return (
    <div className="min-h-screen bg-[#f7f6f2] flex flex-col">
      <header className="bg-white border-b border-[#dcd9d5] px-4 py-3 flex items-center justify-between sticky top-0 z-10">
        <span className="text-[#01696f] font-bold text-lg">AarogyaAid</span>
        {policy && (
          <span className="text-xs bg-[#cedcd8] text-[#01696f] px-3 py-1 rounded-full font-medium">
            {policy.policy_name}
          </span>
        )}
        <button onClick={() => router.push("/results")} className="text-sm text-[#7a7974] hover:text-[#01696f] transition-colors">
          ← Back
        </button>
      </header>

      <div className="flex-1 overflow-y-auto px-4 py-6 flex flex-col gap-4 max-w-2xl mx-auto w-full">
        {messages.map((m, i) => (
          <div key={i} className={`flex gap-3 ${m.role === "user" ? "flex-row-reverse" : ""}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold ${
              m.role === "assistant" ? "bg-[#01696f] text-white" : "bg-[#28251d] text-white"}`}>
              {m.role === "assistant" ? "AI" : "You"}
            </div>
            <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
              m.role === "assistant"
                ? "bg-white border border-[#dcd9d5] text-[#28251d]"
                : "bg-[#01696f] text-white"}`}>
              {m.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-[#01696f] flex items-center justify-center text-white text-xs font-bold">AI</div>
            <div className="bg-white border border-[#dcd9d5] rounded-2xl px-4 py-3 flex items-center gap-2">
              <svg className="animate-spin h-4 w-4 text-[#01696f]" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
              </svg>
              <span className="text-sm text-[#7a7974]">Thinking…</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="bg-white border-t border-[#dcd9d5] px-4 py-4 sticky bottom-0">
        <div className="max-w-2xl mx-auto flex gap-3">
          <textarea rows={1} value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={handleKey}
            placeholder="Ask about coverage, premiums, exclusions…"
            className="flex-1 border border-[#d4d1ca] rounded-xl px-4 py-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-[#01696f] focus:border-transparent" />
          <button onClick={send} disabled={!input.trim() || loading}
            className={`px-5 py-3 rounded-xl text-white font-medium text-sm transition-all ${
              input.trim() && !loading ? "bg-[#01696f] hover:bg-[#0c4e54]" : "bg-[#cedcd8] cursor-not-allowed text-[#7a7974]"}`}>
            Send
          </button>
        </div>
        <p className="text-center text-xs text-[#bab9b4] mt-2">Press Enter to send · Shift+Enter for new line</p>
      </div>
    </div>
  );
}