#!/usr/bin/env python3
"""
Test script for sequential progression functionality
"""

def test_sequential_progression():
    """Test that domains can only be accessed sequentially"""
    print("🎮 Testing Sequential Progression...")
    
    try:
        from assessment_flow import AssessmentFlowManager
        from models import DomainStatus
        
        # Create assessment manager
        manager = AssessmentFlowManager()
        
        # Start assessment session
        session = manager.start_assessment_session("Python Programming", 3)
        print("✅ Assessment session started")
        
        # Test initial state - only first domain should be accessible
        assert manager.can_access_domain(0) == True, "First domain should be accessible"
        assert manager.can_access_domain(1) == False, "Second domain should be locked"
        assert manager.can_access_domain(2) == False, "Third domain should be locked"
        print("✅ Initial domain access control works")
        
        # Start first domain
        domain_name = manager.start_domain_assessment(0)
        assert session.domain_assessments[0].status == DomainStatus.IN_PROGRESS
        print(f"✅ Started first domain: {domain_name}")
        
        # Complete first domain
        session.domain_assessments[0].questions_attempted = 10
        session.domain_assessments[0].questions_correct = 8
        completed_assessment = manager.complete_domain_assessment(0)
        print(f"✅ Completed first domain with status: {completed_assessment.status}")
        
        # Now second domain should be accessible
        assert manager.can_access_domain(0) == True, "First domain should still be accessible"
        assert manager.can_access_domain(1) == True, "Second domain should now be accessible"
        assert manager.can_access_domain(2) == False, "Third domain should still be locked"
        print("✅ Sequential progression works - second domain unlocked")
        
        # Start and complete second domain
        manager.start_domain_assessment(1)
        session.domain_assessments[1].questions_attempted = 10
        session.domain_assessments[1].questions_correct = 9
        manager.complete_domain_assessment(1)
        
        # Now all domains should be accessible
        assert manager.can_access_domain(0) == True
        assert manager.can_access_domain(1) == True
        assert manager.can_access_domain(2) == True
        print("✅ All domains accessible after completing previous ones")
        
        print("🎉 Sequential progression tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Sequential progression test failed: {e}")
        return False

def test_domain_clicking_logic():
    """Test the domain clicking logic"""
    print("\n🖱️ Testing Domain Clicking Logic...")
    
    try:
        from app import KnowledgeAssessmentApp
        
        # Create app instance
        app = KnowledgeAssessmentApp()
        
        # Start assessment
        result = app.start_assessment("Python Programming", 3)
        assert "Knowledge Assessment started" in result[0]
        print("✅ Assessment started successfully")
        
        # Test domain display generation
        domain_display = app._generate_domain_display()
        assert "Level 1" in domain_display
        assert "Level 2" in domain_display
        assert "Level 3" in domain_display
        assert "data-clickable='True'" in domain_display
        assert "data-clickable='False'" in domain_display  # Some should be locked
        print("✅ Domain display includes level numbers and clickable states")
        
        # Test that locked domains show proper styling
        assert "🔒" in domain_display  # Locked icon should be present
        assert "opacity: 0.6" in domain_display  # Locked domains should be dimmed
        print("✅ Locked domains have proper visual indicators")
        
        print("🎉 Domain clicking logic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Domain clicking logic test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Sequential Progression Tests\n")
    
    tests = [
        test_sequential_progression,
        test_domain_clicking_logic
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All sequential progression tests passed!")
    else:
        print("⚠️ Some tests failed. Please review the issues above.")
