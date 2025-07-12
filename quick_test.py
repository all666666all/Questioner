"""
Quick test to verify Python is working
"""
import sys
print(f"✅ Python {sys.version} is working!")
print(f"✅ Python executable: {sys.executable}")

# Test if we can import basic modules
try:
    import json
    print("✅ JSON module available")
except ImportError:
    print("❌ JSON module not available")

try:
    import typing
    print("✅ Typing module available")
except ImportError:
    print("❌ Typing module not available")

print("\n🎯 Next steps:")
print("1. Install dependencies: python -m pip install -r requirements.txt")
print("2. Set up .env file with your OpenAI API key")
print("3. Run the demo: python demo.py")
print("4. Run the full app: python app.py")
