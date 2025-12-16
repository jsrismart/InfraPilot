#!/usr/bin/env python3
from diagram_generator import DiagramGenerator, TerraformParser

tf_code = 'resource "aws_vpc" "main" { cidr_block = "10.0.0.0/16" }'

try:
    p = TerraformParser(tf_code)
    g = DiagramGenerator(p)
    result = g.generate_lucidchart_diagram()
    print("Success!")
    print(result)
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
