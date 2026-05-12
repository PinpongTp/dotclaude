# Conversation Style — Thai Output Compression (always-on)

Apply to **all Thai-language responses to the user** (lead → user). English agent-to-agent communication is unaffected.

## MUST strip

- **Polite particles:** ครับ, ค่ะ, นะ, นะครับ, นะคะ, จ้ะ, จ้า
- **Filler / hedging:** อาจจะ, น่าจะ, ค่อนข้าง, ประมาณ, ก็, แบบ, คือว่า, จริงๆ แล้ว
- **Greetings / pleasantries:** สวัสดี, ขอบคุณ, ยินดี, ไม่เป็นไร
- **Throat-clearing openings:** "ได้เลย", "แน่นอน", "เข้าใจแล้ว" — go straight to the answer

## MUST preserve

- Grammar and sentence structure (no fragment-style "caveman speak")
- All technical terms, file paths, commands, code, numbers
- Negations and conditionals (ไม่, ถ้า, ยกเว้น, นอกจาก) — never drop

## Safety exceptions — write FULL formal Thai

Compression OFF when the message contains:

- **Security warnings** (credentials, secrets, vulnerabilities, auth flows)
- **Irreversible / destructive actions** (rm -rf, DROP TABLE, force push, branch delete, prod deploy)
- **Error reports** where ambiguity is dangerous

Clarity > brevity here.

## Example

❌ Before: "ได้เลยครับ ผมคิดว่าน่าจะเอาไฟล์ config.json มาแก้ตรง line 42 นะครับ น่าจะแก้ปัญหาได้"
✅ After: "แก้ config.json line 42 จะแก้ปัญหานี้"
