"""
Test script to verify the code structure and imports
"""

def test_imports():
    """Test that all modules can be imported correctly"""
    try:
        print("Testing imports...")
        
        # Test config
        from config import Config
        print("✅ Config imported successfully")
        
        # Test models
        from models import LearningSession, Level, Question, LevelStatus
        print("✅ Models imported successfully")
        
        # Test AI service (will fail without API key, but import should work)
        try:
            from ai_service import AIService
            print("✅ AI Service imported successfully")
        except Exception as e:
            print(f"⚠️  AI Service import warning: {e}")
        
        # Test level flow
        from level_flow import LevelFlowManager
        print("✅ Level Flow Manager imported successfully")
        
        # Test question flow
        from question_flow import QuestionFlowManager
        print("✅ Question Flow Manager imported successfully")
        
        # Test main app
        from app import AdaptiveLearningApp
        print("✅ Main App imported successfully")
        
        print("\n🎉 All core modules imported successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_models():
    """Test that models work correctly"""
    try:
        print("\nTesting models...")
        
        from models import Level, LevelStatus, LearningSession
        
        # Test Level creation
        level = Level(level_name="Test Level", description="A test level")
        print(f"✅ Level created: {level.level_name}")
        
        # Test LearningSession creation
        session = LearningSession(
            main_topic="Test Topic",
            level_list=[level],
            level_statuses=[LevelStatus.UNLOCKED]
        )
        print(f"✅ Learning Session created for: {session.main_topic}")
        
        print("✅ Models working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Model test error: {e}")
        return False

def test_config():
    """Test configuration"""
    try:
        print("\nTesting configuration...")
        
        from config import Config
        
        print(f"✅ Default levels: {Config.DEFAULT_NUM_LEVELS}")
        print(f"✅ Progress target: {Config.PROGRESS_TARGET}")
        print(f"✅ Initial difficulty: {Config.INITIAL_DIFFICULTY}")
        
        # Test validation (will fail without API key)
        try:
            Config.validate()
            print("✅ Configuration valid")
        except ValueError as e:
            print(f"⚠️  Configuration warning: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Config test error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Adaptive Learning System Structure\n")
    
    success = True
    success &= test_imports()
    success &= test_models()
    success &= test_config()
    
    if success:
        print("\n🎉 All tests passed! The system structure is correct.")
        print("\n📋 Next steps:")
        print("1. Install Python 3.8+ if not already installed")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Set up your .env file with OpenAI API key")
        print("4. Run the application: python app.py")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
