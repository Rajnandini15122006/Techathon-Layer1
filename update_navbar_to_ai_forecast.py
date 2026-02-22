"""
Update all navbars to replace "Dashboard" with "AI Forecast"
This highlights the time-series forecasting feature
"""
import os
import glob

def update_navbar(file_path):
    """Update navbar in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace Dashboard link with AI Forecast link
        # Keep index.html but change the text
        content = content.replace(
            '<a href="/static/index.html" class="nav-btn">Dashboard</a>',
            '<a href="/static/forecast_dashboard.html" class="nav-btn">AI Forecast</a>'
        )
        
        # Update active state for index.html
        content = content.replace(
            '<a href="/static/index.html" class="nav-btn active">Dashboard</a>',
            '<a href="/static/forecast_dashboard.html" class="nav-btn active">AI Forecast</a>'
        )
        
        # Also update any remaining "Dashboard" references in nav
        # But be careful not to replace page titles
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    print("="*60)
    print("UPDATING NAVBAR: Dashboard → AI Forecast")
    print("="*60)
    
    # Get all HTML files
    html_files = glob.glob('app/static/*.html')
    
    updated = 0
    for file_path in html_files:
        filename = os.path.basename(file_path)
        print(f"\nUpdating {filename}...")
        
        if update_navbar(file_path):
            print(f"  ✓ {filename} updated")
            updated += 1
        else:
            print(f"  ✗ {filename} failed")
    
    print("\n" + "="*60)
    print(f"✓ Updated {updated}/{len(html_files)} files")
    print("="*60)
    print("\nChanges made:")
    print("  • 'Dashboard' → 'AI Forecast' in navbar")
    print("  • Links now point to forecast_dashboard.html")
    print("  • Highlights time-series forecasting feature")
    print("\nResult:")
    print("  Judges will see 'AI Forecast' as first nav item")
    print("  Showcases your ML/AI capabilities prominently")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
