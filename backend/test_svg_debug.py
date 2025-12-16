from diagram_image_generator import TerraformParser, AdvancedDiagramGenerator

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
    
    print("===== SVG OUTPUT START =====")
    print(svg)
    print("===== SVG OUTPUT END =====")
    print(f"\nTotal length: {len(svg)} characters")
    
    # Check for common issues
    print("\n=== VALIDATION ===")
    print(f"Starts with '<svg': {svg.strip().startswith('<svg')}")
    print(f"Ends with '</svg>': {svg.strip().endswith('</svg>')}")
    print(f"Contains unescaped '<': {'<' in svg.replace('<svg', '').replace('<text', '').replace('<rect', '').replace('<style', '').replace('</svg>', '').replace('</text>', '').replace('</rect>', '').replace('</style>', '')}")
    print(f"Contains unescaped '>': {'>' in svg.replace('</svg>', '').replace('</text>', '').replace('</rect>', '').replace('</style>', '').replace('width=\"800\">', '').replace('height=\"600\">', '')}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
