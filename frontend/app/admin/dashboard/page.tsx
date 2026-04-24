"use client";
import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

interface Policy {
  policy_id: string;
  policy_name: string;
  insurer: string;
  chunk_count?: number;
}

export default function AdminDashboard() {
  const router = useRouter();
  const fileRef = useRef<HTMLInputElement>(null);
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [toast, setToast] = useState<{ msg: string; type: "success" | "error" } | null>(null);
  const [uploadForm, setUploadForm] = useState({ policy_name: "", insurer: "" });
  const [confirmDelete, setConfirmDelete] = useState<{ id: string; name: string } | null>(null);

  const showToast = (msg: string, type: "success" | "error") => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3500);
  };

  const fetchPolicies = async () => {
    try {
      const res = await api.get("/api/admin/policies");
      setPolicies(res.data);
    } catch {
      showToast("Failed to load policies", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem("admin_token");
    if (!token) { router.push("/admin"); return; }
    fetchPolicies();
  }, []);

  const upload = async (e: React.FormEvent) => {
    e.preventDefault();
    const file = fileRef.current?.files?.[0];
    if (!file) { showToast("Please select a file", "error"); return; }
    setUploading(true);
    const fd = new FormData();
    fd.append("file", file);
    fd.append("policy_name", uploadForm.policy_name);
    fd.append("insurer", uploadForm.insurer);
    try {
      await api.post("/api/admin/upload", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      showToast(`✓ ${uploadForm.policy_name} ingested successfully`, "success");
      setUploadForm({ policy_name: "", insurer: "" });
      if (fileRef.current) fileRef.current.value = "";
      fetchPolicies();
    } catch {
      showToast("Upload failed. Try again.", "error");
    } finally {
      setUploading(false);
    }
  };

  const deletePolicy = async () => {
    if (!confirmDelete) return;
    try {
      await api.delete(`/api/admin/policies/${confirmDelete.id}`);
      showToast(`Deleted ${confirmDelete.name}`, "success");
      setConfirmDelete(null);
      fetchPolicies();
    } catch {
      showToast("Delete failed", "error");
    }
  };

  return (
    <div className="min-h-screen bg-[#f7f6f2]">
      {toast && (
        <div className={`fixed top-4 right-4 z-50 px-4 py-3 rounded-xl shadow-lg text-sm font-medium ${
          toast.type === "success" ? "bg-[#01696f] text-white" : "bg-red-500 text-white"}`}>
          {toast.msg}
        </div>
      )}

      {confirmDelete && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center px-4">
          <div className="bg-white rounded-2xl p-6 max-w-sm w-full shadow-xl flex flex-col gap-4">
            <h3 className="font-semibold text-[#28251d] text-lg">Delete Policy?</h3>
            <p className="text-sm text-[#7a7974]">
              Permanently deletes <strong>{confirmDelete.name}</strong> and all its chunks from the vector store.
            </p>
            <div className="flex gap-3">
              <button onClick={() => setConfirmDelete(null)}
                className="flex-1 py-2.5 rounded-xl border border-[#d4d1ca] text-sm hover:bg-[#f7f6f2] transition-all">
                Cancel
              </button>
              <button onClick={deletePolicy}
                className="flex-1 py-2.5 rounded-xl bg-red-500 text-white text-sm font-medium hover:bg-red-600 transition-all">
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      <header className="bg-white border-b border-[#dcd9d5] px-6 py-4 flex items-center justify-between">
        <span className="text-[#01696f] font-bold text-xl">AarogyaAid</span>
        <span className="text-sm text-[#7a7974]">Admin Dashboard</span>
        <button onClick={() => { localStorage.removeItem("admin_token"); router.push("/admin"); }}
          className="text-sm text-[#7a7974] hover:text-[#01696f] transition-colors">
          Sign out →
        </button>
      </header>

      <div className="max-w-3xl mx-auto px-4 py-8 flex flex-col gap-8">
        <div className="bg-white rounded-2xl shadow-sm border border-[#dcd9d5] p-6 flex flex-col gap-4">
          <h2 className="font-semibold text-[#28251d] text-lg">Upload New Policy</h2>
          <form onSubmit={upload} className="flex flex-col gap-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium text-[#28251d]">Policy Name *</label>
                <input value={uploadForm.policy_name}
                  onChange={(e) => setUploadForm((f) => ({ ...f, policy_name: e.target.value }))}
                  placeholder="e.g. Star Health Senior Care"
                  className="border border-[#d4d1ca] rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#01696f]" required />
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium text-[#28251d]">Insurer *</label>
                <input value={uploadForm.insurer}
                  onChange={(e) => setUploadForm((f) => ({ ...f, insurer: e.target.value }))}
                  placeholder="e.g. Star Health Insurance"
                  className="border border-[#d4d1ca] rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#01696f]" required />
              </div>
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium text-[#28251d]">Policy File (.txt or .pdf) *</label>
              <input ref={fileRef} type="file" accept=".txt,.pdf"
                className="border border-[#d4d1ca] rounded-lg px-3 py-2 text-sm file:mr-3 file:py-1 file:px-3 file:rounded-full file:border-0 file:text-xs file:bg-[#cedcd8] file:text-[#01696f] cursor-pointer" required />
            </div>
            <button type="submit" disabled={uploading}
              className={`w-full py-3 rounded-xl text-white font-medium text-sm transition-all ${
                uploading ? "bg-[#cedcd8] cursor-not-allowed text-[#7a7974]" : "bg-[#01696f] hover:bg-[#0c4e54]"}`}>
              {uploading ? "Ingesting into vector store…" : "Upload & Ingest →"}
            </button>
          </form>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-[#dcd9d5] overflow-hidden">
          <div className="px-6 py-4 border-b border-[#dcd9d5] flex items-center justify-between">
            <h2 className="font-semibold text-[#28251d] text-lg">Ingested Policies</h2>
            <span className="text-xs bg-[#f7f6f2] border border-[#dcd9d5] px-2 py-1 rounded-full text-[#7a7974]">
              {policies.length} total
            </span>
          </div>
          {loading ? (
            <div className="px-6 py-12 flex items-center justify-center">
              <svg className="animate-spin h-6 w-6 text-[#01696f]" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
              </svg>
            </div>
          ) : policies.length === 0 ? (
            <div className="px-6 py-12 flex flex-col items-center gap-2">
              <p className="text-[#7a7974] text-sm">No policies ingested yet. Upload one above.</p>
            </div>
          ) : (
            <ul className="divide-y divide-[#f3f0ec]">
              {policies.map((p) => (
                <li key={p.policy_id} className="px-6 py-4 flex items-center justify-between gap-4">
                  <div className="flex flex-col gap-0.5 min-w-0">
                    <span className="font-medium text-[#28251d] text-sm truncate">{p.policy_name}</span>
                    <span className="text-xs text-[#7a7974]">{p.insurer} · {p.policy_id}</span>
                  </div>
                  {p.chunk_count && (
                    <span className="text-xs bg-[#cedcd8] text-[#01696f] px-2 py-1 rounded-full whitespace-nowrap">
                      {p.chunk_count} chunks
                    </span>
                  )}
                  <button onClick={() => setConfirmDelete({ id: p.policy_id, name: p.policy_name })}
                    className="text-[#7a7974] hover:text-red-500 transition-colors p-1.5 rounded-lg hover:bg-red-50 flex-shrink-0">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6" />
                    </svg>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}