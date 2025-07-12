#!/usr/bin/env python3
"""
Test script for the Knowledge Assessment Tool
"""

def test_basic_functionality():
    """Test basic functionality without AI calls"""
    print("🧪 Testing Knowledge Assessment Tool...")
    
    try:
        # Test imports
        from assessment_flow import AssessmentFlowManager
        from question_flow import QuestionFlowManager
        from models import DomainStatus, AdaptiveDifficultyEngine
        from config import Config
        print("✅ All imports successful")
        
        # Test configuration
        assert Config.DEFAULT_NUM_DOMAINS == 5
        assert Config.MIN_DOMAINS == 3
        assert Config.MAX_DOMAINS == 8
        print("✅ Configuration values correct")
        
        # Test adaptive difficulty engine
        engine = AdaptiveDifficultyEngine()
        assert engine.current_difficulty == 50
        print("✅ Adaptive difficulty engine initialized")
        
        # Test difficulty adjustment
        new_diff = engine.update_difficulty(True, 15.0, 0.8)  # Correct, fast, confident
        assert new_diff > 50  # Should increase difficulty
        print(f"✅ Difficulty adjustment works: {50} -> {new_diff}")
        
        # Test assessment manager initialization
        assessment_mgr = AssessmentFlowManager()
        print("✅ Assessment flow manager initialized")
        
        # Test question manager initialization
        question_mgr = QuestionFlowManager()
        print("✅ Question flow manager initialized")
        
        print("🎉 All basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_responsive_design():
    """Test responsive design elements"""
    print("\n📱 Testing responsive design...")
    
    try:
        # Check if CSS file exists and has responsive rules
        with open('styles.css', 'r') as f:
            css_content = f.read()
        
        # Check for iOS design system variables
        assert '--ios-blue' in css_content
        assert '--font-family' in css_content
        assert '--radius-md' in css_content
        print("✅ iOS design system variables present")
        
        # Check for responsive breakpoints
        assert '@media (max-width: 768px)' in css_content
        assert '@media (max-width: 480px)' in css_content
        print("✅ Responsive breakpoints defined")
        
        # Check for grid layouts
        assert 'grid-template-columns' in css_content
        print("✅ Grid layouts implemented")
        
        print("🎉 Responsive design tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Responsive design test failed: {e}")
        return False

def test_assessment_focus():
    """Test that the application is properly focused on assessment"""
    print("\n🎯 Testing assessment focus...")
    
    try:
        # Check app.py for assessment terminology
        with open('app.py', 'r', encoding='utf-8') as f:
            app_content = f.read()

        assert 'KnowledgeAssessmentApp' in app_content
        assert 'Knowledge Assessment Tool' in app_content
        assert 'start_assessment' in app_content
        assert 'domain_assessment' in app_content
        print("✅ Assessment terminology used throughout")

        # Check models for assessment structures
        with open('models.py', 'r', encoding='utf-8') as f:
            models_content = f.read()

        assert 'AssessmentDomain' in models_content
        assert 'DomainAssessment' in models_content
        assert 'AdaptiveDifficultyEngine' in models_content
        print("✅ Assessment-focused data models")

        # Check AI service for assessment prompts
        with open('ai_service.py', 'r', encoding='utf-8') as f:
            ai_content = f.read()
        
        assert 'assessment' in ai_content.lower()
        assert 'knowledge' in ai_content.lower()
        print("✅ AI service focused on assessment")
        
        print("🎉 Assessment focus tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Assessment focus test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Knowledge Assessment Tool Tests\n")
    
    tests = [
        test_basic_functionality,
        test_responsive_design,
        test_assessment_focus
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The Knowledge Assessment Tool is ready.")
    else:
        print("⚠️ Some tests failed. Please review the issues above.")
