"""
Demo script showing the Adaptive Learning System workflow
This script demonstrates the system without requiring API keys or external dependencies
"""

from models import Level, LevelStatus, LearningSession, Question, QuestionSession, LevelReport
from typing import List

class MockAIService:
    """Mock AI service for demonstration purposes"""
    
    def generate_learning_path(self, main_topic: str, num_levels: int) -> List[Level]:
        """Generate a mock learning path"""
        if "python" in main_topic.lower():
            return [
                Level(level_name="Python Basics", description="Learn variables, data types, and basic syntax"),
                Level(level_name="Control Structures", description="Master if statements, loops, and functions"),
                Level(level_name="Data Structures", description="Work with lists, dictionaries, and sets"),
                Level(level_name="Object-Oriented Programming", description="Understand classes, objects, and inheritance"),
                Level(level_name="File Handling & Modules", description="Learn to work with files and import modules"),
                Level(level_name="Error Handling", description="Master try-except blocks and debugging")
            ][:num_levels]
        else:
            return [
                Level(level_name=f"Level {i+1}: {main_topic} Fundamentals", 
                     description=f"Learn the basics of {main_topic} - Part {i+1}")
                for i in range(num_levels)
            ]
    
    def generate_question(self, topic: str, difficulty: int, past_weaknesses: List[str] = None) -> Question:
        """Generate a mock question"""
        if "python" in topic.lower():
            if difficulty < 30:
                return Question(
                    question="What is the correct way to create a variable in Python?",
                    options=["var x = 5", "x = 5", "int x = 5", "x := 5"],
                    correct_answer_index=1,
                    knowledge_tag="variable_assignment",
                    explanation="In Python, you create variables by simply assigning a value: x = 5"
                )
            elif difficulty < 70:
                return Question(
                    question="Which of the following is a mutable data type in Python?",
                    options=["tuple", "string", "list", "int"],
                    correct_answer_index=2,
                    knowledge_tag="data_types",
                    explanation="Lists are mutable in Python, meaning you can change their contents after creation."
                )
            else:
                return Question(
                    question="What does the 'super()' function do in Python?",
                    options=[
                        "Creates a new class",
                        "Calls the parent class method",
                        "Deletes an object",
                        "Imports a module"
                    ],
                    correct_answer_index=1,
                    knowledge_tag="inheritance",
                    explanation="super() is used to call methods from the parent class in inheritance."
                )
        else:
            return Question(
                question=f"Sample question about {topic} (difficulty: {difficulty})",
                options=["Option A", "Option B", "Option C", "Option D"],
                correct_answer_index=1,
                knowledge_tag="general",
                explanation="This is a sample explanation for demonstration purposes."
            )

def demo_learning_flow():
    """Demonstrate the complete learning flow"""
    print("🎓 Adaptive Learning System Demo")
    print("=" * 50)
    
    # Initialize mock AI service
    ai_service = MockAIService()
    
    # 1. Create learning path
    print("\n1. 🎯 Creating Learning Path")
    topic = "Python Programming"
    levels = ai_service.generate_learning_path(topic, 4)
    
    print(f"Topic: {topic}")
    for i, level in enumerate(levels):
        print(f"  Level {i+1}: {level.level_name}")
        print(f"    {level.description}")
    
    # 2. Initialize learning session
    print("\n2. 🚀 Starting Learning Session")
    session = LearningSession(
        main_topic=topic,
        level_list=levels,
        level_statuses=[LevelStatus.UNLOCKED] + [LevelStatus.LOCKED] * (len(levels) - 1)
    )
    
    print(f"Session created with {len(session.level_list)} levels")
    print(f"Current level: {session.level_list[0].level_name}")
    
    # 3. Simulate question flow for first level
    print("\n3. 🎮 Starting Level: Python Basics")
    question_session = QuestionSession(
        level_name=session.level_list[0].level_name,
        progress=0,
        difficulty=50
    )
    
    # Simulate answering questions
    questions_answered = 0
    while question_session.progress < 100 and questions_answered < 8:
        questions_answered += 1
        
        # Generate question
        question = ai_service.generate_question(
            question_session.level_name,
            question_session.difficulty,
            question_session.weakness_tags
        )
        
        print(f"\n   Question {questions_answered}:")
        print(f"   {question.question}")
        for i, option in enumerate(question.options):
            print(f"   {chr(65+i)}. {option}")
        
        # Simulate user answer (sometimes correct, sometimes wrong)
        import random
        user_answer = random.choice([question.correct_answer_index, (question.correct_answer_index + 1) % len(question.options)])
        is_correct = user_answer == question.correct_answer_index
        
        print(f"   User selected: {chr(65 + user_answer)} ({'✅ Correct' if is_correct else '❌ Incorrect'})")
        
        # Update session
        question_session.questions_attempted += 1
        if is_correct:
            question_session.questions_correct += 1
            # Increase progress and difficulty
            progress_bonus = 15 if question_session.difficulty >= 70 else 12
            question_session.progress += progress_bonus
            question_session.difficulty = min(90, question_session.difficulty + 8)
        else:
            # Add weakness and decrease difficulty
            if question.knowledge_tag not in question_session.weakness_tags:
                question_session.weakness_tags.append(question.knowledge_tag)
            question_session.difficulty = max(10, question_session.difficulty - 15)
        
        print(f"   Progress: {question_session.progress}/100, Difficulty: {question_session.difficulty}")
        
        if question_session.progress >= 100:
            print("\n   🎉 Level completed!")
            break
    
    # 4. Generate level report
    print("\n4. 📊 Level Report")
    final_status = LevelStatus.PASSED if question_session.progress >= 100 else LevelStatus.FAILED
    accuracy = (question_session.questions_correct / question_session.questions_attempted) * 100
    
    report = LevelReport(
        level_name=question_session.level_name,
        final_status=final_status,
        weakness_tags=question_session.weakness_tags,
        questions_attempted=question_session.questions_attempted,
        questions_correct=question_session.questions_correct,
        final_difficulty=question_session.difficulty
    )
    
    print(f"   Status: {report.final_status.value}")
    print(f"   Questions: {report.questions_correct}/{report.questions_attempted} ({accuracy:.1f}% accuracy)")
    print(f"   Weaknesses: {', '.join(report.weakness_tags) if report.weakness_tags else 'None identified'}")
    print(f"   Final Difficulty: {report.final_difficulty}")
    
    # 5. Update session and show next steps
    print("\n5. 🎯 Next Steps")
    session.history.append(report)
    session.level_statuses[0] = final_status
    
    if final_status == LevelStatus.PASSED and len(session.level_list) > 1:
        session.level_statuses[1] = LevelStatus.UNLOCKED
        print(f"   ✅ Level unlocked: {session.level_list[1].level_name}")
    
    print(f"   Overall Progress: {len(session.history)}/{len(session.level_list)} levels completed")
    
    print("\n🎉 Demo completed! This shows how the adaptive learning system works:")
    print("   • AI generates personalized learning paths")
    print("   • Questions adapt to user performance")
    print("   • Progress tracking with detailed analytics")
    print("   • Gamified level progression")

if __name__ == "__main__":
    demo_learning_flow()
