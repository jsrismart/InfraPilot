from diagram_generator import TerraformParser, DiagramGenerator

tf = '''resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}
resource "aws_subnet" "pub" {
  vpc_id = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
}
resource "aws_instance" "web" {
  subnet_id = aws_subnet.pub.id
}
'''

p = TerraformParser(tf)
g = DiagramGenerator(p)
m = g.generate_mermaid_diagram()
print('=== MERMAID OUTPUT ===')
print(m)
print()
print('=== SYNTAX ANALYSIS ===')
lines = m.split('\n')
print(f'Total lines: {len(lines)}')
print()

# Check for common Mermaid syntax issues
print("Checking for syntax issues:")
open_brackets = 0
open_quotes = 0
open_braces = 0

for i, line in enumerate(lines, 1):
    # Count brackets
    open_brackets += line.count('[')
    close_brackets = line.count(']')
    open_brackets -= close_brackets
    
    # Count quotes
    if line.count('"') % 2 != 0:
        print(f"⚠️ Line {i} has odd quotes: {repr(line)}")
    
    # Look for unclosed brackets
    if '[' in line:
        close = line.count(']')
        open_in_line = line.count('[')
        if open_in_line != close:
            print(f"Line {i}: [ count={open_in_line}, ] count={close}: {repr(line)}")

print(f"\nFinal bracket balance: {open_brackets} (should be 0)")
print("✅ Diagram generated successfully" if open_brackets == 0 else "❌ Syntax error detected")
