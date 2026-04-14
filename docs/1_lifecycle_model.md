# 📋 Life Cycle Model — PanchkarmaSetu

---

## 1. Identified Model: **Hybrid (Agile + Waterfall)**

PanchkarmaSetu adopts a **Hybrid Life Cycle Model**, combining structured Waterfall phases for foundational architecture with Agile sprints for iterative feature delivery.

---

## 2. Why Hybrid?

### 2.1 Waterfall Elements Used

| Phase | Activity in PanchkarmaSetu |
|---|---|
| Requirements | Roles (Patient, Therapist, Centre Head), Dosha types, treatment plans defined upfront |
| System Design | Django MVT architecture, database schema (User, Appointment, TreatmentCycle, etc.) designed at start |
| Database Design | All models finalized before development began (SQLite → migrations) |
| Deployment | Single production server, no blue-green or rolling deployment needed |

**Justification:** Core domain knowledge (Ayurvedic Panchkarma treatment workflow) was well-understood from the beginning. The data model (patients → appointments → diagnosis → treatment cycles → attendance → feedback) is a strict sequential pipeline that couldn't be changed mid-development without breaking the schema.

---

### 2.2 Agile Elements Used

| Sprint | Activity |
|---|---|
| Sprint 1 | User authentication (signup/login/logout), role-based redirects |
| Sprint 2 | Patient appointment booking, slot availability API |
| Sprint 3 | Therapist dashboard — diagnosis submission, attendance marking |
| Sprint 4 | Centre Head dashboard — therapist assignment, analytics |
| Sprint 5 | Feedback system, PDF report generation |
| Sprint 6 | UI overhaul — Bootstrap 5, glassmorphism design, notifications |

**Justification:** Each dashboard (Patient, Therapist, Centre Head) was built and tested independently in iterations. UI improvements and new features (e.g., PDF export, notifications, live stats on home page) were added incrementally based on feedback — a hallmark of Agile.

---

## 3. Logical Justification

### Why Not Pure Waterfall?
- Requirements must evolve as clinic workflows are better understood.
- UI/UX needs continuous refinement (e.g., Bootstrap 5 refactoring done after initial release).
- Testing revealed edge cases (e.g., concurrent appointment booking conflict) only during iteration.

### Why Not Pure Agile (Scrum)?
- Healthcare domain demands strict data integrity — the database schema must be stable and well-thought-out from day one.
- No dedicated Product Owner or daily standup structure exists in a college project setting.
- Some deliverables (database migrations, initial setup) are inherently sequential.

### Conclusion
The **Hybrid model** gave PanchkarmaSetu the **predictability of Waterfall for architecture** and the **flexibility of Agile for feature development**, making it the most pragmatic choice for a semester-length healthcare web application project.

---

## 4. Development Timeline Summary

```
Week 1-2   : [WATERFALL] Requirements gathering, architecture & DB design
Week 3-4   : [AGILE S1]  Auth system, role-based access, models & migrations
Week 5-6   : [AGILE S2]  Patient flow — booking, slot API, intake form
Week 7-8   : [AGILE S3]  Therapist flow — diagnosis, attendance, vitals
Week 9-10  : [AGILE S4]  Centre Head flow — assign therapist, analytics
Week 11-12 : [AGILE S5]  Feedback, ratings, PDF report generation
Week 13-14 : [AGILE S6]  UI polish, Bootstrap 5, notifications, final testing
Week 15    : [WATERFALL] Deployment, documentation, submission
```

---

*Document: PanchkarmaSetu Project Management | Life Cycle Model*
