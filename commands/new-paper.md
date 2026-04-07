Create a new paper note from: $ARGUMENTS

## Step 1: Fetch Paper Information
1. If a URL is provided (arxiv, paper link), fetch the paper metadata
2. If just a title/description, use that as the basis
3. Look for GitHub/code repository links:
   - Check the arxiv abstract page for "Code" links
   - Search the paper page for github.com URLs
   - Check for "paperswithcode" links

## Step 2: Deep Knowledge Base Search
Before creating the note, search extensively for related content:
1. Search `20-notes/` for concept notes related to the paper's key topics
2. Search `20-notes/` for other papers on similar topics
3. Search `01-projects/` for active projects this paper might apply to
4. Search `10-mocs/` for relevant Maps of Content
5. Identify specific techniques, architectures, or methods mentioned that match existing notes

## Step 3: Create Comprehensive Note
Use the paper template from `30-templates/` but expand each section:

### Frontmatter
- type: paper
- status: reading
- arxiv: (extract if available)
- github: (extract if available, empty string if not found)
- year: (extract from paper)
- authors: (list authors)
- tags: [paper, domain/...] - be specific with tags
- date_added: today's date

### Key Contribution
- 2-3 sentences explaining the main contribution
- Why this matters in the broader field

### Core Ideas (Expanded)
- List 4-6 core ideas with 1-2 sentence explanations each
- For each idea, note if it relates to an existing concept note: "Related: [[concept-name]]"
- Explain novel terminology introduced

### Method (Detailed)
- Describe the approach in 3-5 bullet points
- Include architecture details if applicable
- Note any interesting implementation choices
- Compare to existing methods: "Unlike X, this approach..."

### Results
- Key benchmarks with specific numbers if available
- Comparison to baselines/SOTA
- Notable strengths and limitations mentioned

### Relevance to My Work (Personalized)
This section should be detailed and specific:
- **Active Projects**: For each relevant project in `01-projects/`, explain specifically how this paper applies
- **Concepts to Update**: List any existing concept notes that should be updated with insights from this paper
- **Customer Applications**: Consider how this might apply to customer use cases (I work as AI SSA at Databricks)
- **Learning Goals**: Connect to my 2026 learning goals (Agentic Design, Fine-tuning, Inference Optimization)
- **Practical Takeaways**: What can I immediately apply or experiment with?

### Implementation Notes
- Prerequisites or dependencies
- Estimated complexity to implement
- Potential Databricks integration points

### Citations to Explore
- List 3-5 key references from the paper worth reading
- Note which ones might already exist in the knowledge base

### Related Notes (Comprehensive)
- Link to ALL relevant existing notes found in Step 2
- Group by type: Concepts, Papers, Guides, Projects

## Step 4: Save and Integrate
1. Save to `20-notes/paper-{short-name}-{year}.md`
2. Suggest which MOC(s) this belongs to
3. Suggest if any existing notes should be updated to reference this paper
