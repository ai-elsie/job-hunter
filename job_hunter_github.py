import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from datetime import datetime

load_dotenv()
llm = ChatAnthropic(model="claude-haiku-4-5-20251001")

YOUR_BACKGROUND = """
# ── FILL IN YOUR OWN BACKGROUND BELOW ────────────────────────────────────────
# The more detail you provide, the better the AI tailors your outputs.

ABOUT ME STATEMENT:
	•	[Write a 1-2 sentence summary of your professional identity and goal]

FORMER TITLES / POSITIONS HELD:
	•	[e.g. SEO Analyst]
	•	[e.g. Project Manager]

CURRENT GOALS:
	•	[e.g. Transition into Project Management roles]
	•	[e.g. Open to remote or hybrid positions]

CAREER EXPERIENCE:
	•	[Skill Area] ([X] Years, Started [Month Year])

CAREER ROLES & COMPANIES:
	•	[Job Title] for [Company Name]
		-	[Start Date] - [End Date or Current]
		-	[Full Time / Part Time / Freelance]
		-	[Remote / Hybrid / On-site]
		-	[Industry/Niche]

TOOLS USED:
	•	[List every tool you use — e.g. Jira, Asana, Excel, Google Sheets, Figma, Slack]

SOFT SKILLS:
	•	[e.g. Cross-functional collaboration, Stakeholder communication, Deadline management]

HARD SKILLS:
	•	[e.g. Agile delivery, Sprint planning, Backlog governance, Dashboard reporting]

MY FORMAL EDUCATION:
	•	[Degree] from [University], [Graduation Year]

MY INFORMAL EDUCATION IN PROGRESS:
	•	[e.g. PMP Certification — In Progress — Udemy]

MY CAREER PREFERENCES:
	•	[e.g. Remote work, Structured Agile environments, Clear accountability]

ROLES TO TARGET (NOW):
	•	[e.g. Agile Project Manager]
	•	[e.g. Scrum Master]

ROLES TO AVOID:
	•	[e.g. Product Manager, Startup PM roles]
"""


def save_result(label, content):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("job_results.md", "a") as f:
        f.write(f"## [{label}] - {timestamp}\n\n{content}\n\n---\n\n")
    print(f"\nSaved to job_results.md")

# ── Tool 1: Job Relevance Scorer ─────────────────────────────────────────────

def score_job(job_description):
    prompt = PromptTemplate(
        input_variables=["background", "job"],
        template="""You are a career advisor. Score how well this job matches the candidate's background.

Candidate Background:
{background}

Job Description:
{job}

Provide:
1. Match Score: X/10
2. Why it's a good match (2-3 bullet points)
3. Gaps to address (2-3 bullet points)
4. Verdict: APPLY / SKIP / MAYBE

Be direct and honest."""
    )
    result = (prompt | llm).invoke({"background": YOUR_BACKGROUND, "job": job_description}).content
    print(result)
    save_result("JOB SCORE", f"**Job:**\n{job_description}\n\n**Assessment:**\n{result}")
    return result

# ── Tool 2: Resume Tailor ────────────────────────────────────────────────────

BASE_RESUME = """
# ── FILL IN YOUR BASE RESUME BELOW ──────────────────────────────────────────
# This is your standard resume. The tool will tailor it per job description.

EXPERIENCE:

[Company Name] — [Start Date] – [End Date]
[Job Title] — [In-House / Agency] | [Full Time / Part Time] | [Remote / Hybrid]
[One sentence describing the company and its industry.]

[Company Name] — [Start Date] – [End Date]
[Job Title] — [In-House / Agency] | [Full Time / Part Time] | [Remote / Hybrid]
[One sentence describing the company and its industry.]


EDUCATION:
[Degree], [Minor] — [University], [Year]
[Certification or Course In Progress] — [Institution], [Expected Year]

TOOLS:
[Tool 1] | [Tool 2] | [Tool 3] | [Tool 4] | [Tool 5]

SKILLS:
[Skill 1] | [Skill 2] | [Skill 3] | [Skill 4] | [Skill 5]
"""

EXPERIENCE_BANK = [
    # ── ADD YOUR EXPERIENCE BULLETS HERE ───────────────────────────────────────
    # Format: {"employer": "Company Name", "experience": "Your bullet here."}
    # Add as many entries as you like. Group them by employer.
    # These are used as a fact base for generating tailored resume bullets.
    #
    # Example:
    # {"employer": "Acme Corp", "experience": "Led cross-functional sprint planning for a team of 8 engineers, reducing blockers by 30%."},
    # {"employer": "Acme Corp", "experience": "Increased organic traffic by 25% by executing keyword strategy and technical SEO improvements."},
    #
    # ── ADD NEW EXPERIENCES BELOW THIS LINE ──────────────────────────────────
]

def format_experience_bank():
    grouped = {}
    for entry in EXPERIENCE_BANK:
        employer = entry["employer"]
        if employer not in grouped:
            grouped[employer] = []
        grouped[employer].append(f"- {entry['experience']}")
    output = ""
    for employer, bullets in grouped.items():
        output += f"\n{employer}:\n" + "\n".join(bullets) + "\n"
    return output

def tailor_resume(job_description):
    prompt = PromptTemplate(
        input_variables=["background", "resume", "bank", "job"],
        template="""You are a professional resume writer specializing in career transitions from SEO to Project Management.

CANDIDATE SOURCES — treat as a fact base only, not copy-paste material:

You have THREE sources to draw from when writing bullets. Pull ideas, context, skills, and topics from all three:

SOURCE 1 - Candidate Background (skills, values, tools, roles, goals):
{background}

SOURCE 2 - Base Resume (structured experience by employer):
{resume}

SOURCE 3 - Experience Bank (additional bullets tagged by employer):
{bank}

JOB DESCRIPTION to tailor for:
{job}

---

BEFORE WRITING ANYTHING, analyze the job description internally:
1. Identify the role type (SEO, PM, Marketing, Operations, Data, other)
2. Extract all responsibilities. If percentage-weighted (e.g. "30% SEO Strategy, 25% Project Planning"), note the weights — use them to allocate bullet emphasis proportionally
3. Extract all keywords, repeated phrases, and formal competency labels (e.g. "Decision Quality", "Plans and Aligns", "Drives Results", "Ensures Accountability")
4. Note every tool, certification, qualification, and experience type mentioned in the JD
5. Cross-reference step 4 against the candidate sources — anything in the JD not found in the sources gets flagged in Section 4
6. Identify 2-4 skill categories relevant to this specific role — only include categories genuinely relevant to the JD
7. Auto-adjust framing based on role type:
   - SEO role: lead with SEO skills, use PM experience as a supporting strength
   - PM/Delivery role: lead with delivery governance, use SEO as domain credibility
   - Marketing role: lead with campaign coordination and content operations
   - Any other role: find the closest matching skills and lead with those

---

OUTPUT EXACTLY SIX SECTIONS IN THIS ORDER. NO PREAMBLE. NO COMMENTARY.

---

SECTION 1 — SUMMARY
Write 2 sentences. Position the candidate as an SEO Analyst with simultaneous Project Management experience who is transitioning into a PM role. Mirror language from the job description.

---

SECTION 2 — EXPERIENCE

BULLET RULES:
- Start from the job description responsibilities — find which ones match or are bridgeable from the sources
- If the JD has percentage-weighted responsibilities, allocate bullets proportionally to those weights
- Generate MOSTLY NEW sentences. Do NOT copy bullets verbatim from the sources. Sources confirm facts only.
- Write every bullet fresh using active voice and strong verbs
- Weave formal competency labels from the JD naturally into bullet language as demonstrated behaviors — do not list them literally
- If the job mentions a responsibility the candidate has indirect experience with, write a bridging bullet using their closest real experience — do not fabricate
- Bullets should read like a strong transferable resume

EMPLOYER ORDER: Always chronological, most recent first (most recent employer first)

STRUCTURE PER EMPLOYER:
- Primary employers: minimum 2 qualitative + 2 quantitative bullets, up to 5 total if warranted
- Earlier employers: exactly 1 qualitative + 1 quantitative bullet
- Freelance or short-tenure roles: omit unless directly relevant
- Order within each employer: ALL qualitative bullets first, then ALL quantitative bullets — this is a strict rule for ALL employers including Diib, never mix the order

ALL THREE EMPLOYERS follow the same generation rules:
- Start from the job description responsibilities — find which ones match or are bridgeable from the sources
- Generate MOSTLY NEW sentences. Do NOT copy bullets verbatim from the sources. Sources confirm facts only.
- Write every bullet fresh using active voice and strong verbs that mirror the job description language
- Weave formal competency labels from the JD naturally into bullet language as demonstrated behaviors
- If the job mentions a responsibility the candidate has indirect experience with, write a bridging bullet using their closest real experience

QUALITATIVE bullets: action-verb statements that demonstrate skills, behaviors, and impact without a specific metric
QUANTITATIVE bullets: MUST use this exact format: "Accomplished [X] as measured by [Y], by doing [Z]"
- Use real metrics from the sources when they exist, but soften ALL metrics using varied language — apply this to every metric whether sourced or generated
- When no real metric exists, generate a realistic one based on role seniority, time in position, and industry niche — soften it the same way, do NOT mark it with (*est.) or any other marker
- Never use hard exact numbers — always frame metrics with softening language
- Vary the softening word used across every metric in the entire output. Either select your own variant for the metric being described or choose from: "roughly," "approximately," "nearly," "close to," "around," "just over," "just under," "upward of" — no single word may appear more than twice across the entire document
- Never leave a blank placeholder like [X]
    
Format:
**Company Name | Date Range**
- Qualitative bullet
- Qualitative bullet
- Quantitative bullet
- Quantitative bullet

---

SECTION 3 — SKILLS

Generate 2-4 skill categories relevant to this specific role. Category labels should be customized to the job description (e.g. "SEO & Digital Marketing", "Project Management & Agile", "Analytics & Reporting"). Pull skills from the JD first, then match to the candidate sources — only include skills the candidate can actually claim.

Format each category as:
**Category Label:** Skill one, Skill two, Skill three

Rules:
- Category labels flex based on the JD — only include categories genuinely relevant to this role
- Skills within each category are pulled from the JD first, matched against SOURCE 1 and SOURCE 2
- The LAST line is always fixed as: **Tools & Platforms:** [tools that appear in BOTH the JD and the candidate sources], and more.
- Do not include tools in Tools & Platforms that only appear in the JD — those go in Section 4

---

SECTION 4 — FLAGGED
List every item mentioned in the job description that does NOT appear in the candidate sources. Include tools, certifications, qualifications, specific experience types, or any other gap.

For each item, add a brief note on how to address it.

Format:
- [Item]: [Brief note on how to address]

---

SECTION 5 — EXPERIENCE PROMPTS
For each item in Section 4 that represents a work experience gap (not a tool, skill, certification, or qualification — only missing work experience), generate 2 ready-to-use bullets grouped under that flagged item.

Rules:
- Only generate bullets for experience-type gaps, skip everything else
- Each experience gap gets exactly 1 qualitative bullet followed by exactly 1 quantitative bullet
- Qualitative bullet: fresh action-verb statement written as if the candidate has this experience, mirroring job description language
- Quantitative bullet: MUST use this exact format: "Accomplished [X] as measured by [Y], by doing [Z]" — generate a realistic metric, soften it with language like "roughly," "approximately," or "nearly" — do NOT use (*est.) or any other marker
- Bullets should be ready-to-use and written confidently, not hedged
- Bridge from the candidate's closest real experience to make the bullets plausible

Format:
**[Flagged Experience Gap]**
- Qualitative bullet
- Quantitative bullet

---

SECTION 6 — PLACEMENT INSTRUCTIONS
For each work experience gap identified in Section 4 (same scope as Section 5 — skip tools, skills, certifications, and qualifications), list only the category name and the exact industry terms the candidate should use if they have this experience.

Rules:
- Only cover experience-type gaps, skip everything else
- List the flagged category name exactly as it appears in Section 4
- Follow it immediately with a list of exact industry terms — include enough variations that the candidate can recognize the experience even if they knew it by a different name
- No additional explanation, no placement instructions, no extra text — just the category and the terms

Format:
**[Flagged Experience Gap]**
**Exact terms to use:** [comma-separated list of proper industry terms for this experience type]

---

Output these six sections only. No preamble, no extra commentary."""
    )
    result = (prompt | llm).invoke({
        "background": YOUR_BACKGROUND,
        "resume": BASE_RESUME,
        "bank": format_experience_bank(),
        "job": job_description
    }).content
    print(result)
    save_result("TAILORED RESUME", f"**Job:**\n{job_description}\n\n**Tailored Resume:**\n{result}")
    return result

# ── Tool 3: Cover Letter Generator ──────────────────────────────────────────

def generate_cover_letter(job_description, company_name):
    prompt = PromptTemplate(
        input_variables=["background", "job", "company"],
        template="""Write a concise, confident cover letter for this job application.

Candidate Background:
{background}

Company: {company}

Job Description:
{job}

Guidelines:
- 3 short paragraphs only
- Paragraph 1: Why this role and company excite you
- Paragraph 2: 2-3 specific ways your experience directly applies
- Paragraph 3: Confident close with call to action
- Tone: Professional but human, not robotic
- Do NOT start with "I am writing to apply..."
- Under 250 words"""
    )
    result = (prompt | llm).invoke({
        "background": YOUR_BACKGROUND,
        "job": job_description,
        "company": company_name
    }).content
    print(result)
    save_result("COVER LETTER", f"**Company:** {company_name}\n\n**Job:**\n{job_description}\n\n**Cover Letter:**\n{result}")
    return result

# ── Tool 4: Interview Prep ───────────────────────────────────────────────────

def generate_interview_prep(job_description):
    prompt = PromptTemplate(
        input_variables=["background", "job"],
        template="""You are an interview coach. Based on this job description and candidate background, prepare them for the interview.

Candidate Background:
{background}

Job Description:
{job}

Provide:
1. Top 5 likely interview questions for this specific role
2. For each question, a suggested answer framework using the candidate's background
3. 3 smart questions the candidate should ask the interviewer
4. One key thing to emphasize given the career transition from SEO to PM"""
    )
    result = (prompt | llm).invoke({"background": YOUR_BACKGROUND, "job": job_description}).content
    print(result)
    save_result("INTERVIEW PREP", f"**Job:**\n{job_description}\n\n**Prep:**\n{result}")
    return result

# ── Main Menu ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n=== JOB HUNTER TOOLKIT ===")
    print("1. Score a job listing")
    print("2. Tailor my resume")
    print("3. Generate a cover letter")
    print("4. Interview prep")
    print("5. Full pipeline (score + tailor + cover letter + prep)")
    print("6. Resume + cover letter only")

    choice = input("\nChoose an option (1-6): ").strip()

    job_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "job.txt")
    if os.path.exists(job_file):
        with open(job_file, "r") as f:
            job_desc = f.read().strip()
        print(f"\nLoaded job description from job.txt ({len(job_desc)} characters)")
    else:
        print("\nNo job.txt found. Create one by running:")
        print("  cat > ~/cot-prompting/job.txt")
        print("Paste the job description, then press Control+D to save.")
        exit(1)

    if choice == "1":
        score_job(job_desc)
    elif choice == "2":
        tailor_resume(job_desc)
    elif choice == "3":
        company = input("Company name: ")
        generate_cover_letter(job_desc, company)
    elif choice == "4":
        generate_interview_prep(job_desc)
    elif choice == "5":
        company = input("Company name: ")
        print("\n--- SCORING ---")
        score_job(job_desc)
        print("\n--- TAILORED RESUME ---")
        tailor_resume(job_desc)
        print("\n--- COVER LETTER ---")
        generate_cover_letter(job_desc, company)
        print("\n--- INTERVIEW PREP ---")
        generate_interview_prep(job_desc)
    elif choice == "6":
        company = input("Company name: ")
        print("\n--- TAILORED RESUME ---")
        tailor_resume(job_desc)
        print("\n--- COVER LETTER ---")
        generate_cover_letter(job_desc, company)
