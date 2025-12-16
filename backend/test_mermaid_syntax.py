import json
import sys
sys.path.insert(0, '.')

from diagram_generator import TerraformParser, DiagramGenerator
from diagram_image_generator import AdvancedDiagramGenerator

tf_code = '''
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}
resource "aws_subnet" "main" {
  vpc_id = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
}
resource "aws_instance" "web" {
  subnet_id = aws_subnet.main.id
}
'''

parser = TerraformParser(tf_code)
gen = DiagramGenerator(parser)

print("=== MERMAID DIAGRAM ===")
mermaid = gen.generate_mermaid_diagram()
print(mermaid)
print("\n=== CHECKING FOR ISSUES ===")
print(f"Has emoji: {'🌐' in mermaid or '📡' in mermaid or '🖥️' in mermaid}")
print(f"Has quotes: {'\"' in mermaid}")
print(f"Has newline chars: {repr(mermaid).count(r'\\n')}")
print(f"Mermaid lines: {len(mermaid.splitlines())}")

# Check for unmatched brackets
open_brackets = mermaid.count('[')
close_brackets = mermaid.count(']')
print(f"\nBracket balance: [ = {open_brackets}, ] = {close_brackets}")

open_parens = mermaid.count('(')
close_parens = mermaid.count(')')
print(f"Paren balance: ( = {open_parens}, ) = {close_parens}")

open_braces = mermaid.count('{')
close_braces = mermaid.count('}')
print(f"Brace balance: {{ = {open_braces}, }} = {close_braces}")

open_quotes = mermaid.count('"')
print(f"Double quotes: {open_quotes} (should be even)")

