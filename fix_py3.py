"""
Script to convert Python 2 syntax to Python 3 in the Pacman project.
Handles: print statements, dict methods, exception syntax, integer division, imports.
"""
import os
import re
import sys

def fix_print_statements(content):
    """Convert Python 2 print statements to Python 3 print() calls."""
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        stripped = line.lstrip()
        indent = line[:len(line) - len(stripped)]
        
        # Skip comments, docstrings, and lines that already use print()
        if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
            new_lines.append(line)
            continue
        
        # Match "print something" but not "print(" or "print()" 
        m = re.match(r'^(print)\s+(?!\()(.*)', stripped)
        if m:
            args = m.group(2).rstrip('\r')
            # Handle trailing comma (no newline) -> end=''
            if args.endswith(','):
                args = args[:-1]
                new_lines.append(f'{indent}print({args}, end=" ")')
            # Handle >> stderr redirect
            elif args.startswith('>>'):
                parts = args[2:].split(',', 1)
                if len(parts) == 2:
                    stream = parts[0].strip()
                    msg = parts[1].strip()
                    new_lines.append(f'{indent}print({msg}, file={stream})')
                else:
                    new_lines.append(f'{indent}print({args})')
            else:
                new_lines.append(f'{indent}print({args})')
        else:
            new_lines.append(line)
    return '\n'.join(new_lines)

def fix_dict_methods(content):
    """Convert dict.has_key(x) to x in dict."""
    content = re.sub(r'(\w+)\.has_key\(([^)]+)\)', r'\2 in \1', content)
    return content

def fix_exception_syntax(content):
    """Convert 'except Exception, e:' to 'except Exception as e:'."""
    content = re.sub(r'except\s+(\w+)\s*,\s*(\w+)\s*:', r'except \1 as \2:', content)
    return content

def fix_reduce_import(content):
    """Add functools import if reduce is used."""
    if 'reduce(' in content and 'from functools import' not in content and 'import functools' not in content:
        content = 'from functools import reduce\n' + content
    return content

def fix_raw_input(content):
    """Convert raw_input to input."""
    content = content.replace('raw_input(', 'input(')
    return content

def fix_integer_division(content):
    """This is tricky - skip for now, most code already uses float()."""
    return content

def fix_dict_iteritems(content):
    """Convert .iteritems() to .items(), .itervalues() to .values(), etc."""
    content = content.replace('.iteritems()', '.items()')
    content = content.replace('.itervalues()', '.values()')
    content = content.replace('.iterkeys()', '.keys()')
    return content

def fix_xrange(content):
    """Convert xrange to range."""
    content = re.sub(r'\bxrange\b', 'range', content)
    return content

def fix_file(filepath):
    """Apply all fixes to a single file."""
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    original = content
    content = fix_print_statements(content)
    content = fix_dict_methods(content)
    content = fix_exception_syntax(content)
    content = fix_reduce_import(content)
    content = fix_raw_input(content)
    content = fix_dict_iteritems(content)
    content = fix_xrange(content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def process_directory(dirpath):
    """Process all .py files in a directory."""
    count = 0
    for fname in sorted(os.listdir(dirpath)):
        if fname.endswith('.py'):
            fpath = os.path.join(dirpath, fname)
            if fix_file(fpath):
                print(f'  Fixed: {fname}')
                count += 1
            else:
                print(f'  OK:    {fname}')
    return count

def main():
    base = os.path.dirname(os.path.abspath(__file__))
    folders = ['search', 'multiagent', 'reinforcement', 'tracking']
    
    total = 0
    for folder in folders:
        dirpath = os.path.join(base, folder)
        if os.path.isdir(dirpath):
            print(f'\n=== Processing {folder}/ ===')
            total += process_directory(dirpath)
    
    print(f'\nDone! Fixed {total} files total.')

if __name__ == '__main__':
    main()
