# ⚠️ Risk Management — PanchkarmaSetu

---

## 1. Risk Management Framework

Risks are evaluated on two axes:
- **Probability** (1–5): Likelihood of occurrence
- **Impact** (1–5): Severity if it occurs
- **Risk Score** = Probability × Impact (higher = more critical)

---

## 2. Risk Register — Top Three Prioritized Risks

### 🔴 Risk #1 (HIGHEST PRIORITY): Technical Risk — Database Schema Incompatibility

| Attribute | Detail |
|-----------|--------|
| **Risk Category** | Technical |
| **Risk Statement** | The SQLite database schema may become incompatible mid-project due to model changes (new fields, relationships), causing migration failures and data loss. |
| **Probability** | 4 / 5 |
| **Impact** | 5 / 5 |
| **Risk Score** | **20 / 25** 🔴 |
| **Trigger** | Adding a new field to `TreatmentCycle`, `Attendance`, or `User` models after production data exists |
| **Real Example from Project** | Adding the `is_cancelled_midway` field and `Notification` model to a running database required careful migration management |

**Consequences if Not Managed:**
- Application crashes on all requests due to missing columns
- Existing patient/therapist data may be wiped if `--run-syncdb` is used blindly
- Treatment cycles and attendance records could become orphaned

**Mitigation Strategies:**

| Strategy | Action |
|---------|--------|
| **Version Control Migrations** | Always commit `migrations/` folder with every model change |
| **Backup Before Migration** | Run `python manage.py dumpdata > backup.json` before any `makemigrations` |
| **Staging Environment** | Test migrations on a copy of the database before applying to production |
| **Descriptive Migration Names** | Use `--name` flag: `python manage.py makemigrations --name add_notification_model` |
| **Avoid `--fake` without Reason** | Only use `--fake` migrations when absolutely sure state is correct |

**Contingency Plan:**
- Keep `backup.json` dated snapshots; restore with `python manage.py loaddata backup.json` if migration fails.

---

### 🟠 Risk #2 (HIGH PRIORITY): Schedule Risk — Feature Scope Creep

| Attribute | Detail |
|-----------|--------|
| **Risk Category** | Schedule |
| **Risk Statement** | Continuous addition of new features (PDF export, live stats, notifications, payment page) beyond the initial scope may push the deadline. |
| **Probability** | 4 / 5 |
| **Impact** | 4 / 5 |
| **Risk Score** | **16 / 25** 🟠 |
| **Trigger** | Stakeholder (faculty) requests new features mid-sprint; team self-adds "nice-to-have" features |
| **Real Example from Project** | PDF report generation, notification system, and dummy payment page were all added after the core was built — each taking 2–3 additional days |

**Consequences if Not Managed:**
- Core features (appointment booking, diagnosis, attendance) may not be fully polished at submission
- Testing phase gets compressed, increasing bug risk
- Documentation lags behind development

**Mitigation Strategies:**

| Strategy | Action |
|---------|--------|
| **Feature Freeze Date** | Lock product backlog 2 weeks before deadline |
| **MoSCoW Prioritization** | Classify all features as Must-have / Should-have / Could-have / Won't-have |
| **Sprint Reviews** | At end of each sprint, re-evaluate remaining scope vs. remaining time |
| **Change Request Protocol** | Any new feature request must be approved by the Project Lead and logged |
| **Buffer Time** | Keep Week 14 as a buffer week — no new features, only polishing |

**Contingency Plan:**
- If behind schedule, drop "Could-have" features (e.g., email notifications, advanced analytics graphs).

---

### 🟡 Risk #3 (MODERATE PRIORITY): Resource Risk — Single Point of Failure for Backend Knowledge

| Attribute | Detail |
|-----------|--------|
| **Risk Category** | Resource |
| **Risk Statement** | Critical backend knowledge (Django ORM, authentication, view logic) is concentrated in one team member. If they are unavailable, development halts. |
| **Probability** | 3 / 5 |
| **Impact** | 5 / 5 |
| **Risk Score** | **15 / 25** 🟡 |
| **Trigger** | Project Lead falls ill, has a personal emergency, or becomes unavailable for > 5 days |
| **Real Example from Project** | `views.py` grew to 609 lines with complex logic (role-based dashboards, ORM aggregations, slot booking concurrency checks) — understood deeply only by the main developer |

**Consequences if Not Managed:**
- No one else can debug a broken authentication flow or fix a failing ORM query
- Other team members waste time trying to understand undocumented code
- Features dependent on backend (all frontend templates, PDF, admin) are blocked

**Mitigation Strategies:**

| Strategy | Action |
|---------|--------|
| **Code Comments** | Add inline comments to all complex logic in `views.py` and `models.py` |
| **Pair Programming** | Conduct at least 2 pair-programming sessions per sprint on backend features |
| **Architecture Document** | Maintain a brief system architecture document in `/docs` |
| **Git Commit History** | Write descriptive commit messages so others can understand what changed and why |
| **Backup Developer** | Database engineer has secondary exposure to backend views through code reviews |

**Contingency Plan:**
- Temporarily simplify complex views (e.g., replace analytics aggregation with static data) to unblock the rest of the team.

---

## 3. Risk Priority Matrix

```
IMPACT
  5  |       |       | R#1   |       |       |
     |       |       | (Tech)|       |       |
  4  |       |       | R#2   |       |       |
     |       |       |(Sched)|       |       |
  3  |       |       |       |       |       |
     |       |       |       |       |       |
  2  |       |       |       |       |       |
     |       |       |       |       |       |
  1  |       |       |       |       |       |
     +-------+-------+-------+-------+-------+
          1       2       3       4       5
                      PROBABILITY

  🔴 R#1 (Technical): Score 20 — CRITICAL
  🟠 R#2 (Schedule):  Score 16 — HIGH
  🟡 R#3 (Resource):  Score 15 — MODERATE
```

---

## 4. Risk Summary Table

| # | Risk | Category | Probability | Impact | Score | Priority |
|---|------|----------|:-----------:|:------:|:-----:|:--------:|
| 1 | Database schema incompatibility | Technical | 4 | 5 | **20** | 🔴 Critical |
| 2 | Feature scope creep | Schedule | 4 | 4 | **16** | 🟠 High |
| 3 | Single point of failure (backend knowledge) | Resource | 3 | 5 | **15** | 🟡 Moderate |

---

*Document: PanchkarmaSetu Project Management | Risk Management Plan*
