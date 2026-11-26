---
name: new-customer
description: Creates a new customer or engagement note in the vault's 02-customers/ folder from the customer-note template, optionally tagged with an engagement or ticket ID. Use when the user starts work with a new customer or engagement and wants a note for it.
argument-hint: "<customer-name> [engagement-id]"
arguments: [customer, engagement_id]
allowed-tools: Read, Glob, Bash(date *)
---

# New Customer Note

Customer: `$customer` · Engagement ID: `$engagement_id` (optional)

## Setup

- **Vault root**: `${user_config.vault_path}`. If blank or a literal placeholder, use the current working directory.
- If the vault `CLAUDE.md` names a different customers folder, use it. Otherwise use `02-customers/`.
- Today: !`date +%Y-%m-%d`

## Steps

1. **Filename**: `customer-<CustomerName>.md`, or `customer-<CustomerName>-<engagement_id>.md` if an ID was given. Use the user's spelling of the name, with spaces as hyphens.
2. **Duplicate check**: Glob the customers folder for an existing note with the same customer name. If one exists, show it and ask whether to create a new engagement note or open the existing one.
3. **Create** from `30-templates/customer-note.md`. Fill in `customer_name`, `created`, `last_updated` (today) and the title. Add `engagement_id` to the frontmatter if one was given. Remove template comments that are only prompts, and leave the other sections for the user.
4. Tell the user the path and list the sections that need input.
