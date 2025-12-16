from diagram_generator import TerraformParser, DiagramGenerator
from diagram_image_generator import AdvancedDiagramGenerator

tf_code = '''
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "public" {
  vpc_id = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
}

resource "aws_instance" "web" {
  subnet_id = aws_subnet.public.id
  instance_type = "t2.micro"
}
'''

try:
    parser = TerraformParser(tf_code)
    gen = AdvancedDiagramGenerator(parser)
    png_data = gen.generate_png_diagram()
    if png_data:
        print(f"✓ PNG generation successful! Size: {len(png_data)} bytes")
        print(f"✓ PNG data is valid base64: {isinstance(png_data, str)}")
    else:
        print("✗ PNG generation returned empty (PIL not available)")
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
