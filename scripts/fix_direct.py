#!/usr/bin/env python3
"""
Fix markup in CURRENT document directly.
Patterns to fix:
1. **  word **  -> **word** (remove spaces inside emphasis)
2. word**word   -> word** word (space at glued boundary)
3. **word**word -> **word** word (space after closing)
4. word**word** -> word** word** (space between emphases)
"""

import re
from pathlib import Path

REPO = Path(r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator')
REL = 'v0.3-prelim/docs/PAPER_V1_DRAFT.md'

CUR = (REPO/REL).read_text(encoding='utf-8').split('\n')

def in_code_span(line, pos, code_ranges):
    return any(a <= pos < b for a,b in code_ranges)

def get_code_ranges(line):
    ranges = []
    i = 0
    while i < len(line):
        m = re.match(r'(`+)', line[i:])
        if not m: break
        t = m.group(1)
        c = line.find(t, i + len(t))
        if c == -1: break
        ranges.append((i, c + len(t)))
        i = c + len(t)
    return ranges

def fix_line(line):
    """Fix markup in a single line."""
    code_ranges = get_code_ranges(line)
    
    # First pass: fix **  word **  -> **word**
    # Find all ** pairs
    stars = []
    for m in re.finditer(r'\*\*', line):
        if not in_code_span(line, m.start(), code_ranges):
            stars.append(m.start())
    
    if len(stars) < 2:
        return line
    
    # Process pairs of ** (opening/closing)
    # Build output by processing segments
    out = []
    last = 0
    
    for i in range(0, len(stars), 2):
        if i + 1 >= len(stars):
            # Unmatched - just copy
            out.append(line[last:])
            last = len(line)
            break
        
        open_pos = stars[i]
        close_pos = stars[i+1]
        
        # Text before opening **
        out.append(line[last:open_pos])
        
        # Content between ** **
        content = line[open_pos+2:close_pos]
        
        # Fix: remove leading/trailing spaces from content
        content = content.strip()
        
        # Write fixed emphasis
        out.append('**' + content + '**')
        
        last = close_pos + 2
    
    # Remaining text
    out.append(line[last:])
    
    line = ''.join(out)
    
    # Second pass: fix glued boundaries word**word
    # Re-scan for ** positions
    code_ranges = get_code_ranges(line)
    stars = []
    for m in re.finditer(r'\*\*', line):
        if not in_code_span(line, m.start(), code_ranges):
            stars.append(m.start())
    
    if len(stars) < 2:
        return line
    
    out = []
    last = 0
    for idx, pos in enumerate(stars):
        out.append(line[last:pos+2])
        
        # Check if next ** is glued (word char on both sides of boundary)
        if idx + 1 < len(stars):
            next_pos = stars[idx+1]
            # Text between this ** and next **
            between = line[pos+2:next_pos]
            
            # If between is empty, check boundary chars
            if between == '':
                # Check char before this ** and after next **
                before = line[pos-1] if pos > 0 else ''
                after = line[next_pos+2] if next_pos+2 < len(line) else ''
                if before.isalnum() and after.isalnum():
                    # word**word - insert space
                    out.append(' ')
            else:
                # There's content between - check if it's glued to next **
                # e.g., word**content**word -> word**content** word
                if between and between[-1].isalnum() and next_pos+2 < len(line) and line[next_pos+2].isalnum():
                    out.append(' ')
        
        last = pos + 2
    
    out.append(line[last:])
    return ''.join(out)

def render_literal_count(text):
    from markdown_it import MarkdownIt
    md = MarkdownIt('commonmark')
    return re.sub(r'<[^>]+>','', md.render(text)).count('**')

# Apply fix to all lines
new_lines = [fix_line(l) for l in CUR]

# Verify
old_lit = sum(render_literal_count(l) for l in CUR if l.strip())
new_lit = sum(render_literal_count(l) for l in new_lines if l.strip())
print(f"CUR literal **: {old_lit}")
print(f"NEW literal **: {new_lit}")

# Check specific known problem lines
test_lines = [102, 129, 134, 135, 136, 137, 138, 139, 168, 198, 869, 870, 871, 872, 873, 877, 881, 883, 886, 888, 889, 927, 1081, 1145, 1176, 1177, 1178, 1690, 1692, 1697, 1710, 1748, 1750, 1752]
for ln in test_lines:
    if ln <= len(new_lines):
        lit = render_literal_count(new_lines[ln-1])
        if lit > 0:
            print(f"  L{ln}: STILL {lit} literal ** | {new_lines[ln-1][:150]}")

# Write
out = '\n'.join(new_lines)
(REPO/REL).write_text(out, encoding='utf-8')
print(f"\nWritten {len(new_lines)} lines")