#!/usr/bin/env python3
"""Debug res_type_lower value"""

res_type = 'azurerm_windows_virtual_machine'
res_type_lower = res_type.lower().replace('azurerm_', '')
print(f"res_type: {res_type}")
print(f"res_type_lower: {res_type_lower}")
print(f"Check: 'virtual_machine' in res_type_lower = {'virtual_machine' in res_type_lower}")
print(f"Check: res_type_lower == 'windows_virtual_machine' = {res_type_lower == 'windows_virtual_machine'}")
