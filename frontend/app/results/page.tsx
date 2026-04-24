"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function Results() {
  const router = useRouter();
  const [rec, setRec] = useState<any>(null);
  const [profile, setProfile] = useState<any>(null);

  useEffect(() => {
    const r = sessionStorage.getItem("recommendation");
    const p = sessionStorage.getItem("profile");
    if (!r) { router.push("/"); return; }
    setRec(JSON.parse(r));
    if (p) setProfile(JSON.parse(p));
  }, [router]);

  const goToChat = (policy: any) => {
    sessionStorage.setItem("selected_policy", JSON.stringify(policy));
    router.push("/chat");
  };

  if (!rec) return (
    <div className="min-h-screen bg-[#f7f6f2] flex items-center justify-center">
      <div className="flex flex-col items-center gap-3">
        <svg className="animate-spin h-8 w-8 text-[#01696f]" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
        </svg>
        <p className="text-[#7a7974] text-sm">Loading your recommendations…</p>
      </div>
    </div>
  );

  const recommendation = rec.recommendation ?? rec;
  const peers = recommendation.peer_comparison ?? [];
  const coverage = recommendation.coverage_detail ?? null;
  const empathy = recommendation.empathy_note ?? "";
  const why = recommendation.why_this_policy ?? "";

  return (
    <main className="min-h-screen bg-[#f7f6f2] px-4 py-10">
      <div className="max-w-3xl mx-auto flex flex-col gap-8">

        {/* Header */}
        <div className="flex items-center justify-between">
          <span className="text-[#01696f] font-bold text-xl">AarogyaAid</span>
          <button onClick={() => router.push("/")} className="text-sm text-[#7a7974] hover:text-[#01696f] transition-colors">
            ← New Search
          </button>
        </div>

        {/* Empathy Note */}
        {empathy && (
          <div className="bg-[#cedcd8] border border-[#01696f]/20 rounded-2xl px-6 py-5">
            <p className="text-sm text-[#0c4e54] leading-relaxed">{empathy}</p>
          </div>
        )}

        {/* Peer Comparison Table */}
        {peers.length > 0 && (
          <div className="bg-white rounded-2xl shadow-sm border border-[#dcd9d5] overflow-hidden">
            <div className="px-6 py-4 border-b border-[#dcd9d5]">
              <h2 className="font-semibold text-[#28251d] text-lg">Policy Comparison</h2>
              <p className="text-xs text-[#7a7974] mt-0.5">Ranked by suitability for your profile</p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-[#f7f6f2] text-[#7a7974] text-xs uppercase tracking-wide">
                    <th className="px-4 py-3 text-left">Policy</th>
                    <th className="px-4 py-3 text-left">Insurer</th>
                    <th className="px-4 py-3 text-right">Premium/yr</th>
                    <th className="px-4 py-3 text-right">Cover</th>
                    <th className="px-4 py-3 text-left">Waiting</th>
                    <th className="px-4 py-3 text-right">Score</th>
                    <th className="px-4 py-3"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#f3f0ec]">
                  {peers.map((p: any, i: number) => (
                    <tr key={i} className={i === 0 ? "bg-[#f7fffe]" : "bg-white"}>
                      <td className="px-4 py-3 font-medium text-[#28251d]">
                        {i === 0 && <span className="inline-block bg-[#01696f] text-white text-xs px-2 py-0.5 rounded-full mr-2">Best</span>}
                        {p.policy_name}
                      </td>
                      <td className="px-4 py-3 text-[#7a7974]">{p.insurer}</td>
                      <td className="px-4 py-3 text-right text-[#28251d]">₹{p.premium_per_year}</td>
                      <td className="px-4 py-3 text-right text-[#28251d]">₹{p.cover_amount}</td>
                      <td className="px-4 py-3 text-[#7a7974]">{p.waiting_period}</td>
                      <td className="px-4 py-3 text-right">
                        <span className="inline-block bg-[#cedcd8] text-[#01696f] font-semibold text-xs px-3 py-1 rounded-full">
                          {/* If the score already includes '/10', print it. Otherwise, append it. */}
                          {String(p.suitability_score).includes("/10") ? p.suitability_score : `${p.suitability_score}/10`}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <button onClick={() => goToChat(p)}
                          className="text-xs bg-[#01696f] text-white px-3 py-1.5 rounded-lg hover:bg-[#0c4e54] transition-colors whitespace-nowrap">
                          Ask AI →
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Coverage Detail */}
        {coverage && (
          <div className="bg-white rounded-2xl shadow-sm border border-[#dcd9d5] px-6 py-5 flex flex-col gap-4">
            <h2 className="font-semibold text-[#28251d] text-lg">
              Coverage Detail — <span className="text-[#01696f]">{coverage.policy_name}</span>
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <p className="text-xs font-semibold text-[#7a7974] uppercase tracking-wide mb-2">Inclusions</p>
                <ul className="flex flex-col gap-1.5">
                  {(coverage.inclusions ?? []).map((item: string, i: number) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-[#28251d]">
                      <span className="text-[#01696f] mt-0.5">✓</span>{item}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="text-xs font-semibold text-[#7a7974] uppercase tracking-wide mb-2">Exclusions</p>
                <ul className="flex flex-col gap-1.5">
                  {(coverage.exclusions ?? []).map((item: string, i: number) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-[#28251d]">
                      <span className="text-red-400 mt-0.5">✕</span>{item}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
            {(coverage.sub_limits?.length > 0 || coverage.co_pay) && (
              <div className="flex flex-wrap gap-3 pt-2 border-t border-[#f3f0ec]">
                {coverage.co_pay && (
                  <span className="text-xs bg-[#f7f6f2] border border-[#dcd9d5] rounded-full px-3 py-1 text-[#28251d]">
                    <strong>Co-pay</strong> (the % of each claim you pay): {coverage.co_pay}
                  </span>
                )}
                {coverage.claim_type && (
                  <span className="text-xs bg-[#f7f6f2] border border-[#dcd9d5] rounded-full px-3 py-1 text-[#28251d]">
                    <strong>Claim type:</strong> {coverage.claim_type}
                  </span>
                )}
                {(coverage.sub_limits ?? []).map((s: string, i: number) => (
                  <span key={i} className="text-xs bg-[#f7f6f2] border border-[#dcd9d5] rounded-full px-3 py-1 text-[#28251d]">{s}</span>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Why This Policy */}
        {why && (
          <div className="bg-white rounded-2xl shadow-sm border border-[#dcd9d5] px-6 py-5">
            <h2 className="font-semibold text-[#28251d] text-lg mb-3">Why This Policy For You</h2>
            <p className="text-sm text-[#28251d] leading-relaxed">{why}</p>
          </div>
        )}

        {/* CTA */}
        {peers.length > 0 && (
          <button onClick={() => goToChat(peers[0])}
            className="w-full py-4 bg-[#01696f] hover:bg-[#0c4e54] text-white font-semibold rounded-2xl transition-all text-base">
            Chat with AI about {peers[0]?.policy_name} →
          </button>
        )}
      </div>
    </main>
  );
}