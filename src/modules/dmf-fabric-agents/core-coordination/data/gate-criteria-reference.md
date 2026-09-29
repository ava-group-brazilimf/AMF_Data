# Gate Criteria Reference

**Reference:** Orion (Migration Coordinator) Agent  
**Version:** 1.0

---

## Gate Framework Overview

The AI-Agent Migration Factory uses a 3-gate Stage-Gate framework to ensure quality at each phase transition.

---

## Gate 1: UPSTREAM → MIDSTREAM

| Criterion | Source Agent | Threshold | Weight |
|-----------|:----------:|-----------|:------:|
| Inventory completeness | Scout 🔍 | 100% scope scanned | 25% |
| Dependency graph validity | Scout 🔍 | Zero unresolved cycles | 20% |
| Pseudocode confidence | Logan 🧠 | >= 85% per pipeline | 25% |
| Digital twin completeness | Logan 🧠 | All entities mapped | 15% |
| SME validation | Human | 20% sample reviewed | 15% |

---

## Gate 2: MIDSTREAM → DOWNSTREAM

| Criterion | Source Agent | Threshold | Weight |
|-----------|:----------:|-----------|:------:|
| First-attempt approval rate | Vera ✅ | >= 85% | 20% |
| Self-healing success rate | Phoenix 🔧 | >= 75% | 15% |
| Compliance status | Shield 🔒 | Zero violations | 25% |
| Unit test pass rate | Vera ✅ | 100% | 20% |
| Performance estimate | Vera ✅ | >= baseline | 10% |
| PII masking validation | Shield 🔒 | 100% masked | 10% |

---

## Gate 3: DOWNSTREAM → PRODUCTION

| Criterion | Source Agent | Threshold | Weight |
|-----------|:----------:|-----------|:------:|
| Data parity | Balance ⚖️ | >= 99.9% | 30% |
| Pipeline execution | Target | 100% running | 20% |
| Documentation | Scribe 📚 | 100% complete | 10% |
| Dry run success | Ops | Min 2x successful | 15% |
| Stakeholder sign-off | Human | PM + Sponsor + Security | 25% |

---

## Scoring Formula

```
Gate Score = Σ (criterion_pass × weight)

PASS:        Score >= 100%
CONDITIONAL: Score >= 80% AND no critical failures
FAIL:        Score < 80% OR any critical failure
```
