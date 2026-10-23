# AI Incident Index — scoring rubric (v1, 2026-10-22)

Severity (0–100) = 0.55 × Harm score + 0.45 × Signal score

Harm score (0–100) = 100 × (0.5·H/5 + 0.25·R/5 + 0.25·I/5)
Signal score (0–100) = 100 × (0.6·A/4 + 0.4·N/5)

H — Harm realized (0–5)
0 none realized (lab/eval, caught pre-deployment)
1 embarrassment, misinformation with little effect, minor inconvenience
2 material harm to a person/org: data loss, <$1M loss, harassment, privacy exposure
3 serious harm: a death, $1M–$100M loss, millions of records exposed, or harm to children
4 multiple deaths, >$100M, critical-infrastructure/cloud outage, state-level espionage
5 mass casualty, >$1B, national-scale disruption

R — Reach (0–5)
0 contained to a lab/eval
1 one person or org
2 dozens
3 thousands
4 millions
5 hundreds of millions / global

A — Autonomy (0–4)
0 human misused AI as a passive tool
1 harm arose from humans relying on AI output
2 AI took a bounded action inside its task
3 AI agent executed multi-step operations largely on its own (whether a human sanctioned the goal or not)
4 AI pursued a goal against its operator's/developer's intent (deception, sabotage, coercion, escape)

N — Novelty / capability signal (0–5)
1 repeat of a known pattern
2 notable escalation in scale or polish of a known pattern
3 first in-the-wild instance of a behavior previously seen only in labs, or first of its kind in a sector
4 first demonstration of a qualitatively new dangerous capability or behavior
5 paradigm-shifting first (e.g., first largely autonomous state-level cyber campaign)

I — Irreversibility (0–5)
0 caught in sandbox / never left the lab
1 trivially reversed (rollback, apology)
2 reversed with effort (restore from backup, refunds)
3 partly irreversible (leaked data, lost money partly recovered)
4 irreversible (death, money gone, secrets stolen)
5 irreversible and propagating (self-spreading, ongoing)

Tiers: <20 Minor · 20–39 Moderate · 40–59 Serious · 60–79 Severe · 80+ Critical
