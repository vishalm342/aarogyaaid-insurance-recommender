"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

export default function AdminLogin() {
  const router = useRouter();
  const [creds, setCreds] = useState({ username: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const login = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await api.post("/api/admin/login", creds);
      localStorage.setItem("admin_token", res.data.access_token);
      router.push("/admin/dashboard");
    } catch {
      setError("Invalid credentials. Check username and password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#f7f6f2] flex items-center justify-center px-4">
      <div className="w-full max-w-sm bg-white rounded-2xl shadow-md border border-[#dcd9d5] p-8 flex flex-col gap-6">
        <div className="text-center">
          <span className="text-[#01696f] font-bold text-2xl">AarogyaAid</span>
          <p className="text-[#7a7974] text-sm mt-1">Policy Manager · Admin Access</p>
        </div>
        <form onSubmit={login} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-medium text-[#28251d]">Username</label>
            <input type="text" value={creds.username}
              onChange={(e) => setCreds({ ...creds, username: e.target.value })}
              className="border border-[#d4d1ca] rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#01696f] focus:border-transparent"
              placeholder="admin" required />
          </div>
          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-medium text-[#28251d]">Password</label>
            <input type="password" value={creds.password}
              onChange={(e) => setCreds({ ...creds, password: e.target.value })}
              className="border border-[#d4d1ca] rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#01696f] focus:border-transparent"
              placeholder="••••••••" required />
          </div>
          {error && (
            <p className="text-red-500 text-xs bg-red-50 border border-red-100 rounded-lg px-3 py-2">{error}</p>
          )}
          <button type="submit" disabled={loading}
            className={`w-full py-3 rounded-xl text-white font-semibold text-sm transition-all ${
              loading ? "bg-[#cedcd8] cursor-not-allowed text-[#7a7974]" : "bg-[#01696f] hover:bg-[#0c4e54]"}`}>
            {loading ? "Signing in…" : "Sign In"}
          </button>
        </form>
        <button onClick={() => router.push("/")} className="text-center text-xs text-[#7a7974] hover:text-[#01696f] transition-colors">
          ← Back to main app
        </button>
      </div>
    </main>
  );
}