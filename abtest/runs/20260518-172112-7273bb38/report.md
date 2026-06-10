# A/B Test Report

> **Target**: `/Users/pinpongt/.claude/rules/conversation.md`  
> **Run ID**: `20260518-172112-7273bb38`  
> **Started**: 2026-05-18T17:21:12.510929  
> **Finished**: 2026-05-18T17:23:13.999740  
> **Model (runner)**: `sonnet`  
> **Model (judge)**: `sonnet`  

## Summary

### Derived tests — 1 total

| outcome | count |
|---|---|
| ⚪ redundant | 1 |

## Verdict (at a glance)

| # | outcome | id | without → with | claim |
|---|---|---|---|---|
| 1 | ⚪ redundant | `no-polite-particles` | ✅ PASS → ✅ PASS | Thai responses must not contain polite particles: ครับ, ค่ะ, นะ, นะครับ, นะคะ, จ้ะ, จ้า |

## Metrics

Averages across derived tests (per call):

| metric | without | with | diff |
|---|---|---|---|
| input tokens | 3 | 3 | +0.0% |
| output tokens | 682 | 631 | -7.5% |
| turns | 1.00 | 1.00 | — |
| cost total | $0.0474 | $0.0486 | — |

**Tool set diff**

| variant | tools |
|---|---|
| only `with` | _none_ |
| only `without` | _none_ |
| shared | _none_ |

---

## Derived test detail

### 1. ⚪ redundant — `no-polite-particles`

**Claim**: Thai responses must not contain polite particles: ครับ, ค่ะ, นะ, นะครับ, นะคะ, จ้ะ, จ้า

**Prompt sent**:

```
ช่วยอธิบายว่า git rebase กับ git merge ต่างกันอย่างไร
```

**Pass criteria**:

- **must_not_contain**: `ครับ`, `ค่ะ`, `\bนะ\b`, `นะครับ`, `นะคะ`, `จ้ะ`, `จ้า`
- **must_contain**: `rebase`, `merge`
- **judge_question**: Is the response in Thai and free of polite sentence-ending particles while still using complete, grammatically correct sentences?

#### Without rule — ✅ PASS

_Reason_: all regex checks passed

<details><summary>Response</summary>

_1072 chars · 682 output tokens · 1 turns · $0.0474_

```
## Git Merge vs Git Rebase

ทั้งคู่ใช้รวม branch เข้าด้วยกัน แต่ทำงานต่างกัน:

---

### `git merge`

``​`
main:    A - B - C - - - - M
                  \       /
feature:           D - E
``​`

- สร้าง **merge commit (M)** ใหม่ที่รวม history ของทั้งสอง branch
- **ประวัติยังคงสมบูรณ์** เห็นว่า branch ถูกสร้างเมื่อไหร่และรวมเมื่อไหร่
- ปลอดภัย — ไม่แก้ไข commit เดิม

### `git rebase`

``​`
main:    A - B - C
                  \
feature:           D' - E'   ← D, E ถูก "ย้าย" มาต่อจาก C
``​`

- นำ commit ใน feature branch ไป **ต่อท้าย** ปลายของ main
- ได้ history ที่ **เป็นเส้นตรง** ดูสะอาดกว่า
- **เขียน commit ใหม่** (D→D', E→E') — SHA เปลี่ยน

---

### เลือกใช้อะไร?

| สถานการณ์ | แนะนำ |
|---|---|
| Feature branch ส่วนตัว (ยังไม่ push) | `rebase` — history สะอาด |
| Branch ที่ push และคนอื่น pull ไปแล้ว | `merge` — ปลอดภัยกว่า |
| อยาก trace ว่า feature ถูกสร้างจาก branch ไหน | `merge` |
| อยากให้ log เป็นเส้นตรง อ่านง่าย | `rebase` |

**กฎง่ายๆ:** ถ้า branch ยังอยู่คนเดียว → `rebase`. ถ้า share กับคนอื่นแล้ว → `merge` เพื่อหลีกเลี่ยง "rewriting public history"
```

</details>

#### With rule — ✅ PASS

_Reason_: all regex checks passed

<details><summary>Response</summary>

_1102 chars · 631 output tokens · 1 turns · $0.0486_

```
## Git Merge vs Git Rebase

### Git Merge
รวม branch โดย**สร้าง merge commit ใหม่** ที่มี 2 parents:

``​`
main:   A---B---C
                 \
feature:          D---E
                       \
after merge:      M  ← merge commit
``​`

- ประวัติตรงไปตรงมา เห็นว่า branch แยกและ merge เมื่อไหร่
- Non-destructive — ไม่แก้ไข commit เดิม
- ประวัติรก ถ้า branch เยอะ

### Git Rebase
ย้าย commit ของ branch ไป**ต่อท้าย** branch เป้าหมาย โดย rewrite commit ใหม่:

``​`
main:    A---B---C
feature (before): A---B---D---E
feature (after):  A---B---C---D'---E'
``​`

- ประวัติเป็นเส้นตรง สะอาด อ่านง่าย
- Rewrites commit hash (D→D', E→E') — **destructive**
- ห้าม rebase branch ที่ push ขึ้น remote แล้ว (คนอื่นจะ conflict)

---

### เลือกใช้อะไร?

| สถานการณ์ | ใช้ |
|---|---|
| Feature branch ส่วนตัว ยังไม่ push | `rebase` — ประวัติสะอาด |
| Branch ที่แชร์กับทีมแล้ว | `merge` — ปลอดภัย |
| ต้องการเห็น timeline ว่า merge เมื่อไหร่ | `merge` |
| อยากให้ `git log` อ่านง่ายเหมือนเส้นตรง | `rebase` |

**กฎง่ายๆ:** "Never rebase public branches" — ถ้า branch ยังอยู่แค่ local ใช้ rebase ได้ ถ้า push แล้ว ใช้ merge
```

</details>

---
