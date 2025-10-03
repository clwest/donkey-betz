# 📤 Upload Instructions for AI Systems

## Quick Upload Guide

### Option 1: Single Master File (Recommended for GPT-5/Claude)
1. Open `master_context_all.md` 
2. Select all text (Ctrl+A / Cmd+A)
3. Copy (Ctrl+C / Cmd+C)
4. Paste into AI chat
5. The AI now has complete context of your project!

### Option 2: Split Files (For size limits)
If the master file is too large:
1. Upload `master_context_part_01.md` first
2. Then upload subsequent parts in order
3. Each part builds on the previous

### Option 3: Original Chunks (Maximum control)
Use the individual chunk files in `donkey_betz_chunks/` for:
- Selective context loading
- Specific feature discussions
- Memory-efficient processing

## File Types to Upload

### Essential Files:
- `master_context_all.md` - Complete documentation context
- `donkey_betz_analysis/overview_*.md` - High-level project summary

### Optional Files (skip JSON for now):
- `donkey_betz_analysis/detailed_report_*.json` - Only if AI requests specific data
- `donkey_betz_analysis/features_timeline_*.json` - Only for timeline questions

## Tips for Best Results

1. **Start with the master file** - It contains everything organized
2. **JSON files are optional** - The markdown files contain all key information
3. **Tell the AI what you want** - Be specific about what insights you need
4. **Reference the overview** - Point the AI to the overview for quick understanding

## Sample Prompts After Upload

```
"You now have complete context of my 18-month project. Please provide:
1. A executive summary of what I've built
2. The key technical achievements
3. Recommendations for next steps"
```

```
"Based on the documentation, what are the most innovative aspects of this platform?"
```

```
"Identify any patterns in how I solve problems across the project"
```

## File Size Reference

- Master file: ~10-15 MB (should work with GPT-5/Claude)
- Individual chunks: ~200-300 KB each
- Overview: ~50-100 KB

## Troubleshooting

**File too large?**
- Use the split versions in `master_parts/`
- Or use individual chunks

**AI not understanding context?**
- Start with the overview file first
- Then add the master context

**Need specific features only?**
- Use the document index to find relevant chunks
- Upload only those specific chunks
