"""
Setup script for the Adaptive Learning System
"""
import os
import sys
import subprocess

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Set up environment file"""
    print("\n🔧 Setting up environment...")
    
    if os.path.exists(".env"):
        print("✅ .env file already exists")
        return True
    
    if os.path.exists(".env.example"):
        # Copy example file
        with open(".env.example", "r") as src:
            content = src.read()
        
        with open(".env", "w") as dst:
            dst.write(content)
        
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env and add your OpenAI API key")
        return True
    else:
        print("❌ .env.example file not found")
        return False

def test_imports():
    """Test that all modules can be imported"""
    print("\n🧪 Testing imports...")
    try:
        import gradio
        print("✅ Gradio imported")
        
        import openai
        print("✅ OpenAI imported")
        
        from config import Config
        print("✅ Config imported")
        
        from models import LearningSession
        print("✅ Models imported")
        
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Main setup function"""
    print("🎓 Adaptive Learning System Setup")
    print("=" * 40)
    
    success = True
    
    # Check Python version
    success &= check_python_version()
    
    # Install dependencies
    if success:
        success &= install_dependencies()
    
    # Setup environment
    if success:
        success &= setup_environment()
    
    # Test imports
    if success:
        success &= test_imports()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Edit .env file and add your OpenAI API key")
        print("2. Run the demo: python demo.py")
        print("3. Start the application: python app.py")
        print("4. Open http://localhost:7860 in your browser")
    else:
        print("❌ Setup failed. Please check the errors above.")
        print("\n🔧 Manual setup:")
        print("1. Ensure Python 3.8+ is installed")
        print("2. Run: pip install -r requirements.txt")
        print("3. Copy .env.example to .env")
        print("4. Add your OpenAI API key to .env")

if __name__ == "__main__":
    main()
