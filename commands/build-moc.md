Build or update a Map of Content for: $ARGUMENTS

1. Search `20-notes/` for all notes related to the topic
   - Check tags, titles, and content
   - Include papers, concepts, code patterns, experiments

2. Organize found notes into sections:
   - **Core Concepts**: Foundational ideas, prerequisites first
   - **Key Papers**: Research papers, ordered by influence/date
   - **Implementations**: Code patterns, practical guides
   - **Experiments**: Related experiment logs
   - **Databricks Integration**: Platform-specific notes if relevant
   - **Open Questions**: Unanswered questions, areas to explore

3. Create MOC structure:
   ```markdown
   ---
   type: moc
   domain: [appropriate domain tag]
   updated: [today's date]
   ---
   
   # MOC: {Topic Name}
   
   Brief description of what this topic covers.
   
   ## Core Concepts
   - [[concept-x]] - brief description
   
   ## Key Papers
   - [[paper-y]] - what it contributes
   
   ... etc
   ```

4. Add Dataview query for dynamic updates where useful

5. Save to `10-mocs/MOC-{Topic}.md`

6. Update any existing notes that should link to this MOC
