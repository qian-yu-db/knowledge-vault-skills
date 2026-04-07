Find and review outdated notes in the vault.

1. Search for notes that may be outdated:
   - `last_verified` date older than 90 days
   - Tags containing `status/review-needed` or `confidence/needs-review`
   - Databricks feature notes (these change frequently)
   - Code patterns with `version_context` that may be stale

2. For each outdated note found, report:
   - Filename
   - Type
   - Last verified/modified date
   - Why it's flagged (age, tag, version-sensitive)

3. Group results by priority:
   - **High**: Databricks features, actively-used code patterns
   - **Medium**: Papers with implementations, model cards
   - **Low**: Concepts, archived experiments

4. Ask which notes to review, then for each selected note:
   - Show current content
   - Search web for updated information if relevant
   - Suggest updates or deprecation
   - Update `last_verified` date after review
   - Add deprecation warning if content is obsolete (don't delete)
