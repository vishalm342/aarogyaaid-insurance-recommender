# PRD — AarogyaAid Insurance Recommendation Platform

## 1. User Profile
Primary user: A first-generation insurance buyer in India, aged 28–55,
with low-to-moderate health literacy. They often have one or more
pre-existing conditions (Diabetes, Hypertension) and are making this
decision under emotional stress — sometimes disclosing a chronic illness
digitally for the first time. Their biggest fear is not the premium cost,
but hidden exclusions and claim rejection at the worst possible moment.

## 2. Problem Statement
Selecting health insurance in India today means opening 30-page PDFs,
decoding jargon like "sub-limits" and "co-pay", and comparing plans
with no personalisation. Standard comparison sites rank by price, not
by fit. A 45-year-old diabetic patient in a Tier-2 city has completely
different risk exposure than a 25-year-old in a metro — yet both see the
same table. This platform solves that by building an AI agent that reads
the actual policy documents, understands the user's health and financial
profile, and explains its reasoning in plain language.

## 3. Feature Priority

| Priority | Feature | Justification |
|---|---|---|
| 1 | Grounded RAG pipeline + recommendation engine | Carries 65% of score (Approach 35% + Document Intelligence 30%). An AI that hallucinates insurance data is dangerous. |
| 2 | Empathetic 3-section recommendation output + chat explainer | Directly maps to Transparency & Explainability (20%). |
| 3 | 6-field profile form (exactly as spec) | Core input without which nothing works. |
| 4 | Admin panel (upload/edit/delete with vector store sync) | Required deliverable; deletion from vector store is a hard requirement. |
| 5 | README + unit test | Code Quality (15%). Easy points, often missed. |

## 4. Recommendation Logic (Plain English)

The engine processes the 6 profile fields in a deliberate sequence:

1. **Pre-existing Conditions** — First pass filter. Policies with hard
   exclusions for the user's condition are flagged, not hidden. The agent
   surfaces the exclusion explicitly rather than recommending a policy
   that will reject their claim.

2. **Annual Income / Financial Band** — Sets the affordability ceiling.
   Policies with annual premiums exceeding ~4% of stated income are
   deprioritised unless no better option exists, in which case the agent
   explains the trade-off.

3. **Age** — Determines premium bracket sensitivity and waiting period
   tolerance. A 58-year-old cannot afford a 48-month waiting period for
   a cardiac condition they already have. Age cross-references with
   pre-existing conditions to flag this risk.

4. **City / Tier** — Adjusts network hospital availability weighting.
   A Tier-3 user with a cashless claim policy is only as covered as the
   hospitals in their network. The agent surfaces network density as a
   named factor.

5. **Lifestyle** — Adjusts OPD coverage weighting. Active/Athlete users
   benefit more from OPD cover; Sedentary users are prioritised for
   hospitalisation cover depth.

6. **Full Name** — Used throughout to personalise responses. The agent
   addresses the user by name in the "Why This Policy" explanation,
   making the output feel like advice from a person, not a query result.

The Suitability Score (shown in the Peer Comparison Table) is a
weighted calculation: Exclusion Match (40%) + Affordability Fit (30%) +
Network Availability (20%) + Waiting Period Tolerance (10%).

## 5. Assumptions
- Policy documents uploaded by admin are accurate and current.
- Users understand their own diagnosed medical history.
- "Annual Income" is self-reported and used only for affordability filtering.
- All policies are assumed to be individual (not family floater) for v1.
- Network hospital data is extracted from the policy PDF text, not from
  a live insurer API.

## 6. Out of Scope (v1)
- Live policy data scraping from insurer websites.
- Payment gateway or actual policy purchase flow.
- Family floater or group insurance recommendations.
- Multi-language support (English only for this prototype).
- User authentication on the portal (admin panel is authenticated; user side is not).