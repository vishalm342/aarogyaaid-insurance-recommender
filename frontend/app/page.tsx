"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

const CONDITIONS = ["Diabetes", "Hypertension", "Asthma", "Cardiac", "None", "Other"];

export default function HomePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    full_name: "",
    age: "",
    lifestyle: "",
    pre_existing_conditions: [] as string[],
    annual_income: "",
    city_tier: "",
  });

  const toggleCondition = (c: string) => {
    setForm((prev) => {
      if (c === "None") return { ...prev, pre_existing_conditions: ["None"] };
      const filtered = prev.pre_existing_conditions.filter((x) => x !== "None");
      return {
        ...prev,
        pre_existing_conditions: filtered.includes(c)
          ? filtered.filter((x) => x !== c)
          : [...filtered, c],
      };
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await fetch("/api/profile/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...form,
          age: parseInt(form.age),
        }),
      });
      
      if (!response.ok) throw new Error("Failed to fetch recommendations");
      
      const data = await response.json();
      sessionStorage.setItem("recommendation", JSON.stringify(data));
      sessionStorage.setItem("profile", JSON.stringify(form));
      router.push("/results");
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const isValid =
    form.full_name.trim() &&
    form.age &&
    form.lifestyle &&
    form.pre_existing_conditions.length > 0 &&
    form.annual_income &&
    form.city_tier;

  return (
    <main className="min-h-screen bg-[#f7f6f2] flex flex-col items-center justify-start px-4 py-10">
      <header className="w-full max-w-2xl flex items-center justify-between mb-10">
        <span className="text-[#01696f] font-bold text-xl">AarogyaAid</span>
        <button onClick={() => router.push("/admin")} className="text-sm text-[#7a7974] hover:text-[#01696f] transition-colors">
          Admin Portal
        </button>
      </header>

      <div className="w-full max-w-2xl text-center mb-8">
        <span className="inline-flex items-center gap-1.5 text-sm text-[#01696f] bg-[#cedcd8] px-3 py-1 rounded-full mb-4">
          AI-Powered Recommendations
        </span>
        <h1 className="text-4xl font-bold text-[#28251d] mb-3 tracking-tight">Find Your Health Insurance</h1>
        <p className="text-[#7a7974] text-base max-w-md mx-auto">
          Answer a few questions and get personalised policy matches — grounded in real policy documents, not guesswork.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="w-full max-w-2xl bg-white rounded-2xl shadow-md border border-[#dcd9d5] p-8 flex flex-col gap-6">
        <div className="grid grid-cols-2 gap-4">
          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-medium text-[#28251d]">Full Name <span className="text-red-500">*</span></label>
            <input type="text" placeholder="e.g. Priya Sharma" value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              className="border border-[#d4d1ca] rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#01696f] focus:border-transparent transition-all" required />
          </div>
          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-medium text-[#28251d]">Your Age <span className="text-red-500">*</span></label>
            <input type="number" min={1} max={99} placeholder="e.g. 32" value={form.age}
              onChange={(e) => setForm({ ...form, age: e.target.value })}
              className="border border-[#d4d1ca] rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#01696f] focus:border-transparent transition-all" required />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-medium text-[#28251d]">Lifestyle <span className="text-red-500">*</span></label>
            <select value={form.lifestyle} onChange={(e) => setForm({ ...form, lifestyle: e.target.value })}
              className="border border-[#d4d1ca] rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#01696f] bg-white transition-all" required>
              <option value="">Select lifestyle</option>
              <option value="Sedentary">Sedentary</option>
              <option value="Moderate">Moderate</option>
              <option value="Active">Active</option>
              <option value="Athlete">Athlete</option>
            </select>
          </div>
          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-medium text-[#28251d]">City Tier <span className="text-red-500">*</span></label>
            <select value={form.city_tier} onChange={(e) => setForm({ ...form, city_tier: e.target.value })}
              className="border border-[#d4d1ca] rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#01696f] bg-white transition-all" required>
              <option value="">Select city tier</option>
              <option value="Metro">Metro (Mumbai, Delhi, Bengaluru…)</option>
              <option value="Tier-2">Tier-2 (Pune, Coimbatore, Jaipur…)</option>
              <option value="Tier-3">Tier-3 (Smaller towns)</option>
            </select>
          </div>
        </div>

        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-[#28251d]">Annual Income <span className="text-red-500">*</span></label>
          <div className="grid grid-cols-2 gap-2">
            {[{ label: "Below ₹3L", value: "under_3L" }, { label: "₹3L – ₹8L", value: "3_8L" },
              { label: "₹8L – ₹15L", value: "8_15L" }, { label: "Above ₹15L", value: "above_15L" }].map((opt) => (
              <button key={opt.value} type="button" onClick={() => setForm({ ...form, annual_income: opt.value })}
                className={`py-2.5 px-4 rounded-lg text-sm font-medium border transition-all ${
                  form.annual_income === opt.value
                    ? "bg-[#01696f] text-white border-[#01696f]"
                    : "bg-white text-[#28251d] border-[#d4d1ca] hover:border-[#01696f] hover:text-[#01696f]"}`}>
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-[#28251d]">Pre-existing Conditions <span className="text-red-500">*</span></label>
          <p className="text-xs text-[#7a7974]">Your information is private and helps us find policies that don't exclude your conditions.</p>
          <div className="flex flex-wrap gap-2 mt-1">
            {CONDITIONS.map((c) => (
              <button key={c} type="button" onClick={() => toggleCondition(c)}
                className={`px-4 py-2 rounded-full text-sm font-medium border transition-all ${
                  form.pre_existing_conditions.includes(c)
                    ? "bg-[#01696f] text-white border-[#01696f]"
                    : "bg-white text-[#28251d] border-[#d4d1ca] hover:border-[#01696f] hover:text-[#01696f]"}`}>
                {c}
              </button>
            ))}
          </div>
        </div>

        <button type="submit" disabled={!isValid || loading}
          className={`w-full py-3.5 rounded-xl text-white font-semibold text-base transition-all ${
            isValid && !loading ? "bg-[#01696f] hover:bg-[#0c4e54] active:bg-[#0f3638]" : "bg-[#cedcd8] cursor-not-allowed text-[#7a7974]"}`}>
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
              </svg>
              Analysing your profile…
            </span>
          ) : "Get My Recommendations →"}
        </button>
        <p className="text-xs text-center text-[#7a7974]">Your health data is never stored beyond your session.</p>
      </form>
    </main>
  );
}