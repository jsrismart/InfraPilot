import requests
import json

terraform_code = """
resource "azurerm_resource_group" "main" {
  name     = "rg-infrapilot"
  location = "East US"
}

resource "azurerm_virtual_network" "main" {
  name                = "vnet-main"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_subnet" "internal" {
  name                 = "subnet-internal"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.2.0/24"]
}
"""

print("Testing Export Endpoint...")
print("=" * 70)

response = requests.post(
    'http://localhost:8000/api/v1/diagram/lucidchart/export',
    json={
        'terraform_code': terraform_code,
        'lucidchart_doc_title': 'Architecture Diagram Export Test'
    },
    timeout=30
)

print(f'Status Code: {response.status_code}')
data = response.json()

print(f'Success: {data.get("success")}')
print(f'Message: {data.get("message")}')
print(f'Automated Import: {data.get("automated_import")}')
print(f'Document ID: {data.get("lucidchart_document_id")}')
print(f'Edit URL: {data.get("edit_url")}')

print(f'\nHas Mermaid Code: {bool(data.get("mermaid_code"))}')
if data.get('mermaid_code'):
    print(f'Mermaid Code Length: {len(data.get("mermaid_code"))}')
    print(f'Mermaid Code Preview:\n{data.get("mermaid_code")[:300]}...')

print(f'\nHas Import Instructions: {bool(data.get("import_instructions"))}')
if data.get('import_instructions'):
    print('Import Instructions Keys:', list(data.get('import_instructions').keys()))

print(f'\nPreview URL: {data.get("preview_url")}')

print('\n' + '=' * 70)
print('Full Response:')
print(json.dumps(data, indent=2))
