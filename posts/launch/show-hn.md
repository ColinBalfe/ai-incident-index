<!-- DRAFT. Nothing here posts itself. Numbers as of Oct 26, 2026, 15:25 ET; recheck them against https://warningshots.ai/index/?utm_source=hackernews&utm_medium=social&utm_campaign=launch&utm_content=show-hn before posting. Licence line pending Colin's decision. -->

# Show HN

**Title:** Show HN: An open, scored index of AI incidents, updated three times a day

**URL:** https://warningshots.ai/?utm_source=hackernews&utm_medium=social&utm_campaign=launch&utm_content=show-hn

**First comment:**

I built Warning Shots to track AI incidents the way a newsroom tracks a beat: every significant one since 2023 (160 so far), each scored 0–100 by a published formula (harm, reach, autonomy, novelty, irreversibility) and linked to its sources.

Two things the data shows: severe incidents went from 3 to 13 in a year, and in 42% of this year's real-world cases the AI system itself did the acting, rather than a person using it as a tool.

Things I tried to get right:
- Retractions run as big as the claims. When Palo Alto's Unit 42 withdrew a report this week, the correction went on the front page in the same column.
- Proof is graded: Tried (attempts logged), Proven (a test system broken into), Hit (a real victim confirmed). They're never blurred.
- Dated forecasts that are never edited after they resolve; misses stay up.
- The data is open: https://warningshots.ai/data/incidents.json and .csv. The formula is on the page.

Built as a static site from JSON with Python and Playwright. Feedback on the scoring rubric especially welcome.
