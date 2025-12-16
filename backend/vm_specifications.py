"""
Azure VM Specifications Database
Complete specifications for all supported VM sizes (vCPU, RAM, Disk, Network)
"""

VM_SPECIFICATIONS = {
    # A-Series (older generation)
    'Standard_A0': {'vCPU': 1, 'RAM_GB': 0.768, 'Disk_GB': 20, 'Network_Mbps': 100, 'Series': 'A', 'Use_Case': 'Dev/Test'},
    'Standard_A1': {'vCPU': 1, 'RAM_GB': 1.75, 'Disk_GB': 40, 'Network_Mbps': 100, 'Series': 'A', 'Use_Case': 'Dev/Test'},
    'Standard_A2': {'vCPU': 2, 'RAM_GB': 3.5, 'Disk_GB': 60, 'Network_Mbps': 100, 'Series': 'A', 'Use_Case': 'Small App'},
    'Standard_A3': {'vCPU': 4, 'RAM_GB': 7, 'Disk_GB': 120, 'Network_Mbps': 100, 'Series': 'A', 'Use_Case': 'Medium App'},
    'Standard_A4': {'vCPU': 8, 'RAM_GB': 14, 'Disk_GB': 240, 'Network_Mbps': 100, 'Series': 'A', 'Use_Case': 'Large App'},
    'Standard_A5': {'vCPU': 2, 'RAM_GB': 14, 'Disk_GB': 70, 'Network_Mbps': 100, 'Series': 'A', 'Use_Case': 'Memory Optimized'},
    'Standard_A6': {'vCPU': 4, 'RAM_GB': 28, 'Disk_GB': 140, 'Network_Mbps': 100, 'Series': 'A', 'Use_Case': 'Memory Optimized'},
    'Standard_A7': {'vCPU': 8, 'RAM_GB': 56, 'Disk_GB': 280, 'Network_Mbps': 100, 'Series': 'A', 'Use_Case': 'Large Memory'},
    'Standard_A8': {'vCPU': 8, 'RAM_GB': 56, 'Disk_GB': 382, 'Network_Mbps': 1000, 'Series': 'A', 'Use_Case': 'HPC'},
    'Standard_A9': {'vCPU': 16, 'RAM_GB': 112, 'Disk_GB': 382, 'Network_Mbps': 1000, 'Series': 'A', 'Use_Case': 'HPC'},
    
    # B-Series (Burstable)
    'Standard_B1s': {'vCPU': 1, 'RAM_GB': 1, 'Disk_GB': 30, 'Network_Mbps': 100, 'Series': 'B', 'Use_Case': 'Dev/Test'},
    'Standard_B1ms': {'vCPU': 1, 'RAM_GB': 2, 'Disk_GB': 30, 'Network_Mbps': 100, 'Series': 'B', 'Use_Case': 'Dev/Test'},
    'Standard_B2s': {'vCPU': 2, 'RAM_GB': 4, 'Disk_GB': 60, 'Network_Mbps': 100, 'Series': 'B', 'Use_Case': 'Small App'},
    'Standard_B2ms': {'vCPU': 2, 'RAM_GB': 8, 'Disk_GB': 60, 'Network_Mbps': 100, 'Series': 'B', 'Use_Case': 'Dev/Web'},
    'Standard_B4ms': {'vCPU': 4, 'RAM_GB': 16, 'Disk_GB': 120, 'Network_Mbps': 100, 'Series': 'B', 'Use_Case': 'Medium App'},
    
    # C-Series v3 (Compute Optimized)
    'Standard_C2s_v3': {'vCPU': 2, 'RAM_GB': 4, 'Disk_GB': 50, 'Network_Mbps': 1000, 'Series': 'C', 'Use_Case': 'Compute Optimized'},
    'Standard_C4s_v3': {'vCPU': 4, 'RAM_GB': 8, 'Disk_GB': 100, 'Network_Mbps': 2000, 'Series': 'C', 'Use_Case': 'Compute Optimized'},
    'Standard_C8s_v3': {'vCPU': 8, 'RAM_GB': 16, 'Disk_GB': 200, 'Network_Mbps': 4000, 'Series': 'C', 'Use_Case': 'Compute Optimized'},
    
    # D-Series v3 (General Purpose)
    'Standard_D2s_v3': {'vCPU': 2, 'RAM_GB': 8, 'Disk_GB': 56, 'Network_Mbps': 1000, 'Series': 'D', 'Use_Case': 'General Purpose'},
    'Standard_D4s_v3': {'vCPU': 4, 'RAM_GB': 16, 'Disk_GB': 112, 'Network_Mbps': 2000, 'Series': 'D', 'Use_Case': 'General Purpose'},
    'Standard_D8s_v3': {'vCPU': 8, 'RAM_GB': 32, 'Disk_GB': 224, 'Network_Mbps': 4000, 'Series': 'D', 'Use_Case': 'General Purpose'},
    'Standard_D16s_v3': {'vCPU': 16, 'RAM_GB': 64, 'Disk_GB': 448, 'Network_Mbps': 8000, 'Series': 'D', 'Use_Case': 'High Performance'},
    'Standard_D32s_v3': {'vCPU': 32, 'RAM_GB': 128, 'Disk_GB': 896, 'Network_Mbps': 16000, 'Series': 'D', 'Use_Case': 'Enterprise'},
    
    # D-Series v4 (General Purpose - Latest)
    'Standard_D2s_v4': {'vCPU': 2, 'RAM_GB': 8, 'Disk_GB': 60, 'Network_Mbps': 1000, 'Series': 'D', 'Use_Case': 'General Purpose'},
    'Standard_D4s_v4': {'vCPU': 4, 'RAM_GB': 16, 'Disk_GB': 120, 'Network_Mbps': 2000, 'Series': 'D', 'Use_Case': 'General Purpose'},
    'Standard_D8s_v4': {'vCPU': 8, 'RAM_GB': 32, 'Disk_GB': 240, 'Network_Mbps': 4000, 'Series': 'D', 'Use_Case': 'General Purpose'},
    'Standard_D16s_v4': {'vCPU': 16, 'RAM_GB': 64, 'Disk_GB': 480, 'Network_Mbps': 8000, 'Series': 'D', 'Use_Case': 'High Performance'},
    'Standard_D32s_v4': {'vCPU': 32, 'RAM_GB': 128, 'Disk_GB': 960, 'Network_Mbps': 16000, 'Series': 'D', 'Use_Case': 'Enterprise'},
    'Standard_D32a_v4': {'vCPU': 32, 'RAM_GB': 128, 'Disk_GB': 960, 'Network_Mbps': 16000, 'Series': 'D', 'Use_Case': 'Enterprise'},
    
    # E-Series v3 (Memory Optimized)
    'Standard_E2s_v3': {'vCPU': 2, 'RAM_GB': 16, 'Disk_GB': 32, 'Network_Mbps': 1000, 'Series': 'E', 'Use_Case': 'Memory Optimized'},
    'Standard_E4s_v3': {'vCPU': 4, 'RAM_GB': 32, 'Disk_GB': 64, 'Network_Mbps': 2000, 'Series': 'E', 'Use_Case': 'Memory Optimized'},
    'Standard_E8s_v3': {'vCPU': 8, 'RAM_GB': 64, 'Disk_GB': 128, 'Network_Mbps': 4000, 'Series': 'E', 'Use_Case': 'Memory Optimized'},
    'Standard_E16s_v3': {'vCPU': 16, 'RAM_GB': 128, 'Disk_GB': 256, 'Network_Mbps': 8000, 'Series': 'E', 'Use_Case': 'Large Memory'},
    'Standard_E32s_v3': {'vCPU': 32, 'RAM_GB': 256, 'Disk_GB': 512, 'Network_Mbps': 16000, 'Series': 'E', 'Use_Case': 'Enterprise Memory'},
    
    # F-Series (Compute Optimized)
    'Standard_F1s': {'vCPU': 1, 'RAM_GB': 2, 'Disk_GB': 16, 'Network_Mbps': 100, 'Series': 'F', 'Use_Case': 'Compute Optimized'},
    'Standard_F2s': {'vCPU': 2, 'RAM_GB': 4, 'Disk_GB': 32, 'Network_Mbps': 100, 'Series': 'F', 'Use_Case': 'Compute Optimized'},
    'Standard_F4s': {'vCPU': 4, 'RAM_GB': 8, 'Disk_GB': 64, 'Network_Mbps': 100, 'Series': 'F', 'Use_Case': 'Compute Optimized'},
    'Standard_F8s': {'vCPU': 8, 'RAM_GB': 16, 'Disk_GB': 128, 'Network_Mbps': 100, 'Series': 'F', 'Use_Case': 'Compute Optimized'},
    'Standard_F16s': {'vCPU': 16, 'RAM_GB': 32, 'Disk_GB': 256, 'Network_Mbps': 100, 'Series': 'F', 'Use_Case': 'High Compute'},
    
    # G-Series (Memory Optimized, older)
    'Standard_G1': {'vCPU': 2, 'RAM_GB': 28, 'Disk_GB': 384, 'Network_Mbps': 1000, 'Series': 'G', 'Use_Case': 'Large Memory'},
    'Standard_G2': {'vCPU': 4, 'RAM_GB': 56, 'Disk_GB': 768, 'Network_Mbps': 2000, 'Series': 'G', 'Use_Case': 'Large Memory'},
    'Standard_G3': {'vCPU': 8, 'RAM_GB': 112, 'Disk_GB': 1536, 'Network_Mbps': 4000, 'Series': 'G', 'Use_Case': 'Enterprise'},
    'Standard_G4': {'vCPU': 16, 'RAM_GB': 224, 'Disk_GB': 3072, 'Network_Mbps': 8000, 'Series': 'G', 'Use_Case': 'Enterprise'},
}

def get_vm_specifications(vm_size: str) -> dict:
    """
    Get detailed specifications for a VM size
    
    Args:
        vm_size: VM size name (e.g., 'Standard_D2s_v3')
        
    Returns:
        Dictionary with vCPU, RAM, Disk, Network, Series, Use_Case
    """
    if vm_size in VM_SPECIFICATIONS:
        return VM_SPECIFICATIONS[vm_size].copy()
    return {
        'vCPU': 0,
        'RAM_GB': 0,
        'Disk_GB': 0,
        'Network_Mbps': 0,
        'Series': 'Unknown',
        'Use_Case': 'Unknown'
    }

def get_all_vm_sizes(series: str = None) -> list:
    """Get list of all VM sizes, optionally filtered by series"""
    if series:
        return [size for size, spec in VM_SPECIFICATIONS.items() if spec['Series'] == series.upper()]
    return list(VM_SPECIFICATIONS.keys())

def get_series_info(series: str) -> dict:
    """Get all VMs in a specific series"""
    series = series.upper()
    series_vms = {size: spec for size, spec in VM_SPECIFICATIONS.items() if spec['Series'] == series}
    return series_vms

if __name__ == '__main__':
    # Test functionality
    print("✓ VM Specifications Database Loaded")
    print(f"✓ Total VM Sizes: {len(VM_SPECIFICATIONS)}")
    
    # Show sample
    print("\n[Sample] Standard_D2s_v3:")
    print(f"  vCPU: {VM_SPECIFICATIONS['Standard_D2s_v3']['vCPU']}")
    print(f"  RAM: {VM_SPECIFICATIONS['Standard_D2s_v3']['RAM_GB']}GB")
    print(f"  Disk: {VM_SPECIFICATIONS['Standard_D2s_v3']['Disk_GB']}GB")
    print(f"  Use Case: {VM_SPECIFICATIONS['Standard_D2s_v3']['Use_Case']}")
    
    # Series list
    print("\n[Series Summary]")
    for series in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
        count = len(get_all_vm_sizes(series))
        print(f"  {series}-Series: {count} VMs")
