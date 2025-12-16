from diagram_image_generator import TerraformParser, AdvancedDiagramGenerator
import xml.etree.ElementTree as ET

tf_code = '''
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "main" {
  vpc_id = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
}

resource "aws_security_group" "main" {
  vpc_id = aws_vpc.main.id
}

resource "aws_instance" "web" {
  subnet_id = aws_subnet.main.id
  security_groups = [aws_security_group.main.id]
}

resource "aws_db_instance" "main" {
  allocated_storage = 20
}
'''

try:
    parser = TerraformParser(tf_code)
    gen = AdvancedDiagramGenerator(parser)
    svg = gen.generate_professional_architecture_diagram()
    
    print("===== SVG OUTPUT =====")
    print(svg[:300])
    print("...[middle]...")
    print(svg[-200:])
    print(f"\nTotal length: {len(svg)} characters")
    
    # Try to parse as XML
    print("\n=== XML VALIDATION ===")
    try:
        root = ET.fromstring(svg)
        print("✅ Valid XML - parsed successfully")
        print(f"Root tag: {root.tag}")
        text_elements = root.findall('.//text')
        print(f"Found {len(text_elements)} text elements")
        if text_elements:
            print(f"First text: {text_elements[0].text}")
    except ET.ParseError as e:
        print(f"❌ XML Parse Error: {e}")
        print(f"Error line: {e.lineno}, column: {e.offset}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
