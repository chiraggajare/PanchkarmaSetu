# 👥 Team & Scenario — PanchkarmaSetu

---

## 1. Project Overview

**Project Name:** PanchkarmaSetu  
**Type:** Healthcare Web Application (Django + Python)  
**Domain:** Ayurvedic Panchkarma clinic management  
**Duration:** ~15 weeks (Semester Project)  
**Team Size:** 4 Members  

---

## 2. Team Roles & Responsibilities

| # | Role | Member | Primary Responsibilities |
|---|------|--------|--------------------------|
| 1 | **Project Lead / Full-Stack Developer** | Chirag | Overall architecture, Django backend, views, URL routing, authentication, deployment |
| 2 | **Backend Developer / Database Engineer** | Member 2 | Models design, migrations, database queries, ORM optimization, PDF report generation |
| 3 | **Frontend Developer / UI Designer** | Member 3 | HTML templates, Bootstrap 5, glassmorphism UI, responsive design, AJAX interactions |
| 4 | **QA Engineer / Documentation Lead** | Member 4 | Testing (unit + manual), bug reporting, writing documentation, admin panel configuration |

---

## 3. Responsibility Matrix (RACI)

| Task | Project Lead | Backend Dev | Frontend Dev | QA / Docs |
|------|:---:|:---:|:---:|:---:|
| Requirements definition | **R/A** | C | C | I |
| Database schema design | A | **R** | I | C |
| Backend views & logic | **R/A** | C | I | I |
| Template HTML/CSS | I | I | **R/A** | C |
| Bootstrap UI refactoring | C | I | **R/A** | I |
| PDF report generation | C | **R/A** | I | C |
| Admin panel setup | **R** | C | I | A |
| Testing & bug fixing | C | C | C | **R/A** |
| Documentation | C | C | I | **R/A** |
| Deployment | **R/A** | C | I | I |

> **R** = Responsible, **A** = Accountable, **C** = Consulted, **I** = Informed

---

## 4. Risk Scenarios: Impact if a Member Leaves Suddenly

### 4.1 Scenario: Project Lead / Full-Stack Developer Leaves

**Likelihood of Occurrence:** Low (but highest impact)  
**Impact Level:** 🔴 **CRITICAL**

| Category | Impact |
|----------|--------|
| **Immediate** | All backend development halts — views, URL routing, and authentication are blocked |
| **Knowledge Loss** | Deep understanding of Django architecture, request-response cycle, and session management is lost |
| **Dependencies** | Other team members cannot integrate their components without a working backend |
| **Schedule Risk** | 2–3 week delay minimum to onboard a replacement and bring them up to speed |
| **Mitigation** | Maintain detailed comments in `views.py`; conduct weekly knowledge-sharing sessions; use version-controlled documentation |

---

### 4.2 Scenario: Backend Developer / Database Engineer Leaves

**Likelihood of Occurrence:** Medium  
**Impact Level:** 🟠 **HIGH**

| Category | Impact |
|----------|--------|
| **Immediate** | Database migrations stop; PDF generation feature (`pdf_utils.py`) is blocked |
| **Knowledge Loss** | ORM query optimization, complex `defaultdict` structures, and ReportLab PDF logic become opaque |
| **Dependencies** | Frontend developer cannot display dynamic data; QA cannot test database-linked features |
| **Schedule Risk** | 1–2 week delay; some features like analytics may have to be simplified |
| **Mitigation** | Document all model relationships in an ER diagram; review complex ORM queries in team meetings; keep `models.py` heavily commented |

---

### 4.3 Scenario: Frontend Developer / UI Designer Leaves

**Likelihood of Occurrence:** Medium  
**Impact Level:** 🟡 **MODERATE**

| Category | Impact |
|----------|--------|
| **Immediate** | UI development halts; Bootstrap 5 refactoring and template updates are blocked |
| **Knowledge Loss** | Custom CSS variables (glassmorphism styles), JavaScript AJAX calls for slot booking, and template inheritance structure |
| **Dependencies** | Functional pages exist but are unstyled; users cannot test the application effectively |
| **Schedule Risk** | 1 week delay; other members can handle basic HTML changes |
| **Mitigation** | Maintain a shared CSS design system file; document all JavaScript interactions; use Bootstrap utility classes consistently (easier for others to replicate) |

---

### 4.4 Scenario: QA Engineer / Documentation Lead Leaves

**Likelihood of Occurrence:** Medium-High  
**Impact Level:** 🟡 **MODERATE**

| Category | Impact |
|----------|--------|
| **Immediate** | Manual testing stops; documentation falls behind; bugs accumulate |
| **Knowledge Loss** | Test cases for edge conditions (e.g., concurrent booking, cancelled mid-cycles) may be lost |
| **Dependencies** | Development team must self-test, increasing cognitive load and overlooking bugs |
| **Schedule Risk** | Quality risk more than schedule risk; bugs may reach submission |
| **Mitigation** | Maintain a shared test checklist document; write Django unit tests in `tests.py` for automated coverage; divide documentation writing among remaining members |

---

## 5. Key Mitigation Strategies (Overall)

1. **Code Reviews** — All major features reviewed by at least one other member before merging.
2. **Knowledge Sharing Sessions** — Weekly 30-minute demos of completed features to the whole team.
3. **Version Control (Git)** — All code committed with descriptive messages; no single person holds code locally.
4. **Shared Documentation** — Design decisions, DB schema, and workflows documented in the `/docs` folder.
5. **Cross-Training** — Each member understands at least the basics of every other member's domain.

---

*Document: PanchkarmaSetu Project Management | Team & Scenario Analysis*
