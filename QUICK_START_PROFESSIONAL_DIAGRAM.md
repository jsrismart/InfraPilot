# 🚀 Quick Start - Professional Architecture Diagram

## In 30 Seconds 

### 1️⃣ Open the App
Visit: **http://localhost:3001**

### 2️⃣ Paste Terraform Code
```hcl
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_lb" "main" {
  name = "app-alb"
  load_balancer_type = "application"
}

resource "aws_instance" "server" {
  ami = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"
}

resource "aws_db_instance" "db" {
  engine = "mysql"
  instance_class = "db.t3.micro"
}

resource "aws_s3_bucket" "data" {
  bucket = "app-data"
}
```

### 3️⃣ Click "Lucidchart" Button
The new button now shows your **professional architecture diagram** instead of flowchart code!

---

## What You'll See 👀

```
┌────────────────────────────────────────────────────────┐
│ AWS Infrastructure Architecture                         │
├────────────────────────────────────────────────────────┤
│                                                         │
│ ┌─────────────────────────────────────────────────┐   │
│ │ 🌍 INTERNET TIER                                │   │
│ │ [API Gateway] [CloudFront]                      │   │
│ └─────────────────────────────────────────────────┘   │
│           ↓                                             │
│ ┌─────────────────────────────────────────────────┐   │
│ │ ⚖️  WEB TIER                                    │   │
│ │ [ALB - app-alb]                                │   │
│ └─────────────────────────────────────────────────┘   │
│           ↓                                             │
│ ┌─────────────────────────────────────────────────┐   │
│ │ 🖥️  COMPUTE TIER                              │   │
│ │ [EC2 - server]  [Lambda]                      │   │
│ └─────────────────────────────────────────────────┘   │
│           ↓                                             │
│ ┌─────────────────────────────────────────────────┐   │
│ │ 🗄️  DATABASE TIER                              │   │
│ │ [RDS - db]   [DynamoDB]                        │   │
│ └─────────────────────────────────────────────────┘   │
│           ↓                                             │
│ ┌─────────────────────────────────────────────────┐   │
│ │ 📦 STORAGE TIER                                │   │
│ │ [S3 - data]   [EBS]   [EFS]                    │   │
│ └─────────────────────────────────────────────────┘   │
│           ↓                                             │
│ ┌─────────────────────────────────────────────────┐   │
│ │ 🌐 NETWORK TIER                                │   │
│ │ [VPC] [Subnets] [Security Groups] [NAT]       │   │
│ └─────────────────────────────────────────────────┘   │
│                                                         │
└────────────────────────────────────────────────────────┘
```

---

## The 6 Tiers Explained 📚

| Tier | Color | What Goes Here | Examples |
|------|-------|---|---|
| 🌍 **Internet** | Orange | Public entry points | CDN, API Gateway, Internet Gateway |
| ⚖️ **Web** | Blue | Traffic distribution | Load Balancers (ALB, NLB) |
| 🖥️ **Compute** | Green | Processing | EC2, Lambda, ECS, EKS |
| 🗄️ **Database** | Purple | Data storage | RDS, DynamoDB, CosmosDB |
| 📦 **Storage** | Red | Object/Block storage | S3, EBS, EFS |
| 🌐 **Network** | Cyan | Infrastructure foundation | VPC, Subnets, Security Groups |

---

## Available Buttons 🎛️

| Button | Output | Use Case |
|--------|--------|----------|
| **ASCII** | Text diagram | Terminal viewing |
| **Mermaid** | Diagram code | GitHub, GitLab rendering |
| **Lucidchart** | **Professional SVG** ⭐ | Architecture documentation |
| **JSON** | Structured data | Custom applications |
| **SVG** | Vector diagram | Web display |
| **PNG** | Image | Email sharing |
| **HTML** | Interactive | Detailed exploration |

---

## Real Examples 💡

### Example 1: Microservices Architecture
```hcl
# API Gateway for routing
resource "aws_api_gateway_rest_api" "main" { name = "api" }

# Multiple compute services
resource "aws_lambda_function" "users" { ... }
resource "aws_lambda_function" "orders" { ... }
resource "aws_lambda_function" "payments" { ... }

# Databases for each service
resource "aws_dynamodb_table" "users_table" { ... }
resource "aws_dynamodb_table" "orders_table" { ... }

# Shared storage
resource "aws_s3_bucket" "documents" { ... }

# VPC with security
resource "aws_vpc" "main" { ... }
resource "aws_security_group" "api" { ... }
```

**Result**: Professional diagram showing microservices organization!

### Example 2: Web Application
```hcl
# CDN for global delivery
resource "aws_cloudfront_distribution" "website" { ... }

# Load balancer for traffic
resource "aws_lb" "web" { load_balancer_type = "application" }

# Application servers
resource "aws_instance" "server_1" { ... }
resource "aws_instance" "server_2" { ... }

# Database
resource "aws_db_instance" "db" { engine = "mysql" }

# Static files
resource "aws_s3_bucket" "assets" { ... }

# Infrastructure
resource "aws_vpc" "main" { cidr_block = "10.0.0.0/16" }
```

**Result**: Clean web application architecture diagram!

---

## Keyboard Shortcuts ⌨️

- **Paste code**: `Ctrl+V` in textarea
- **View diagrams**: Click any format button
- **Copy SVG**: Right-click diagram → Copy
- **Download**: Use browser download (Firefox/Chrome)

---

## Pro Tips 💪

### Tip 1: Organization Matters
Resources with consistent naming are easier to understand:
```hcl
❌ Bad:    resource "aws_instance" "a" { }
✅ Good:   resource "aws_instance" "web_server_1" { }
```

### Tip 2: Use Proper Types
The more accurate your resource types, the better categorization:
```hcl
❌ Not detected:    resource "aws_???_instance" { }
✅ Detected:        resource "aws_db_instance" { }
                    resource "aws_instance" { }
```

### Tip 3: Complete Terraform is Best
While the diagram works with partial code, complete infrastructure shows full picture:
```hcl
✅ Include: vpc, subnets, security_groups, route tables
✅ Include: load_balancers, compute, databases, storage
✅ Include: CDN, API Gateway, IAM roles
```

### Tip 4: Export for Documentation
1. Click "Lucidchart"
2. Right-click SVG → "Save As"
3. Save as `architecture.svg`
4. Insert into docs/presentations

---

## Common Questions ❓

**Q: Can I import this into other tools?**
A: Yes! The SVG can be opened in:
- Lucidchart (drag & drop)
- Figma (paste SVG)
- Any vector editor
- Web browsers

**Q: Is my data private?**
A: Yes! Everything runs locally on your machine.
- No data sent to external servers
- Backend runs on localhost:8001
- Frontend runs on localhost:3001

**Q: Can I modify the diagram?**
A: Yes! Export as SVG and edit in any vector editor:
- Inkscape (free)
- Adobe Illustrator
- Figma
- Online editors like SVG-Edit

**Q: What if some resources don't show?**
A: Check the resource type name. Ensure you're using valid Terraform resource types like:
- `aws_instance`, `aws_lb`, `aws_db_instance`
- Not custom/experimental types

---

## 🎓 Next Steps

1. **Generate Your First Diagram**
   - Visit http://localhost:3001
   - Paste your Terraform
   - Click Lucidchart

2. **Share with Team**
   - Export the SVG
   - Send to teammates
   - Use in documentation

3. **Integrate into Workflow**
   - Use in code reviews
   - Include in architecture docs
   - Automate diagram generation

4. **Explore Other Formats**
   - Try ASCII for terminal
   - Try PNG for emails
   - Try HTML for interactive exploration

---

## 🆘 Troubleshooting

**Diagram is empty?**
→ Check that your Terraform code has valid resource types

**Lucidchart shows old flowchart?**
→ Refresh the page (Ctrl+R) and try again

**SVG looks pixelated?**
→ That's normal for SVG! Scale it up - it's vector-based

**Diagram is very large?**
→ Right-click → "Save Image As..." to download

---

## 📞 Support

For issues or questions:
1. Check this Quick Start guide
2. Review example Terraform code
3. Check the main documentation files
4. Review test files for working examples

---

**Ready to generate your professional architecture diagram?**

👉 **Go to http://localhost:3001 now!**

---

*Professional Architecture Diagram Generator*
*Part of InfraPilot - Terraform Infrastructure Generator*
