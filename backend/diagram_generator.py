"""
InfraPilot Terraform to Diagram Converter (fixed full script)
Converts generated Terraform IaC into visual infrastructure diagrams
- Robust resource block extraction (brace counting)
- Robust property parsing (scanner for strings, lists, maps, references)
- Provider detection improvements
- Relationship extraction by scanning references and depends_on
- ASCII / Mermaid / JSON / SVG outputs
- Azure resource validation against pricing API
"""

import json
import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Configure logging
logger = logging.getLogger(__name__)

# Try to import validator
try:
    from azure_resource_validator import validator
    VALIDATOR_ENABLED = True
except ImportError:
    VALIDATOR_ENABLED = False
    logger.warning("Azure resource validator not available")


@dataclass
class TerraformResource:
    """Represents a Terraform resource"""
    type: str
    name: str
    properties: Dict[str, str]
    config: Dict = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}


class TerraformParser:
    """Parse Terraform files and extract resources"""

    PROVIDER_ICONS = {
        'aws': '☁️',
        'azure': '🔵',
        'gcp': '📊',
        'kubernetes': '☸️',
        'docker': '🐳',
    }

    RESOURCE_ICONS = {
        # AWS Compute
        'instance': '🖥️',
        'ec2': '🖥️',
        'lambda': '⚡',
        'ecs': '🐳',
        'eks': '☸️',
        'auto_scaling': '📈',
        'batch': '⚙️',
        
        # AWS Networking
        'vpc': '🌐',
        'subnet': '📡',
        'security_group': '🔒',
        'alb': '⚖️',
        'nlb': '⚖️',
        'load_balancer': '⚖️',
        'elb': '⚖️',
        'nat_gateway': '🚪',
        'route': '🛣️',
        'route_table': '🛣️',
        'internet_gateway': '🌍',
        'egress_only_gateway': '🌍',
        'vpn': '🔐',
        'vpn_gateway': '🔐',
        'customer_gateway': '🔐',
        'cloudfront': '📡',
        'api_gateway': '🔌',
        'endpoint': '🔗',
        
        # AWS Storage
        'rds': '🗄️',
        'rds_cluster': '🗄️',
        'dynamodb': '📊',
        's3': '🪣',
        'bucket': '🪣',
        'ebs': '💾',
        'efs': '📂',
        'elasticache': '⚡',
        'backup_vault': '🔐',
        
        # AWS Messaging & Monitoring
        'sqs': '📨',
        'sns': '📢',
        'kinesis': '🔄',
        'kinesis_stream': '🔄',
        'msk_cluster': '📦',
        'cloudwatch': '👁️',
        'cloudtrail': '📝',
        'sns_topic': '📢',
        
        # AWS Security & IAM
        'iam_role': '👤',
        'iam_user': '👤',
        'iam_policy': '📋',
        'acm': '🔐',
        'kms': '🔑',
        'secrets_manager': '🔒',
        'ssm_parameter': '⚙️',
        'waf': '🛡️',
        
        # Azure
        'virtual_machine': '🖥️',
        'app_service': '🌐',
        'app_service_plan': '📋',
        'sql_server': '🗄️',
        'sql_database': '🗄️',
        'storage_account': '💾',
        'virtual_network': '🌐',
        'network_interface': '📡',
        'network_security_group': '🔒',
        'public_ip': '🌍',
        'load_balancer': '⚖️',
        'api_management': '🔌',
        'container_registry': '📦',
        'container_instance': '🐳',
        'kubernetes_cluster': '☸️',
        'cosmosdb': '🔄',
        'resource_group': '📁',
        'data_factory': '📊',
        'key_vault': '🔐',
        'service_bus': '📨',
        
        # GCP
        'compute_instance': '🖥️',
        'compute_engine': '🖥️',
        'cloud_run': '🏃',
        'cloud_functions': '⚡',
        'cloud_sql': '🗄️',
        'datastore': '📊',
        'firestore': '📄',
        'storage_bucket': '🪣',
        'cloud_storage': '💾',
        'vpc_network': '🌐',
        'firewall': '🔒',
        'cloud_load_balancing': '⚖️',
        'cloud_cdn': '📡',
        'cloud_vpn': '🔐',
        'cloud_nat': '🚪',
        'kubernetes_engine': '☸️',
        'cloud_run_service': '🏃',
        'pub_sub': '📨',
        'bigtable': '📊',
        
        # Kubernetes
        'deployment': '📦',
        'service': '🔌',
        'pod': '📦',
        'namespace': '📁',
        'configmap': '⚙️',
        'secret': '🔐',
        'ingress': '🌐',
        'ingress_class': '🌐',
        'persistent_volume': '💾',
        'persistent_volume_claim': '💾',
        'storage_class': '💾',
        'statefulset': '📊',
        'daemonset': '🔄',
        'job': '⏰',
        'cronjob': '⏰',
        'role': '👤',
        'role_binding': '🔗',
        'cluster_role': '👤',
        'cluster_role_binding': '🔗',
        
        # Docker & Containers
        'docker': '🐳',
        'container': '📦',
        'image': '🖼️',
        'registry': '📚',
        
        # Default fallback
        'default': '⚙️',
    }

    def __init__(self, terraform_content: str):
        self.content = terraform_content
        self.resources: List[TerraformResource] = []
        self.parse()

    def parse(self):
        """Parse Terraform content and extract resources using brace counting"""
        # Look for "resource" tokens followed by "type" "name" { ...
        pattern = re.compile(r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{', re.IGNORECASE)
        for m in pattern.finditer(self.content):
            resource_type, resource_name = m.groups()
            start = m.end()
            # Walk forward counting braces
            brace_count = 1
            i = start
            while i < len(self.content) and brace_count > 0:
                ch = self.content[i]
                if ch == '{':
                    brace_count += 1
                elif ch == '}':
                    brace_count -= 1
                i += 1
            body = self.content[start:i-1].strip()
            properties = self._parse_properties(body)
            # Extract config for cost calculation
            config = self._extract_config(resource_type, properties)
            resource = TerraformResource(type=resource_type, name=resource_name, properties=properties, config=config)
            
            # Validate Azure resources if validator is available
            if VALIDATOR_ENABLED and 'azurerm' in resource_type.lower():
                is_valid, message, suggested = validator.validate_resource(resource_type, resource_name, properties)
                logger.info(f"[PARSER] Azure resource validation: {resource_type}.{resource_name} - {message}")
                if suggested:
                    logger.warning(f"[PARSER] Suggested correction for {resource_type}.{resource_name}: {suggested}")
            
            self.resources.append(resource)

    def _parse_properties(self, body: str) -> Dict[str, str]:
        """
        Extract properties from resource body more reliably using a scanner:
        - handles quoted strings
        - lists [ ... ]
        - maps { ... }
        - bare references like aws_vpc.main.id or aws_subnet.public.id
        - numeric and booleans
        """
        properties: Dict[str, str] = {}
        i = 0
        n = len(body)

        def skip_whitespace_and_comments():
            nonlocal i
            while i < n:
                if body[i].isspace():
                    i += 1
                    continue
                # line comments #
                if body[i] == '#':
                    # skip until end of line
                    while i < n and body[i] != '\n':
                        i += 1
                    continue
                # terraform // comments (rare but handle)
                if body.startswith("//", i):
                    i += 2
                    while i < n and body[i] != '\n':
                        i += 1
                    continue
                break

        def read_identifier():
            nonlocal i
            start = i
            while i < n and (body[i].isalnum() or body[i] in '_-'):
                i += 1
            return body[start:i].strip()

        def read_until_matching(end_char):
            nonlocal i
            start = i
            depth = 0
            while i < n:
                ch = body[i]
                if ch == end_char and depth == 0:
                    # return substring before this end_char
                    val = body[start:i].strip()
                    i += 1  # consume end_char
                    return val
                if ch == end_char and depth > 0:
                    # nested same char, reduce
                    depth -= 1
                elif ch == '"' and end_char != '"':
                    # skip quoted strings inside lists/maps
                    i += 1
                    while i < n and body[i] != '"':
                        if body[i] == '\\':
                            i += 2
                        else:
                            i += 1
                elif ch == "'" and end_char != "'":
                    i += 1
                    while i < n and body[i] != "'":
                        if body[i] == '\\':
                            i += 2
                        else:
                            i += 1
                elif ch == '[' and end_char == ']':
                    depth += 1
                    i += 1
                elif ch == '{' and end_char == '}':
                    depth += 1
                    i += 1
                else:
                    i += 1
            # fallback
            return body[start:i].strip()

        while i < n:
            skip_whitespace_and_comments()
            if i >= n:
                break
            # read key
            key = read_identifier()
            skip_whitespace_and_comments()
            # key could be on its own line or equal sign next
            if i < n and body[i] == '=':
                i += 1  # consume =
                skip_whitespace_and_comments()
                # determine type of value
                if i < n and body[i] in ('"', "'"):
                    quote_char = body[i]
                    i += 1
                    val_start = i
                    while i < n:
                        if body[i] == '\\':
                            i += 2
                            continue
                        if body[i] == quote_char:
                            val = body[val_start:i]
                            i += 1
                            break
                        i += 1
                    else:
                        val = body[val_start:i]
                    properties[key] = val
                    continue
                elif i < n and body[i] == '[':
                    # list — read until matching ]
                    i += 1  # consume [
                    val = read_until_matching(']')
                    properties[key] = '[' + val + ']'
                    continue
                elif i < n and body[i] == '{':
                    # map/object
                    i += 1
                    val = read_until_matching('}')
                    properties[key] = '{' + val + '}'
                    continue
                else:
                    # bare token until newline or comment
                    start_val = i
                    while i < n and body[i] not in '\n\r':
                        # stop at comment start
                        if body[i] == '#':
                            break
                        i += 1
                    val = body[start_val:i].strip().rstrip(',')
                    properties[key] = val
                    continue
            else:
                # Could be a nested block like ingress { ... } — skip its body
                skip_whitespace_and_comments()
                if i < n and body[i] == '{':
                    # skip nested block by counting braces
                    i += 1
                    depth = 1
                    while i < n and depth > 0:
                        if body[i] == '{':
                            depth += 1
                        elif body[i] == '}':
                            depth -= 1
                        i += 1
                else:
                    # unknown token — advance a bit
                    i += 1

        return properties

    def _extract_config(self, resource_type: str, properties: Dict[str, str]) -> Dict:
        """Extract config for cost calculation from resource properties"""
        config = {}
        
        # Region/Location
        if 'location' in properties:
            config['region'] = properties['location']
        elif 'region' in properties:
            config['region'] = properties['region']
        else:
            config['region'] = 'eastus'
        
        # OS type for VM
        if 'windows' in str(properties).lower():
            config['os_type'] = 'windows'
        elif 'linux' in str(properties).lower():
            config['os_type'] = 'linux'
        else:
            config['os_type'] = 'windows'  # default
        
        # SQL tier/SKU
        if 'sku_name' in properties:
            config['sku_name'] = properties['sku_name']
        
        # Storage size
        if 'size_gb' in properties:
            try:
                config['size_gb'] = int(properties['size_gb'])
            except:
                config['size_gb'] = 100
        
        return config

    def get_provider(self) -> str:
        """Extract provider from Terraform content with better matching"""
        providers = {
            "aws": r'provider\s+"aws"',
            "azure": r'provider\s+"azurerm"',
            "gcp": r'provider\s+"google"',
            "kubernetes": r'provider\s+"kubernetes"',
            "docker": r'provider\s+"docker"'
        }
        for p, pattern in providers.items():
            if re.search(pattern, self.content, re.IGNORECASE):
                return p
        # check required_providers block for quick hint
        rp = re.search(r'required_providers\s*\{([^}]*)\}', self.content, re.IGNORECASE | re.DOTALL)
        if rp:
            block = rp.group(1)
            if 'aws' in block:
                return 'aws'
            if 'google' in block or 'google-beta' in block:
                return 'gcp'
            if 'azurerm' in block:
                return 'azure'
        return 'unknown'


class DiagramGenerator:
    """Generate ASCII and Mermaid diagrams from Terraform resources"""

    def __init__(self, parser: TerraformParser):
        self.parser = parser
        self.provider = parser.get_provider()

    def get_resource_icon(self, resource_type: str) -> str:
        """Get icon for resource type with smart matching"""
        resource_lower = resource_type.lower()
        
        # Direct exact match
        if resource_lower in TerraformParser.RESOURCE_ICONS:
            return TerraformParser.RESOURCE_ICONS[resource_lower]
        
        # Extract resource name (aws_vpc -> vpc, azurerm_virtual_machine -> virtual_machine)
        if '_' in resource_lower:
            parts = resource_lower.split('_', 1)
            resource_name = parts[1] if len(parts) > 1 else resource_lower
            
            # Try matching the resource name part
            if resource_name in TerraformParser.RESOURCE_ICONS:
                return TerraformParser.RESOURCE_ICONS[resource_name]
            
            # Try substring matching for compound names (e.g., app_service -> app_service)
            for key, icon in TerraformParser.RESOURCE_ICONS.items():
                if key in resource_name or resource_name in key:
                    return icon
        
        # Default fallback
        return TerraformParser.RESOURCE_ICONS.get('default', '⚙️')

    def generate_ascii_diagram(self) -> str:
        """Generate ASCII art infrastructure diagram"""
        lines = []
        lines.append("=" * 70)
        lines.append(f"  🏗️  {self.provider.upper()} INFRASTRUCTURE DIAGRAM")
        lines.append("=" * 70)
        lines.append("")

        # Group resources by base type (e.g., aws_vpc -> aws)
        resources_by_provider_and_type = {}
        for resource in self.parser.resources:
            # base_type = after provider prefix (aws_vpc -> vpc)
            # keep full type for clarity
            base_type = resource.type
            resources_by_provider_and_type.setdefault(base_type, []).append(resource)

        for resource_type in sorted(resources_by_provider_and_type.keys()):
            icon = self.get_resource_icon(resource_type)
            lines.append(f"┌─ {icon} {resource_type}")
            for resource in resources_by_provider_and_type[resource_type]:
                lines.append(f"│  ├─ {resource.name}")
                # show up to 4 properties
                for key, value in list(resource.properties.items())[:4]:
                    lines.append(f"│  │  └─ {key}: {value}")
            lines.append("│")

        lines.append("=" * 70)
        return "\n".join(lines)

    def generate_mermaid_diagram(self) -> str:
        """Generate Mermaid diagram for visualization with automatic connections"""
        lines: List[str] = []
        lines.append("graph TB")
        lines.append('    subgraph "Infrastructure"')

        # Group by resource base type for subgraph grouping (use prefix before first underscore)
        resources_by_group = {}
        for resource in self.parser.resources:
            # group by provider/resource root (aws_vpc -> aws_vpc)
            # for readability, cluster by provider type prefix (aws, google, azurerm) + service
            provider_prefix = resource.type.split('_', 1)[0]
            resources_by_group.setdefault(provider_prefix, []).append(resource)

        node_id = 0
        node_map: Dict[str, str] = {}

        # produce nodes with icons
        for group, resources in resources_by_group.items():
            # create a sub-subgraph per provider prefix for readability
            lines.append(f'    subgraph {group}')
            for resource in resources:
                node_id += 1
                node_name = f"node{node_id}"
                display_name = f"{self.get_resource_icon(resource.type)} {resource.name}\\n({resource.type})"
                # Mermaid requires escaping quotes
                lines.append(f'      {node_name}["{display_name}"]')
                node_map[f"{resource.type}:{resource.name}"] = node_name
            lines.append("    end")

        # Add connections based on property references and depends_on
        lines.extend(self._generate_connections(node_map))

        lines.append("    end")  # Close Infrastructure subgraph
        lines.append("")  # newline
        return "\n".join(lines)

    def generate_lucidchart_diagram(self) -> str:
        """Generate professional infrastructure architecture diagram for Lucidchart"""
        lines: List[str] = []
        lines.append("graph TB")
        
        # Define tier structure for professional architecture
        tiers = {
            'Internet': {
                'icon': '🌐',
                'keywords': ['internet_gateway', 'cloudfront', 'api_gateway', 'cdn'],
                'color': '#FF9800'
            },
            'Web Tier': {
                'icon': '🔒',
                'keywords': ['alb', 'nlb', 'load_balancer', 'elb', 'application_gateway'],
                'color': '#2196F3'
            },
            'Application Tier': {
                'icon': '💻',
                'keywords': ['ec2', 'instance', 'lambda', 'ecs', 'eks', 'app_service', 'compute_instance', 'virtual_machine'],
                'color': '#4CAF50'
            },
            'Data Tier': {
                'icon': '🗄️',
                'keywords': ['rds', 'dynamodb', 'sql_server', 'cosmosdb', 'cloud_sql', 'sql_database', 'database'],
                'color': '#9C27B0'
            },
            'Storage': {
                'icon': '💾',
                'keywords': ['s3', 'bucket', 'storage_account', 'ebs', 'efs', 'cloud_storage'],
                'color': '#FF5722'
            },
            'Network': {
                'icon': '🔗',
                'keywords': ['vpc', 'virtual_network', 'subnet', 'network_interface'],
                'color': '#00BCD4'
            }
        }
        
        # Organize resources by tier
        tier_resources = {tier: [] for tier in tiers.keys()}
        uncategorized = []
        
        for resource in self.parser.resources:
            resource_lower = resource.type.lower()
            placed = False
            
            for tier, config in tiers.items():
                if any(kw in resource_lower for kw in config['keywords']):
                    tier_resources[tier].append(resource)
                    placed = True
                    break
            
            if not placed:
                uncategorized.append(resource)
        
        if uncategorized:
            tier_resources['Network'] = tier_resources.get('Network', []) + uncategorized
        
        node_id = 0
        node_map: Dict[str, str] = {}
        
        # Create professional tier-based architecture
        tier_order = ['Internet', 'Web Tier', 'Application Tier', 'Data Tier', 'Storage', 'Network']
        
        for tier_name in tier_order:
            resources = tier_resources.get(tier_name, [])
            if not resources:
                continue
            
            config = tiers.get(tier_name, {})
            icon = config.get('icon', '⚙️')
            
            # Create subgraph for tier
            lines.append(f'    subgraph tier_{tier_name.replace(" ", "_")}["{icon} {tier_name}"]')
            lines.append('        direction LR')
            
            # Group related resources within tier
            for resource in resources:
                node_id += 1
                node_name = f"n{node_id}"
                res_icon = self.get_resource_icon(resource.type)
                resource_type_clean = resource.type.replace("_", " ").title()
                
                # Create professional node label
                display_name = f"{res_icon} {resource.name}"
                
                lines.append(f'        {node_name}["{display_name}<br/><small>{resource_type_clean}</small>"]')
                node_map[f"{resource.type}:{resource.name}"] = node_name
            
            lines.append('    end')
            lines.append('')
        
        # Add connections between tiers
        connections = self._generate_connections(node_map)
        
        # Add connection lines
        lines.append('    %% Connections')
        for conn in connections:
            if " --> " in conn:
                lines.append(f'    {conn}')
        
        return "\n".join(lines)

    def _generate_connections(self, node_map: Dict[str, str]) -> List[str]:
        """Generate connections between resources by scanning properties for references"""
        connections: List[str] = []

        # helper to find references inside a string value
        # matches patterns like: aws_vpc.main.id or aws_subnet["public"].id or module.foo.aws_vpc.main.id
        ref_patterns = [
            re.compile(r'([a-zA-Z0-9_]+)\.([a-zA-Z0-9_-]+)\.([a-zA-Z0-9_]+)'),  # aws_vpc.main.id
            re.compile(r'([a-zA-Z0-9_]+)\["([^"]+)"\]\.([a-zA-Z0-9_]+)'),       # aws_subnet["public"].id
            re.compile(r'([a-zA-Z0-9_]+)\[\'([^\']+)\'\]\.([a-zA-Z0-9_]+)')     # aws_subnet['public'].id
        ]

        def find_refs(val: str) -> List[Tuple[str, str]]:
            found: List[Tuple[str, str]] = []
            if not isinstance(val, str):
                return found
            for pat in ref_patterns:
                for m in pat.finditer(val):
                    # resource type and name
                    res_type = m.group(1)
                    res_name = m.group(2)
                    # we map to keys like "aws_vpc:main"
                    found.append((res_type, res_name))
            # also find simple "resource_type.resource_name" without trailing .id
            compact = re.findall(r'([a-zA-Z0-9_]+)\.([a-zA-Z0-9_-]+)\b', val)
            for rt, rn in compact:
                # avoid double counting things already captured with .id since above already captured
                if (rt, rn) not in found:
                    found.append((rt, rn))
            return found

        # iterate resources and properties to discover references
        for src_resource in self.parser.resources:
            src_key = f"{src_resource.type}:{src_resource.name}"
            src_node = node_map.get(src_key)
            if not src_node:
                continue

            # first handle explicit depends_on property if present (list)
            depends = src_resource.properties.get('depends_on')
            if depends:
                # naive parsing: find entries inside brackets or list tokens
                # e.g. [aws_vpc.main, aws_subnet.public] or aws_vpc.main
                for m in re.finditer(r'([a-zA-Z0-9_]+)\.([a-zA-Z0-9_-]+)', depends):
                    dst_type, dst_name = m.groups()
                    dst_node = node_map.get(f"{dst_type}:{dst_name}")
                    if dst_node:
                        connections.append(f"    {src_node} --> {dst_node}")

            # scan all property values for references
            for key, val in src_resource.properties.items():
                refs = find_refs(val)
                for rt, rn in refs:
                    dst_node = node_map.get(f"{rt}:{rn}")
                    if dst_node and dst_node != src_node:
                        # create connection arrow
                        connections.append(f"    {src_node} --> {dst_node}")

        # deduplicate while preserving order
        seen = set()
        unique_connections = []
        for c in connections:
            if c not in seen:
                seen.add(c)
                unique_connections.append(c)

        return unique_connections

    def generate_json_diagram(self) -> Dict:
        """Generate JSON representation for interactive diagrams"""
        return {
            "provider": self.provider,
            "resources": [
                {
                    "id": f"{r.type}:{r.name}",
                    "type": r.type,
                    "name": r.name,
                    "icon": self.get_resource_icon(r.type),
                    "properties": r.properties
                }
                for r in self.parser.resources
            ],
            "total_resources": len(self.parser.resources)
        }

    def generate_svg_diagram(self) -> str:
        """Generate a simple grid SVG diagram with resource boxes"""
        resources = self.parser.resources
        if not resources:
            return "<svg><!-- no resources --></svg>"

        cols = max(1, min(4, (len(resources) + 1) // 2))  # 1-4 columns
        rows = (len(resources) + cols - 1) // cols

        width = cols * 240 + 40
        height = rows * 160 + 80

        svg = [
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
            "  <style>",
            "    .resource-box { fill: #4A90E2; stroke: #2E5C8A; stroke-width: 2; }",
            "    .resource-text { fill: white; font-family: Arial, sans-serif; font-size: 12px; text-anchor: middle; }",
            "    .title { fill: #2E5C8A; font-family: Arial, sans-serif; font-size: 16px; font-weight: bold; }",
            "    .connection { stroke: #7B8D9E; stroke-width: 1; fill: none; }",
            "  </style>",
            f'  <text x="20" y="24" class="title">{self.provider.upper()} Infrastructure</text>',
        ]

        for idx, resource in enumerate(resources):
            row = idx // cols
            col = idx % cols
            x = col * 240 + 20
            y = row * 160 + 40
            icon = self.get_resource_icon(resource.type)
            svg.append(f'  <rect x="{x}" y="{y}" width="220" height="110" class="resource-box" rx="6"/>')
            svg.append(f'  <text x="{x + 110}" y="{y + 28}" class="resource-text">{icon} {resource.type}</text>')
            svg.append(f'  <text x="{x + 110}" y="{y + 52}" class="resource-text">{resource.name}</text>')
            # show one or two properties
            prop_items = list(resource.properties.items())[:2]
            py = y + 78
            for key, val in prop_items:
                # shorten long val
                display_val = val
                if len(display_val) > 28:
                    display_val = display_val[:25] + "..."
                svg.append(f'  <text x="{x + 110}" y="{py}" class="resource-text" style="font-size: 10px;">{key}: {display_val}</text>')
                py += 12

        svg.append('</svg>')
        return "\n".join(svg)


def main():
    """Example usage with sample Terraform content"""
    terraform_example = """
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = true
  tags = {
    Name = "main-vpc"
  }
}

resource "aws_subnet" "public" {
  vpc_id = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
  availability_zone = "us-east-1a"
  tags = { Name = "public-subnet" }
}

resource "aws_security_group" "allow_http" {
  vpc_id = aws_vpc.main.id
  name = "allow_http"
  description = "Allow HTTP traffic"
  ingress {
    from_port = 80
    to_port = 80
    protocol = "tcp"
  }
}

resource "aws_db_instance" "db" {
  allocated_storage = 20
  engine = "postgres"
  instance_class = "db.t3.micro"
  vpc_security_group_ids = [aws_security_group.allow_http.id]
  depends_on = [aws_subnet.public]
}

resource "aws_instance" "web_server" {
  ami = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  subnet_id = aws_subnet.public.id
  security_groups = [aws_security_group.allow_http.id]
}
"""
    parser = TerraformParser(terraform_example)
    generator = DiagramGenerator(parser)

    print(generator.generate_ascii_diagram())
    print("\n\n")
    print("=== MERMAID DIAGRAM ===")
    print(generator.generate_mermaid_diagram())
    print("\n\n")
    print("=== JSON REPRESENTATION ===")
    print(json.dumps(generator.generate_json_diagram(), indent=2))
    print("\n\n")
    print("=== SVG OUTPUT (first 400 chars) ===")
    svg = generator.generate_svg_diagram()
    print(svg[:400] + ("\n... (truncated)" if len(svg) > 400 else ""))


if __name__ == "__main__":
    main()
