# 🔀 Git & GitHub Guide for Prompt Guardian
## Complete Beginner-Friendly Collaboration Guide

---

# PART 0 — WHAT IS GIT AND GITHUB? (Everyone Read)

## Git = Save Points for Your Code

Think of Git like a **video game save system** for your project.

- Every time you finish something, you **save** (called a "commit")
- If something breaks, you can **go back** to any previous save
- Multiple people can work on the same project without overwriting each other

## GitHub = Cloud Storage for Git

- Git lives on your computer
- GitHub puts it online so your team can access it
- Think of it like **Google Drive but for code**

## Key Words You Need to Know

```
repository (repo)  = your project folder tracked by Git
commit             = a save point ("I finished this piece")
push               = upload your saves to GitHub
pull               = download teammates' saves from GitHub
branch             = your own separate copy to work in safely
merge              = combining your branch into the main project
merge conflict     = two people edited the same line (Git asks you to choose)
clone              = download a GitHub repo to your computer for the first time
```

---

# PART 1 — ONE-TIME SETUP (Everyone Does This Once)

## Step 1: Install Git

**Windows:**
1. Go to https://git-scm.com/download/win
2. Download and install (click Next for all defaults)
3. **IMPORTANT**: When it asks about default editor, choose **VS Code**

**Mac:**
1. Open Terminal
2. Type: `git --version`
3. If not installed, it will prompt you to install. Click Install.

**Verify it worked:**
```bash
git --version
```
You should see: `git version 2.x.x`

## Step 2: Tell Git Who You Are

Open Terminal (Mac) or Git Bash (Windows — search "Git Bash" in Start menu):

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

**Each person runs this with their OWN name:**

```bash
# Sagar runs:
git config --global user.name "Sagar R"
git config --global user.email "sagar@example.com"

# Poojitha runs:
git config --global user.name "Poojitha"
git config --global user.email "poojitha@example.com"

# Sai Tej runs:
git config --global user.name "Sai Tej"
git config --global user.email "saitej@example.com"

# Prithvi runs:
git config --global user.name "Prithvi"
git config --global user.email "prithvi@example.com"
```

## Step 3: Create a GitHub Account

1. Go to https://github.com
2. Sign up (free)
3. **Everyone creates their own account**
4. Send your GitHub username to Sagar

---

# PART 2 — SAGAR CREATES THE REPO (Only Sagar Does This)

## Step 1: Create Repository on GitHub

1. Go to https://github.com
2. Click the **+** button (top right) → **New repository**
3. Fill in:
   - Repository name: `prompt-guardian`
   - Description: `Browser-native prompt injection firewall`
   - **Public** (so judges can see)
   - ✅ Check "Add a README file"
   - Add .gitignore: select **Python**
4. Click **Create repository**

## Step 2: Add Team Members

1. On your repo page, click **Settings** (tab at top)
2. Left sidebar → **Collaborators**
3. Click **Add people**
4. Search each teammate's GitHub username and add them
5. They will get an email — they must **accept the invitation**

## Step 3: Clone to Your Computer

```bash
cd Desktop
git clone https://github.com/YOUR_USERNAME/prompt-guardian.git
cd prompt-guardian
```

Replace `YOUR_USERNAME` with your actual GitHub username.

## Step 4: Create the Project Structure

```bash
mkdir firewall extension
touch app.py .env requirements.txt
touch firewall/__init__.py firewall/patterns.py
touch firewall/groq_checker.py firewall/scorer.py
touch firewall/sanitizer.py firewall/analyzer.py
touch extension/manifest.json extension/content.js
touch extension/popup.html extension/popup.js
```

**Windows (use Git Bash for touch command, or use type nul > filename)**

## Step 5: Update .gitignore

Open `.gitignore` and add these lines at the top:

```
# Environment
venv/
.env
__pycache__/
*.pyc

# OS files
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
```

**⚠️ CRITICAL: `.env` is in .gitignore — this means your API key will NOT be uploaded to GitHub. This is correct and intentional. Each person creates their own `.env` locally.**

## Step 6: First Commit and Push

```bash
git add .
git commit -m "Initial project structure"
git push origin main
```

## Step 7: Create Branches for Each Person

```bash
git branch backend-sagar
git branch backend-poojitha
git branch extension-saitej
git branch extension-prithvi
git push origin --all
```

This creates 4 separate branches so everyone works independently.

---

# PART 3 — EVERYONE ELSE JOINS (Poojitha, Sai Tej, Prithvi)

## Step 1: Accept the GitHub Invitation

Check your email. Click the invitation link from Sagar. Click **Accept**.

## Step 2: Clone the Repository

```bash
cd Desktop
git clone https://github.com/SAGAR_USERNAME/prompt-guardian.git
cd prompt-guardian
```

Replace `SAGAR_USERNAME` with Sagar's actual GitHub username.

## Step 3: Switch to YOUR Branch

```bash
# Poojitha runs:
git checkout backend-poojitha

# Sai Tej runs:
git checkout extension-saitej

# Prithvi runs:
git checkout extension-prithvi

# Sagar works on:
git checkout backend-sagar
```

## Step 4: Create Your Local `.env` File

```bash
echo "GROQ_API_KEY=paste_the_key_here" > .env
```

Get the API key from the team (Sagar or Poojitha will share it privately).

## Step 5: Set Up Python Environment

```bash
python -m venv venv
source venv/bin/activate      # Mac
venv\Scripts\activate          # Windows
pip install flask flask-cors groq python-dotenv
```

---

# PART 4 — DAILY WORKFLOW (The 6 Commands Everyone Uses)

## The Only 6 Commands You Need

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   1. git pull origin main        ← Get latest from team        │
│   2. git checkout YOUR-BRANCH    ← Switch to your branch       │
│   3. (do your work, edit files)                                │
│   4. git add .                   ← Stage your changes          │
│   5. git commit -m "message"     ← Save your changes           │
│   6. git push origin YOUR-BRANCH ← Upload to GitHub            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Detailed Explanation of Each Command

### Command 1: `git pull origin main`
**What it does:** Downloads the latest code from the main branch
**When to use:** ALWAYS run this FIRST before starting work

```bash
git pull origin main
```

### Command 2: `git checkout YOUR-BRANCH`
**What it does:** Switches you to your personal branch
**When to use:** After pulling, switch to your own branch

```bash
git checkout backend-sagar    # Sagar
git checkout backend-poojitha # Poojitha
git checkout extension-saitej # Sai Tej
git checkout extension-prithvi # Prithvi
```

### Command 3: Do Your Work
Edit files in VS Code normally. Save them.

### Command 4: `git add .`
**What it does:** Tells Git "I want to save these changes"
**The dot means "all changed files"**

```bash
git add .
```

### Command 5: `git commit -m "what I did"`
**What it does:** Creates a save point with a description

```bash
git commit -m "Added pattern detection with 18 regex rules"
```

**Good commit messages:**
```
"Added groq_checker.py with Llama3 integration"
"Fixed overlay CSS not showing on dark theme"
"Added 5 more injection patterns"
"Fixed CORS error in app.py"
```

**Bad commit messages:**
```
"stuff"
"update"
"asdfgh"
"fixed things"
```

### Command 6: `git push origin YOUR-BRANCH`
**What it does:** Uploads your saves to GitHub

```bash
git push origin backend-sagar    # Sagar
git push origin backend-poojitha # Poojitha
git push origin extension-saitej # Sai Tej
git push origin extension-prithvi # Prithvi
```

---

# PART 5 — MERGING (Only Sagar Does This)

## What is Merging?

When someone finishes their work on their branch, their code needs to be added to the `main` branch. This is called **merging**.

**Only Sagar should merge.** This prevents chaos.

## How to Merge (Two Methods)

### Method 1: GitHub Pull Request (Recommended — Easier)

**When a teammate says "I'm done, merge my work":**

1. Go to GitHub repo page
2. Click **"Pull requests"** tab
3. Click **"New pull request"**
4. Set:
   - Base: `main`
   - Compare: `backend-poojitha` (or whoever's branch)
5. Click **"Create pull request"**
6. Add title: "Merge Poojitha's groq_checker"
7. Click **"Create pull request"** again
8. If it says **"Able to merge"** (green) → Click **"Merge pull request"** → **"Confirm merge"**
9. If it says **"Conflicts"** (red) → See Part 6 below

### Method 2: Terminal Merge (For Sagar if GitHub UI is slow)

```bash
# Make sure you're on main and it's up to date
git checkout main
git pull origin main

# Merge someone's branch
git merge backend-poojitha

# If no conflicts:
git push origin main

# If conflicts: see Part 6
```

## Merge Order (Do It In This Order!)

```
MERGE ORDER (to avoid conflicts):

Step 1: Merge Sagar's backend-sagar branch first
        (patterns.py, scorer.py, app.py)

Step 2: Merge Poojitha's backend-poojitha branch
        (groq_checker.py, sanitizer.py, analyzer.py)

Step 3: Merge Sai Tej's extension-saitej branch
        (manifest.json, content.js)

Step 4: Merge Prithvi's extension-prithvi branch
        (popup.html, popup.js)
```

**Why this order?** Backend first because the extension depends on it. If backend isn't working, extension testing is useless.

## After Each Merge — Everyone Pulls

After Sagar merges someone's branch, **EVERYONE** should run:

```bash
git checkout main
git pull origin main
git checkout YOUR-BRANCH
git merge main
```

This keeps everyone's branch up to date.

---

# PART 6 — MERGE CONFLICTS (How to Fix Them)

## What is a Merge Conflict?

A merge conflict happens when **two people edited the same line** in the same file.

Git doesn't know which version to keep, so it asks YOU to decide.

## What a Conflict Looks Like

When you try to merge and there's a conflict, the file will contain:

```
def calculate_risk_score(pattern_result, groq_result):
<<<<<<< HEAD
    combined = (p * 0.55) + (g * 0.45)
=======
    combined = (p * 0.50) + (g * 0.50)
>>>>>>> backend-poojitha
```

**Translation:**
```
<<<<<<< HEAD          = What's currently in main
    (first version)
=======               = Divider
    (second version)
>>>>>>> branch-name   = What's in the incoming branch
```

## How to Fix It

### Step 1: Open the File in VS Code

VS Code shows conflicts with colored highlights:
- **Green** = Current (main)
- **Blue** = Incoming (branch being merged)
- Buttons appear: **Accept Current** | **Accept Incoming** | **Accept Both**

### Step 2: Choose Which Version to Keep

Click one of:
- **Accept Current Change** — keep what's in main
- **Accept Incoming Change** — keep the new branch's version
- **Accept Both Changes** — keep both (usually not what you want)

OR manually edit the file to write the correct version yourself.

### Step 3: Remove the Conflict Markers

Make sure there are NO remaining lines with `<<<<<<<`, `=======`, or `>>>>>>>`.

### Step 4: Save, Add, Commit

```bash
git add .
git commit -m "Resolved merge conflict in scorer.py"
git push origin main
```

## VS Code Conflict Resolution (Visual Guide)

```
When you open a file with conflicts in VS Code:

┌──────────────────────────────────────────────────────┐
│ Accept Current Change | Accept Incoming | Accept Both │
│──────────────────────────────────────────────────────│
│ <<<<<<< HEAD (Current Change)                        │
│     combined = (p * 0.55) + (g * 0.45)               │  ← GREEN
│ =======                                              │
│     combined = (p * 0.50) + (g * 0.50)               │  ← BLUE
│ >>>>>>> backend-poojitha (Incoming Change)            │
└──────────────────────────────────────────────────────┘

Click "Accept Incoming Change" if the branch version is correct.
Click "Accept Current Change" if main version is correct.
```

---

# PART 7 — WHERE CONFLICTS WILL HAPPEN (Specific to Our Project)

## ⚠️ HIGH RISK — Files That Multiple People Might Edit

| File | Who Edits | Conflict Risk | How to Avoid |
|---|---|---|---|
| `app.py` | Sagar only | 🟢 LOW | Only Sagar touches it |
| `firewall/analyzer.py` | Sagar + Poojitha | 🔴 HIGH | Read rule below |
| `extension/content.js` | Sai Tej + Prithvi | 🔴 HIGH | Read rule below |
| `extension/popup.html` | Prithvi only | 🟢 LOW | Only Prithvi touches it |

## ⚡ THE GOLDEN RULE TO AVOID CONFLICTS

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   RULE: NEVER EDIT A FILE THAT ISN'T ASSIGNED TO YOU         ║
║                                                              ║
║   If you need to change someone else's file:                 ║
║   1. Message them on WhatsApp first                          ║
║   2. Wait for them to finish and push                        ║
║   3. Pull their changes                                      ║
║   4. THEN make your edit                                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

## How to Handle `analyzer.py` (The Shared File)

**Problem:** Sagar writes the placeholder, Poojitha writes the final version.

**Solution:**
1. Sagar writes the placeholder `analyzer.py` first (with dummy groq function)
2. Sagar commits and pushes to main
3. Poojitha pulls main
4. Poojitha writes the REAL `analyzer.py` on her branch
5. When merging Poojitha's branch, choose **"Accept Incoming"** for analyzer.py

## How to Handle `content.js` (Another Shared File)

**Problem:** Sai Tej writes the logic, Prithvi might improve the CSS inside it.

**Solution:**
1. Sai Tej writes content.js FIRST (full version with all CSS)
2. Sai Tej commits and pushes
3. Sagar merges Sai Tej's branch to main
4. Prithvi pulls main
5. Prithvi improves ONLY the CSS inside `injectStyles()` function
6. Prithvi commits and pushes
7. Sagar merges — conflict unlikely because they edit different parts

---

# PART 8 — FILE OWNERSHIP MAP

## 2-2 Split

```
┌─────────────────────────────────────────────┐
│ TEAM A (Backend) — Sagar + Poojitha         │
├─────────────────────────────────────────────┤
│                                             │
│ Sagar OWNS:                                 │
│   ├── app.py                ✅ ONLY Sagar   │
│   ├── firewall/patterns.py  ✅ ONLY Sagar   │
│   ├── firewall/scorer.py    ✅ ONLY Sagar   │
│   └── .gitignore            ✅ ONLY Sagar   │
│                                             │
│ Poojitha OWNS:                              │
│   ├── firewall/groq_checker.py ✅ ONLY Poojitha │
│   ├── firewall/sanitizer.py    ✅ ONLY Poojitha │
│   └── firewall/analyzer.py     ✅ ONLY Poojitha │
│                                             │
│ Shared: .env (both need it locally)         │
│ Shared: requirements.txt (Sagar creates)    │
│                                             │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ TEAM B (Extension) — Sai Tej + Prithvi      │
├─────────────────────────────────────────────┤
│                                             │
│ Sai Tej OWNS:                               │
│   ├── extension/manifest.json ✅ ONLY SaiTej│
│   └── extension/content.js   ✅ ONLY SaiTej │
│                                             │
│ Prithvi OWNS:                               │
│   ├── extension/popup.html   ✅ ONLY Prithvi│
│   └── extension/popup.js    ✅ ONLY Prithvi │
│                                             │
│ EXCEPTION: Prithvi may edit the CSS inside  │
│ content.js — but ONLY after Sai Tej is done │
│ and his branch is merged                    │
│                                             │
└─────────────────────────────────────────────┘
```

## 1-1-1-1 Split

```
Sagar         → app.py, patterns.py, scorer.py, .gitignore, requirements.txt
Poojitha      → groq_checker.py, sanitizer.py, analyzer.py
Sai Tej       → manifest.json, content.js
Prithvi       → popup.html, popup.js, demo preparation
```

**ZERO file overlap = ZERO merge conflicts.**

---

# PART 9 — STEP-BY-STEP TIMELINE WITH GIT

## Hour 0-1: Sagar Sets Up

```bash
# Sagar creates repo on GitHub (Part 2 above)
# Sagar clones and creates structure

cd Desktop
git clone https://github.com/sagar/prompt-guardian.git
cd prompt-guardian
mkdir firewall extension
touch app.py .env requirements.txt
touch firewall/__init__.py firewall/patterns.py
touch firewall/groq_checker.py firewall/scorer.py
touch firewall/sanitizer.py firewall/analyzer.py
touch extension/manifest.json extension/content.js
touch extension/popup.html extension/popup.js

# Edit .gitignore (add venv/, .env, __pycache__/)

git add .
git commit -m "Initial project structure with all empty files"
git push origin main

# Create branches
git branch backend-sagar
git branch backend-poojitha
git branch extension-saitej
git branch extension-prithvi
git push origin --all
```

**Sagar texts the group:** "Repo is ready. Clone it now."

## Hour 0-1: Everyone Else Clones

```bash
cd Desktop
git clone https://github.com/sagar/prompt-guardian.git
cd prompt-guardian
git checkout YOUR-BRANCH-NAME

# Set up Python
python -m venv venv
source venv/bin/activate    # Mac
venv\Scripts\activate       # Windows
pip install flask flask-cors groq python-dotenv

# Create .env
echo "GROQ_API_KEY=paste_key_here" > .env
```

## Hour 1-4: Everyone Works on Their Branch

**Sagar:**
```bash
git checkout backend-sagar
# Write patterns.py, scorer.py, app.py
# Save frequently:
git add .
git commit -m "Completed patterns.py with 18 injection patterns"
git push origin backend-sagar

git add .
git commit -m "Completed scorer.py with risk calculation"
git push origin backend-sagar

git add .
git commit -m "Completed app.py Flask server"
git push origin backend-sagar
```

**Poojitha:**
```bash
git checkout backend-poojitha
# Write groq_checker.py, sanitizer.py
git add .
git commit -m "Completed groq_checker.py with Llama3 integration"
git push origin backend-poojitha

git add .
git commit -m "Completed sanitizer.py"
git push origin backend-poojitha
```

**Sai Tej:**
```bash
git checkout extension-saitej
# Write manifest.json, content.js
git add .
git commit -m "Completed manifest.json for Manifest V3"
git push origin extension-saitej

git add .
git commit -m "Completed content.js with interception and overlay"
git push origin extension-saitej
```

**Prithvi:**
```bash
git checkout extension-prithvi
# Write popup.html, popup.js
git add .
git commit -m "Completed popup.html with dark theme UI"
git push origin extension-prithvi

git add .
git commit -m "Completed popup.js with history display"
git push origin extension-prithvi
```

## Hour 4-5: Sagar Merges Everything

```bash
# Sagar merges all branches in order

# Step 1: Merge own backend work
git checkout main
git pull origin main
git merge backend-sagar
git push origin main

# Step 2: Merge Poojitha's work
git merge backend-poojitha
# If conflict in analyzer.py → Accept Incoming
git push origin main

# Step 3: Merge Sai Tej's extension
git merge extension-saitej
git push origin main

# Step 4: Merge Prithvi's popup
git merge extension-prithvi
git push origin main
```

**Sagar texts:** "All merged. Everyone pull main now."

## Hour 5: Everyone Gets the Complete Project

```bash
git checkout main
git pull origin main
```

Now everyone has the complete working project.

---

# PART 10 — EMERGENCY FIXES DURING HACKATHON

## "I messed up my branch and everything is broken"

```bash
# Nuclear option: throw away your branch and start fresh
git checkout main
git pull origin main
git branch -D YOUR-BRANCH-NAME
git checkout -b YOUR-BRANCH-NAME
# Now you have a clean branch from latest main
# Re-do your work (should be fast since you have the code)
```

## "I accidentally edited someone else's file"

```bash
# Undo changes to a specific file (revert to last commit)
git checkout -- path/to/file

# Example:
git checkout -- firewall/patterns.py
```

## "I committed something I shouldn't have"

```bash
# Undo the last commit but keep the files
git reset --soft HEAD~1

# Now the files are still changed but not committed
# Fix what you need, then commit again
```

## "Git says I can't pull because of local changes"

```bash
# Save your changes temporarily
git stash

# Pull the latest
git pull origin main

# Get your changes back
git stash pop
```

## "I pushed my .env file by accident (API key leaked!)"

```bash
# Step 1: Delete the key from Groq console immediately
# Step 2: Create a new key
# Step 3: Remove .env from Git tracking

git rm --cached .env
git commit -m "Removed .env from tracking"
git push origin YOUR-BRANCH

# Step 4: Make sure .env is in .gitignore
# Step 5: Update .env with new key locally
```

---

# PART 11 — QUICK REFERENCE CARD (Print This)

```
╔══════════════════════════════════════════════╗
║          GIT QUICK REFERENCE                 ║
╠══════════════════════════════════════════════╣
║                                              ║
║  START OF WORK SESSION:                      ║
║    git pull origin main                      ║
║    git checkout YOUR-BRANCH                  ║
║                                              ║
║  SAVE YOUR WORK:                             ║
║    git add .                                 ║
║    git commit -m "what I did"                ║
║    git push origin YOUR-BRANCH               ║
║                                              ║
║  CHECK STATUS:                               ║
║    git status                                ║
║    git log --oneline -5                      ║
║                                              ║
║  UNDO LAST CHANGE:                           ║
║    git checkout -- filename                  ║
║                                              ║
║  SEE WHAT BRANCH YOU'RE ON:                  ║
║    git branch                                ║
║                                              ║
║  BRANCHES:                                   ║
║    Sagar    → backend-sagar                  ║
║    Poojitha → backend-poojitha               ║
║    Sai Tej  → extension-saitej               ║
║    Prithvi  → extension-prithvi              ║
║                                              ║
║  GOLDEN RULE:                                ║
║    Never edit a file that isn't yours         ║
║                                              ║
╚══════════════════════════════════════════════╝
```

---

# PART 12 — PERSON-SPECIFIC GIT CHEAT SHEETS

## 📋 Sagar's Git Cheat Sheet (Tech Lead)

**Your extra responsibilities:**
1. Create the repo
2. Create all branches
3. Merge all branches to main
4. Fix any merge conflicts
5. Final testing after all merges

**Commands you run that others don't:**
```bash
# Create branches (once)
git branch backend-sagar
git branch backend-poojitha
git branch extension-saitej
git branch extension-prithvi
git push origin --all

# Merge branches (after teammates finish)
git checkout main
git pull origin main
git merge BRANCH-NAME
git push origin main
```

---

## 📋 Poojitha's Git Cheat Sheet (Semi-Technical)

**Every time you start working:**
```bash
cd Desktop/prompt-guardian
source venv/bin/activate       # Mac
venv\Scripts\activate          # Windows
git pull origin main
git checkout backend-poojitha
```

**Every time you finish a piece:**
```bash
git add .
git commit -m "describe what you did"
git push origin backend-poojitha
```

**When Sagar says "pull main":**
```bash
git checkout main
git pull origin main
git checkout backend-poojitha
git merge main
```

**Files you touch:** groq_checker.py, sanitizer.py, analyzer.py
**Files you NEVER touch:** patterns.py, scorer.py, app.py, anything in extension/

---

## 📋 Sai Tej's Git Cheat Sheet (Non-Technical)

**Every time you start working:**
```bash
cd Desktop/prompt-guardian
git pull origin main
git checkout extension-saitej
```

**Every time you finish a piece:**
```bash
git add .
git commit -m "describe what you did"
git push origin extension-saitej
```

**When Sagar says "pull main":**
```bash
git checkout main
git pull origin main
git checkout extension-saitej
git merge main
```

**Files you touch:** manifest.json, content.js
**Files you NEVER touch:** anything in firewall/, app.py, popup.html, popup.js

---

## 📋 Prithvi's Git Cheat Sheet (Non-Technical)

**Every time you start working:**
```bash
cd Desktop/prompt-guardian
git pull origin main
git checkout extension-prithvi
```

**Every time you finish a piece:**
```bash
git add .
git commit -m "describe what you did"
git push origin extension-prithvi
```

**When Sagar says "pull main":**
```bash
git checkout main
git pull origin main
git checkout extension-prithvi
git merge main
```

**Files you touch:** popup.html, popup.js
**Files you NEVER touch:** anything in firewall/, app.py, manifest.json, content.js

**Exception:** You may edit the CSS inside content.js ONLY after Sai Tej's branch is merged. Ask Sagar first.

---

> **Remember: Git is your safety net. Commit early, commit often. If something breaks, you can always go back. The worst thing you can do is NOT commit for 3 hours and then lose everything.**