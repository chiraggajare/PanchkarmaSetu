# 🧭 Leadership Styles — PanchkarmaSetu

---

## 1. Overview

Effective project delivery requires the team leader to adapt their leadership style based on the situation. Two key styles are demonstrated in the context of PanchkarmaSetu:

| Leadership Style | When to Use | Core Behaviour |
|---|---|---|
| **Directive** | Crisis, ambiguity, technical deadlock, tight deadlines | Leader decides, gives clear instructions, team executes |
| **Collaborative** | Stable phase, design decisions, feature planning, team motivation | Leader facilitates, team contributes ideas jointly |

---

## 2. Directive Leadership Style

### Definition
The leader makes decisions unilaterally, provides explicit step-by-step instructions, and expects the team to follow immediately. This is appropriate when speed and clarity are critical.

---

### 🔴 Realistic Situation #1: Critical Bug — Concurrent Booking Conflict Discovered 3 Days Before Submission

**Scenario:**
During final testing, the QA engineer discovers that two patients can book the same appointment time slot simultaneously. When Appointment A and Appointment B are submitted within milliseconds of each other for the same date/time, both succeed — creating a data conflict in the `Appointment` table.

This is a **critical production bug** 3 days before the submission deadline. The team is anxious, and there's no consensus on how to fix it.

**Directive Leader Response:**

> *"Stop all other work immediately. Chirag — add a race-condition check in `book_appointment()` in `views.py` using an `if Appointment.objects.filter(date=appt.date, time_slot=appt.time_slot, status__in=['scheduled', 'in_progress']).exists()` guard before saving. Member 3 — update the frontend to disable already-booked slots dynamically via the `/get-available-slots/` API. Member 4 — write the manual test case for this scenario right now. We go live with the fix in 2 hours."*

**Why Directive Works Here:**
- Time is extremely limited — no time for debate.
- The technical solution is clear to the lead but not necessarily to others.
- Indecision would be costlier than a suboptimal fix.
- Team members are given specific, unambiguous sub-tasks.

**Outcome in Project:**
This exact fix was implemented — `views.py` line 278 now contains the concurrency guard that prevents double-booking.

---

### 🔴 Realistic Situation #2: Deadline Pressure — Database Migration Failure on Day of Demo

**Scenario:**
On the day of the faculty demo, running `python manage.py migrate` throws an error because a new field (`is_cancelled_midway`) was added to `TreatmentCycle` without a default value, breaking the migration.

**Directive Leader Response:**

> *"Do not run any other command. Roll back the last migration with `python manage.py migrate core 0008`. Then open `models.py`, add `is_cancelled_midway = models.BooleanField(default=False)` with the correct default. Delete the broken migrations file `0009_...py`. Run `makemigrations` and `migrate` again. Member 4 — stay on standby with the data backup `backup.json` in case we need to `loaddata`. Everyone else — keep the demo running on the old branch."*

**Why Directive Works Here:**
- A live system failure requires immediate, confident decision-making.
- Instructions must be precise to avoid making the situation worse.
- Panic in the team is managed by giving everyone a clear role.

---

## 3. Collaborative Leadership Style

### Definition
The leader facilitates open discussion, ensures every team member's input is heard, and builds consensus before making a decision. This is appropriate during planning phases, architecture design, and when team buy-in is important.

---

### 🟢 Realistic Situation #1: Sprint 1 Planning — Designing the Role-Based Dashboard Architecture

**Scenario:**
At the beginning of the project, the team needs to decide how to handle three different user dashboards (Patient, Therapist, Centre Head) from a single `/dashboard/` URL. There are multiple valid approaches.

**Collaborative Leader Approach:**

> *"Let's think through this together. We have three roles. Option A: Three separate URLs — `/patient/`, `/therapist/`, `/head/`. Option B: One URL that renders different templates based on `request.user.role`. Which approach do you all prefer? Member 2, what's the DB implication of each? Member 3, which makes frontend template management easier?"*

**Discussion that Follows:**
- Member 2 notes that one URL with role checking means simpler URL patterns and no need for permission-based URL guards.
- Member 3 prefers Option B because template inheritance with a shared `base.html` is simpler.
- Member 4 raises that Option B makes testing slightly trickier but agrees it's cleaner.

**Decision Reached Together:**
Option B is chosen — `dashboard()` in `views.py` delegates to `render_patient_dashboard()`, `render_therapist_dashboard()`, or `render_head_dashboard()` based on `request.user.role`. This exact design is reflected in the project.

**Why Collaborative Works Here:**
- The decision has no urgency — it's a design-phase discussion.
- Every member is affected by the outcome, so buy-in matters.
- Members 2 and 3 have domain expertise the lead may not fully possess.
- Collaborative decisions result in higher-quality outcomes and greater team ownership.

---

### 🟢 Realistic Situation #2: Sprint 5 Planning — Choosing Features for the Feedback System

**Scenario:**
The team is planning the feedback system. Options include: (a) simple star ratings only, (b) star ratings + text feedback, (c) separate therapist rating + overall rating + text, (d) all of the above + NPS score. Time is limited.

**Collaborative Leader Approach:**

> *"We have limited time for Sprint 5. I want everyone's input on how detailed the feedback system should be. Member 4 — from a QA perspective, how much testing overhead does each add? Member 3 — how complex is the UI for each option? Member 2 — which fields do we already have in TreatmentCycle?"*

**Discussion:**
- Member 2 points out that `therapist_rating`, `overall_rating`, and `feedback_text` fields were already sketched in the `TreatmentCycle` model.
- Member 3 says a dual-rating (therapist + overall) with a text box is achievable in 2 days using a simple Django form.
- Member 4 suggests skipping NPS as it adds complexity without clear benefit for a semester project.

**Decision Reached Together:**
Go with Option C — `therapist_rating`, `overall_rating`, and `feedback_text`. This is exactly what the final `FeedbackForm` in `forms.py` implements, and `TreatmentCycle` holds all three fields.

**Why Collaborative Works Here:**
- No crisis — just a design trade-off.
- Each member brings different insight (technical, UI, testing).
- The team feels ownership of the feature and is more motivated to implement it well.
- A leader imposing unnecessary complexity here would breed resentment.

---

## 4. Styles Comparison Summary

| Dimension | Directive | Collaborative |
|-----------|-----------|---------------|
| **Decision Speed** | Immediate | Takes more time |
| **Best For** | Crises, technical deadlocks, deadlines | Planning, design, feature scoping |
| **Team Autonomy** | Low | High |
| **Risk of Use** | Can reduce team morale if overused | Slower in emergencies |
| **PanchkarmaSetu Phase** | Sprint execution, bug fixes | Sprint planning, architecture design |

---

*Document: PanchkarmaSetu Project Management | Leadership Styles*
