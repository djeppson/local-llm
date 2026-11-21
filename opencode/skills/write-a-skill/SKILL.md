---
name: write-a-skill
description: Create new agent skills conforming to the Agent Skills open standard — structure, frontmatter rules, progressive disclosure, bundled scripts and references. Use when user wants to create, write, or build a new skill.
---

# Writing Skills

Skills follow the **Agent Skills open standard** (spec: agentskills.io; GitHub org `agentskills`). Anthropic published it as an open standard in December 2025 and donated it to the **Agentic AI Foundation** (AAIF, Linux Foundation — the same home as MCP) in October 2026; 70+ agent platforms integrate it, including OpenCode. There are no versioned releases yet — build against the spec in the repository.

## Process

1. **Gather requirements** - ask user about:

   - What task/domain does the skill cover?
   - What specific use cases should it handle?
   - Does it need executable scripts or just instructions?
   - Any reference materials to include?

1. **Draft the skill** - create:

   - `SKILL.md` with frontmatter and concise instructions (required)
   - `references/` files for detailed docs, `assets/` for templates and data, `scripts/` for deterministic operations (all optional)

1. **Review with user** - present draft and ask:

   - Does this cover your use cases?
   - Anything missing or unclear?
   - Should any section be more/less detailed?

## Skill Structure (per the standard)

```
skill-name/
├── SKILL.md           # Frontmatter + instructions (required)
├── references/        # Detailed docs (optional)
├── assets/            # Templates, data files (optional)
└── scripts/           # Utility scripts (optional)
```

Legacy note: older skills in this repo use flat `REFERENCE.md` / `EXAMPLES.md` files. They keep working, but new skills use the standard's directories.

## Frontmatter Rules

- **`name`** (required): 1–64 characters, lowercase letters/digits/single hyphens, not starting or ending with a hyphen, and **must match the folder name**.
- **`description`** (required): max 1024 chars — see trigger guidance below.
- Optional: `license`; `compatibility` (free text — environment needs); `metadata` (e.g. OpenCode's `opencode/autoinvoke: false` for load-by-ID-only skills); `allowed-tools` (experimental — harness support varies).

## Description Requirements

The description is **the only thing your agent sees** when deciding which skill to load. It's surfaced in the system prompt alongside all other installed skills. Your agent reads these descriptions and picks the relevant skill based on the user's request.

**Goal**: Give your agent just enough info to know:

1. What capability this skill provides
1. When/why to trigger it (specific keywords, contexts, file types)

**Format**:

- Max 1024 chars
- Write in third person
- First sentence: what it does
- Second sentence: "Use when [specific triggers]"

**Good example**:

```
Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when user mentions PDFs, forms, or document extraction.
```

**Bad example**:

```
Helps with documents.
```

The bad example gives your agent no way to distinguish this from other document skills.

## Progressive Disclosure

The standard formalizes three loading stages:

1. **Always visible:** `name` + `description` of every installed skill — the model's router.
1. **On trigger:** the full SKILL.md body loads when the request matches.
1. **On demand:** linked reference files and scripts load only when the body calls for them.

Implication: the description is the router, SKILL.md is the manual, bundled files are the library. Never put library content in the manual.

## When to Add Scripts

Add utility scripts when:

- Operation is deterministic (validation, formatting)
- Same code would be generated repeatedly
- Errors need explicit handling

Scripts save tokens and improve reliability vs generated code.

## When to Split Files

Split into `references/` files when:

- SKILL.md exceeds 100 lines
- Content has distinct domains (finance vs sales schemas)
- Advanced features are rarely needed

## Review Checklist

After drafting, verify:

- [ ] `name` matches the folder name, 1–64 chars, lowercase/digits/hyphens
- [ ] Description ≤1024 chars and includes triggers ("Use when...")
- [ ] SKILL.md under 100 lines
- [ ] No time-sensitive info
- [ ] Consistent terminology
- [ ] Concrete examples included
- [ ] References one level deep

## Watch upstream (AAIF)

The AAIF roadmap proposes versioned releases, a formal proposal process, and **security guidance for people who write and install skills** — none shipped yet. When they land, reconcile this skill with them; until then, this skill's guidance fills that gap.
