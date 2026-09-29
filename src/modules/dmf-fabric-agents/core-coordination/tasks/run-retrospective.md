# Task: Run Retrospective

**Command:** `*retrospective` / `*RT`  
**Output:** `retrospective.md`

---

## Objective

Facilitate a structured retrospective to gather feedback, identify improvements, and create actionable items for the next iteration.

---

## Prerequisites

- [ ] Iteration/sprint complete
- [ ] Participants identified
- [ ] Previous retrospective actions reviewed
- [ ] Data/metrics gathered

---

## Steps

### Step 1: Set the Stage

Prepare for the retrospective:

```yaml
setup:
  duration: "60-90 minutes"
  
  participants:
    - role: "facilitator"
      agent: "iteration-improvement"
    - role: "participants"
      agents: ["relevant_agents"]
      humans: ["relevant_humans"]
      
  ground_rules:
    - "Vegas rule - what's said here stays here"
    - "No blame - focus on process"
    - "Everyone participates"
    - "Respect all perspectives"
    - "Be constructive"
```

### Step 2: Gather Data

Collect feedback using chosen format:

**Start-Stop-Continue:**
```markdown
### Start Doing
- {things to begin}

### Stop Doing
- {things to cease}

### Continue Doing
- {things to maintain}
```

**Or 4Ls:**
```markdown
### Liked 👍
- {positives}

### Learned 📚
- {learnings}

### Lacked 😕
- {missing things}

### Longed For 💭
- {wishes}
```

### Step 3: Generate Insights

Analyze patterns:

1. **Theme Identification** - Group similar items
2. **Voting** - Prioritize top items
3. **Discussion** - Explore top themes
4. **Root Cause** - Dig into issues

### Step 4: Decide What to Do

Create action items:

```yaml
action_item:
  description: "{specific action}"
  owner: "{person/agent}"
  deadline: "{date}"
  success_metric: "{how we measure}"
  priority: "high|medium|low"
```

### Step 5: Close the Retrospective

Wrap up:

1. **Summarize** - Key takeaways
2. **Appreciate** - Thank participants
3. **Commit** - Confirm action items
4. **Schedule** - Next retrospective

### Step 6: Document

Create retrospective.md with all content.

---

## Output Template

```markdown
# Retrospective

**Date:** {date}  
**Iteration:** {iteration_name}  
**Facilitator:** Kai (IterationImprovement)

## Participants
- {list of participants}

## Previous Actions Review
| Action | Owner | Status | Notes |
|--------|-------|--------|-------|
| {action} | {owner} | ✅/⏳/❌ | {notes} |

## What Went Well 🎉

### Theme: {theme_1}
- {item}
- {item}

### Theme: {theme_2}
- {item}

## What Didn't Go Well 😓

### Theme: {theme_1}
- {item}
- {item}

### Theme: {theme_2}
- {item}

## Lessons Learned 📚
1. {lesson}
2. {lesson}

## Action Items 📋

| # | Action | Owner | Deadline | Priority |
|---|--------|-------|----------|----------|
| 1 | {action} | {owner} | {date} | High |
| 2 | {action} | {owner} | {date} | Medium |

## Appreciation 🙏
{Recognition of team/agent contributions}

## Next Retrospective
**Scheduled:** {date}
```

---

## Validation

- [ ] All participants contributed
- [ ] Both positives and negatives captured
- [ ] Themes identified
- [ ] Action items are SMART
- [ ] Owners committed
- [ ] Document complete
