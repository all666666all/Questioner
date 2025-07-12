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
    """Install required dependencies using uv or venv"""
    print("\n📦 Installing dependencies...")
    
    # First try uv sync
    try:
        subprocess.check_call(["uv", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ uv found, using uv sync...")
        subprocess.check_call(["uv", "sync"])
        print("✅ Dependencies installed successfully with uv")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  uv not found, creating virtual environment...")
        
        # Create virtual environment if it doesn't exist
        if not os.path.exists("venv"):
            try:
                subprocess.check_call([sys.executable, "-m", "venv", "venv"])
                print("✅ Virtual environment created")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to create virtual environment: {e}")
                return False
        
        # Install dependencies in virtual environment
        venv_pip = os.path.join("venv", "bin", "pip") if os.name != "nt" else os.path.join("venv", "Scripts", "pip.exe")
        try:
            subprocess.check_call([venv_pip, "install", "-r", "requirements.txt"])
            print("✅ Dependencies installed successfully in virtual environment")
            print("💡 To activate the virtual environment, run: source venv/bin/activate")
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
        print("\n🔧 Manual setup options:")
        print("Option 1 - Using uv (recommended):")
        print("1. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("2. Run: uv sync")
        print("\nOption 2 - Using virtual environment:")
        print("1. Create venv: python3 -m venv venv")
        print("2. Activate: source venv/bin/activate")
        print("3. Install: pip install -r requirements.txt")
        print("\nThen:")
        print("4. Copy .env.example to .env")
        print("5. Add your OpenAI API key to .env")

if __name__ == "__main__":
    main()
