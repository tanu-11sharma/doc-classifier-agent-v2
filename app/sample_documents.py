"""
Synthetic, hand-written sample documents used to (a) seed the category
centroids the classifier compares against and (b) exercise the pipeline in
tests and the demo endpoint. None of this text is real correspondence or
real company data -- it's all made up for demonstration purposes.
"""

from __future__ import annotations

# Each category has a handful of short synthetic reference documents. The
# classifier agent builds a TF-IDF "centroid" for each category from these.
CATEGORY_SEED_DOCS: dict[str, list[str]] = {
    "invoice": [
        "Invoice #4521 due on receipt. Total amount due: $1,240.00. "
        "Please remit payment within 30 days to avoid late fees.",
        "This invoice covers consulting services rendered in March. "
        "Subtotal, tax, and total balance due are itemized below.",
        "Payment terms: net 30. Invoice number, billing address, and "
        "line items for hours billed are attached to this statement.",
    ],
    "resume": [
        "Experienced software engineer with 5 years building backend "
        "services in Python and Go. Skills include distributed systems, "
        "REST APIs, and cloud infrastructure. Education: B.S. Computer Science.",
        "Objective: seeking a data analyst role. Work experience includes "
        "SQL reporting, dashboarding, and stakeholder communication. "
        "References available upon request.",
        "Summary of qualifications: product manager with a track record of "
        "shipping features, writing specs, and running sprint planning.",
    ],
    "contract": [
        "This agreement is entered into by and between the parties below. "
        "The term of this contract shall commence on the effective date "
        "and continue until terminated in accordance with Section 8.",
        "Non-disclosure agreement: the receiving party agrees to hold "
        "confidential information in strict confidence and not disclose "
        "it to third parties without prior written consent.",
        "Statement of work: the vendor shall deliver the services "
        "described in Exhibit A in exchange for the fees set forth herein.",
    ],
    "support_ticket": [
        "I can't log into my account, it keeps saying invalid password "
        "even after I reset it twice. Please help urgently.",
        "The app crashes every time I try to upload a file larger than "
        "10MB. Steps to reproduce are attached. Ticket priority: high.",
        "Customer reports that the export button is missing after the "
        "latest update. Requesting a fix or workaround.",
    ],
    "meeting_notes": [
        "Attendees: product, design, and engineering leads. Agenda covered "
        "Q3 roadmap. Action items: finalize scope by Friday, assign owners.",
        "Standup notes: yesterday's progress, today's plan, and blockers "
        "for each team member were discussed in the fifteen minute sync.",
        "Retro summary: what went well, what didn't, and action items for "
        "the next sprint were captured with owners and due dates.",
    ],
}
