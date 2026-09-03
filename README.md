# Performance Review & Career Development Portal

A web-based performance review system built for Qubits, streamlining the annual employee evaluation cycle — from self-assessment to manager review to formal acknowledgment — in one connected workflow.

## Overview

This app replaces a manual, form-based performance review process with a structured digital workflow. Employees submit self-assessments, managers rate and review performance against a fixed set of criteria, and employees formally acknowledge the final evaluation — with everything stored and tracked in a shared database.

## Features

- **Role-based views** — separate Employee and Manager interfaces from a single app
- **Employee self-assessment** — structured form covering achievements, goals accomplished, value added, skills gained, challenges faced, and support needed
- **Manager evaluation** — standardized 1–10 scoring across 10 criteria (punctuality, professional attitude, proactive learning, teamwork & collaboration, commitment & loyalty, strategic alignment, problem solving & data analysis, communication, interpersonal skills, and technical/project management), plus written comments
- **Employee management** — managers can add new employees and assign evaluation periods directly from the app
- **Acknowledgment workflow** — employees review manager feedback and formally sign off, closing the loop on the review cycle
- **Status tracking** — the app tracks each employee's stage in the process (self-assessment pending, submitted, reviewed, acknowledged) and displays the right view automatically

## Tech Stack

| Component          | Technology |
|---------------------|-----------|
| Frontend / App       | Streamlit |
| Backend / Database   | Supabase  |
| Language              | Python    |

## How It Works

1. **Employee** logs in with their name and ID, fills out an initial profile (if new), then submits a self-assessment.
2. **Manager** reviews the employee's self-assessment and fills out a scored evaluation form with comments.
3. **Employee** reviews the manager's feedback and submits a formal acknowledgment, completing the cycle.

Each stage checks the database for existing records, so the app always shows the correct next step for that employee — whether that's filling out a form, waiting on a manager review, or confirming they've seen their feedback.

## Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/ahmadalirizvi/Performance-Review.git
   cd Performance-Review
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**

   Create a `.env` file with your Supabase credentials:
   ```
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_api_key
   ```

4. **Run the app**
   ```bash
   streamlit run app.py
   ```

## Database Structure

The app expects the following Supabase tables:
- `assessments` — core employee record (name, ID, designation, department, manager, evaluation period, status)
- `employee_self_assessments` — employee-submitted self-review data
- `annual_performance_assessments` — manager-submitted scores and comments
- `acknowledgments` — employee sign-off on the final evaluation
