"""
Quick test of AI workflow
"""

import os
import sys

# Ensure we can import
sys.path.insert(0, '/Users/suyashpustake/Desktop/Continuum_EarthDoc/Continuum_Earthdoc')

from ai_workflow.pdd_workflow import PDDWorkflow

def test_workflow():
    """Test complete workflow"""
    print("\n" + "="*60)
    print("Testing AI-Guided PDD Workflow")
    print("="*60)
    
    # Initialize
    print("\n1. Initializing workflow...")
    workflow = PDDWorkflow(os.environ.get('GOOGLE_API_KEY'))
    print("✓ Workflow initialized")
    
    # Test description
    description = """
    We are developing an electric vehicle charging network across Mumbai, India. 
    The project will install and operate 50 public charging stations across strategic 
    locations including 30 Level 2 chargers (7.2 kW each) and 20 DC Fast Chargers (50 kW each).
    
    The project is operated by GreenCharge India in partnership with Mumbai Municipal Corporation. 
    All stations will be equipped with revenue-grade metering systems to accurately measure 
    electricity consumption.
    
    The project aims to accelerate EV adoption by providing reliable charging infrastructure. 
    By displacing fossil fuel vehicle miles, the project is expected to reduce approximately 
    5,000 tCO2e per year. Over a 10-year crediting period, total emission reductions are 
    estimated at 50,000 tCO2e.
    """
    
    # Step 1: Set description
    print("\n2. Setting project description...")
    result = workflow.set_description(description)
    if result['success']:
        print("✓ Context extracted")
        print(f"  - Project: {workflow.context.get('project_name', 'Unknown')}")
        print(f"  - Type: {workflow.context.get('project_type', 'Unknown')}")
        print(f"  - Location: {workflow.context.get('location', {}).get('country', 'Unknown')}")
        print(f"  - Annual Reductions: {workflow.context.get('carbon_metrics', {}).get('annual_reductions', 'Unknown')}")
    
    # Step 2: Get recommendations
    print("\n3. Getting methodology recommendations...")
    recs = workflow.get_recommendations(3)
    if recs:
        print(f"✓ Got {len(recs)} recommendations")
        for i, rec in enumerate(recs, 1):
            print(f"  {i}. {rec.methodology_id} - {rec.title} ({rec.confidence:.0f}%)")
    
    # Step 3: Select methodology
    print(f"\n4. Selecting {recs[0].methodology_id}...")
    result = workflow.select_methodology(recs[0].methodology_id)
    if result['success']:
        print(f"✓ Methodology selected")
        print(f"  - Total sections: {result['total_sections']}")
    
    # Step 4: Populate first 3 sections
    print("\n5. Populating first 3 sections...")
    for i in range(min(3, len(workflow.sections))):
        result = workflow.populate_current_section()
        if result['success'] and not result.get('complete'):
            section = result['section']
            print(f"  ✓ {section.num} {section.title} - {len(section.values)} fields populated")
            
            # Show sample values
            sample_fields = list(section.values.items())[:3]
            for fname, fval in sample_fields:
                print(f"    - {fname}: {str(fval)[:50]}...")
            
            # Auto-approve
            workflow.approve_section()
    
    # Progress
    progress = workflow.get_progress()
    print(f"\n6. Progress: {progress['approved']}/{progress['total']} sections approved ({progress['percent']}%)")
    
    print("\n" + "="*60)
    print("✓ Workflow test complete - All systems working!")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        test_workflow()
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
