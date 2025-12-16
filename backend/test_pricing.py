"""Test the pricing calculator functionality"""

from pricing_calculator import CloudPricingCalculator, calculate_terraform_pricing
import json

# Test basic pricing calculation
calculator = CloudPricingCalculator()

# Add some test resources
calculator.add_resource('web-server', 'aws_instance', 'aws', 't2.micro')
calculator.add_resource('database', 'aws_db_instance', 'aws', 'db.t2.small')
calculator.add_resource('storage', 'aws_s3_bucket', 'aws', config={'size_gb': 500})

# Calculate costs
results = calculator.calculate_total_cost()

print("=" * 60)
print("PRICING CALCULATOR TEST")
print("=" * 60)

print("\nMONTHLY COSTS BY PROVIDER:")
for provider, cost in results['total_costs'].items():
    print(f"  {provider.upper()}: ${cost:.2f}")

print("\nCHEAPEST PROVIDER:")
print(f"  {results['comparison']['cheapest_provider'].upper()}")

print("\nDETAILED BREAKDOWN:")
for provider, resources in results['breakdown'].items():
    if resources:
        print(f"\n  {provider.upper()}:")
        for res in resources:
            print(f"    - {res['name']}: ${res['cost']:.2f} ({res['description']})")

print("\n" + "=" * 60)
print("All pricing calculations completed successfully!")
print("=" * 60)
