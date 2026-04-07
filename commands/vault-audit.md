Perform a health audit of the knowledge base.

Check and report on:

## Structure Issues
- Notes in wrong directories (e.g., non-MOC in `10-mocs/`)
- Files not following naming conventions
- Empty or near-empty notes

## Metadata Issues  
- Notes missing frontmatter entirely
- Notes missing required fields for their type
- Invalid or inconsistent tag usage
- Missing `date_added` or `last_verified` dates

## Linking Health
- Orphan notes (no incoming or outgoing links)
- Broken links (`[[note]]` pointing to non-existent files)
- Notes that should be linked but aren't (similar topics)

## Content Freshness
- Notes older than 6 months without `last_verified`
- High count of `status/review-needed` tags
- Databricks notes not verified in 90+ days

## Statistics
- Total notes by type
- Notes per MOC
- Most connected notes (highest link count)
- Least connected notes
- Inbox size

Generate a report with:
1. Summary stats
2. Critical issues (broken links, missing frontmatter)
3. Warnings (orphans, outdated content)
4. Suggestions (potential new MOCs, linking opportunities)
