# Route Next Task

**Task ID:** route-next  
**Agent:** Orion (Migration Coordinator)  
**Version:** 1.0  
**Command:** `*route`  
**Phase:** CORE

---

## Purpose

Analyze the current migration state and recommend the best agent to handle the user's request or the next logical step.

---

## Execution Steps

### Step 1: Determine Current Phase

Load current wave status and identify active phase.

### Step 2: Match Request to Agent Expertise

```yaml
routing_matrix:
  "scan", "inventory", "discover": → Scout 🔍
  "extract logic", "pseudocode", "business rules": → Logan 🧠
  "generate code", "pyspark", "notebook": → Coda ⚙️
  "validate", "quality", "test": → Vera ✅
  "security", "compliance", "pii", "masking": → Shield 🔒
  "fix", "error", "heal", "debug": → Phoenix 🔧
  "reconcile", "compare", "checksum": → Balance ⚖️
  "document", "report", "lineage": → Scribe 📚
  "gate", "status", "rollback": → Orion 🧭 (self)
```

### Step 3: Present Recommendation

```
Based on your request and current phase ({phase}):

🎯 Recommended Agent: {agent_name} {icon}
   Reason: {rationale}
   Activate with: @{agent-id}

📋 Alternative Agents:
   1. {alt_agent_1} — {reason}
   2. {alt_agent_2} — {reason}
```

---

## Output

Routing recommendation displayed to user.
