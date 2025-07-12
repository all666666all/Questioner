"""
Main Gradio Application for Knowledge Assessment Tool
"""
import gradio as gr
import os
import time
from typing import Optional, List, Tuple
from assessment_flow import AssessmentFlowManager
from question_flow import QuestionFlowManager
from models import DomainStatus, Question, AdaptiveDifficultyEngine
from config import Config

class KnowledgeAssessmentApp:
    def __init__(self):
        self.assessment_manager = AssessmentFlowManager()
        self.question_manager = QuestionFlowManager()
        self.current_question: Optional[Question] = None
        
    def start_assessment(self, topic: str, num_domains: int = 5) -> Tuple[str, str, str]:
        """Start a new knowledge assessment session"""
        try:
            if not topic.strip():
                return "❌ Please enter a topic to assess!", "", ""

            # Start new assessment session
            session = self.assessment_manager.start_assessment_session(topic, num_domains)

            # Generate domain list display
            domain_display = self._generate_domain_display()
            stats_display = self._generate_stats_display()

            return (
                f"🎯 Knowledge Assessment started for '{topic}'! Click on a domain to begin assessment.",
                domain_display,
                stats_display
            )
        except Exception as e:
            return f"❌ Error: {str(e)}", "", ""
    
    def _generate_domain_display(self) -> str:
        """Generate HTML display for assessment domains"""
        session = self.assessment_manager.get_current_session()
        if not session:
            return "No active assessment session."

        html = "<div class='domains-container'>"

        for i, (domain, assessment) in enumerate(zip(session.domain_list, session.domain_assessments)):
            # Check if domain is accessible (sequential progression)
            is_accessible = self.assessment_manager.can_access_domain(i)

            # Determine status class and icon
            status = assessment.status
            if not is_accessible:
                icon = "🔒"
                status_text = "Locked"
                card_class = "assessment-card locked"
                clickable = "False"
            elif status == DomainStatus.NOT_STARTED:
                icon = "📋"
                status_text = "Ready to Assess"
                card_class = "assessment-card not-started"
                clickable = "True"
            elif status == DomainStatus.IN_PROGRESS:
                icon = "⏳"
                status_text = "In Progress"
                card_class = "assessment-card in-progress"
                clickable = "True"
            elif status == DomainStatus.COMPLETED:
                icon = "✅"
                status_text = "Completed"
                card_class = "assessment-card completed"
                clickable = "False"
            elif status == DomainStatus.MASTERED:
                icon = "🏆"
                status_text = "Mastered"
                card_class = "assessment-card mastered"
                clickable = "False"
            else:  # STRUGGLING
                icon = "⚠️"
                status_text = "Needs Review"
                card_class = "assessment-card struggling"
                clickable = "True"

            # Calculate progress if assessment has started
            progress_info = ""
            if assessment.questions_attempted > 0:
                accuracy = (assessment.questions_correct / assessment.questions_attempted) * 100
                progress_info = f"""
                <div class='domain-progress'>
                    <div class='progress-stats'>
                        <span>Questions: {assessment.questions_attempted}</span>
                        <span>Accuracy: {accuracy:.1f}%</span>
                        <span>Difficulty: {assessment.current_difficulty}</span>
                    </div>
                </div>
                """

            current_class = "current" if i == session.current_domain_index else ""

            # Add level number for gamification
            level_number = i + 1

            # Add connection line for progression visualization
            connection_line = ""
            if i < len(session.domain_list) - 1:  # Not the last domain
                next_accessible = self.assessment_manager.can_access_domain(i + 1)
                line_color = "#34C759" if next_accessible else "#E5E5EA"
                connection_line = f"""
                <div style='position: absolute; right: -8px; top: 50%; width: 16px; height: 2px; background: {line_color}; z-index: 1;'></div>
                """

            # Add unlock animation class if recently unlocked
            unlock_class = "recently-unlocked" if is_accessible and status == DomainStatus.NOT_STARTED and i > 0 else ""

            html += f"""
            <div class='{card_class} {current_class} {unlock_class}' data-domain='{i}' data-clickable='{clickable}' onclick='selectDomain({i})' style='cursor: {"pointer" if clickable == "True" else "not-allowed"}; opacity: {"1.0" if is_accessible else "0.6"}; position: relative;'>
                {connection_line}
                <div style='display: flex; align-items: center; gap: 1rem;'>
                    <div style='display: flex; flex-direction: column; align-items: center; min-width: 60px;'>
                        <span style='font-size: 0.8rem; color: {"#666" if is_accessible else "#aaa"}; font-weight: bold;'>Level {level_number}</span>
                        <div style='width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: {"rgba(0, 122, 255, 0.1)" if is_accessible else "rgba(142, 142, 147, 0.1)"}; border: 2px solid {"#007AFF" if is_accessible else "#E5E5EA"};'>
                            <span style='font-size: 1.2rem;'>{icon}</span>
                        </div>
                    </div>
                    <div style='flex: 1;'>
                        <h3 style='margin: 0; color: {"#333" if is_accessible else "#999"}; display: flex; align-items: center; gap: 0.5rem;'>
                            {domain.domain_name}
                            {"<span style='font-size: 0.7rem; background: #FF9500; color: white; padding: 2px 6px; border-radius: 8px;'>NEW!</span>" if unlock_class else ""}
                        </h3>
                        <p style='margin: 0.5rem 0 0 0; color: {"#666" if is_accessible else "#aaa"}; font-size: 0.9rem;'>{domain.description}</p>
                        <div style='display: flex; align-items: center; gap: 0.5rem; margin-top: 0.5rem;'>
                            <span class='status-badge {status.value}'>{status_text}</span>
                            {"<span style='font-size: 0.8rem; color: #666;'>Click to start!</span>" if is_accessible and status == DomainStatus.NOT_STARTED else ""}
                        </div>
                        {progress_info}
                    </div>
                </div>
            </div>
            """

        html += "</div>"
        return html
    
    def _generate_stats_display(self) -> str:
        """Generate assessment statistics display"""
        session = self.assessment_manager.get_current_session()
        if not session:
            return ""

        completed, total = self.assessment_manager.get_assessment_progress()
        overall_score = self.assessment_manager.calculate_overall_score()

        # Calculate domain-specific stats
        mastered_domains = sum(1 for assessment in session.domain_assessments
                              if assessment.status == DomainStatus.MASTERED)
        struggling_domains = sum(1 for assessment in session.domain_assessments
                               if assessment.status == DomainStatus.STRUGGLING)

        html = f"""
        <div class='stats-container'>
            <div class='stat-card'>
                <div class='stat-value'>{completed}/{total}</div>
                <div class='stat-label'>Domains Assessed</div>
            </div>
            <div class='stat-card'>
                <div class='stat-value'>{overall_score:.1f}%</div>
                <div class='stat-label'>Overall Score</div>
            </div>
            <div class='stat-card'>
                <div class='stat-value'>{mastered_domains}</div>
                <div class='stat-label'>Mastered</div>
            </div>
            <div class='stat-card'>
                <div class='stat-value'>{struggling_domains}</div>
                <div class='stat-label'>Need Review</div>
            </div>
        </div>
        """
        return html
    
    def start_domain_assessment(self, domain_index: int) -> Tuple[str, str, str, str]:
        """Start assessment for a specific domain"""
        try:
            if not self.assessment_manager.can_access_domain(domain_index):
                return "❌ This domain is not accessible!", "", "", ""

            # Start domain assessment
            domain_name = self.assessment_manager.start_domain_assessment(domain_index)

            # Get the domain assessment object
            session = self.assessment_manager.get_current_session()
            domain_assessment = session.domain_assessments[domain_index]

            # Start question session for this domain
            self.question_manager.start_domain_assessment(domain_assessment)

            # Generate first question
            question_display, options_display = self._generate_question()
            progress_display = self._generate_progress_display()

            return (
                f"� Starting assessment for: {domain_name}",
                question_display,
                options_display,
                progress_display
            )
        except Exception as e:
            return f"❌ Error: {str(e)}", "", "", ""
    
    def _generate_question(self) -> Tuple[str, str]:
        """Generate and display a new question"""
        try:
            self.current_question = self.question_manager.generate_next_question()
            
            question_html = f"""
            <div class='question-card fade-in'>
                <div class='question-text'>{self.current_question.question}</div>
            </div>
            """
            
            options_html = "<div class='options-container'>"
            for i, option in enumerate(self.current_question.options):
                letter = chr(65 + i)
                options_html += f"""
                <div class='option-item' onclick='selectAnswer("{letter}")' style='cursor: pointer; margin: 0.5rem 0; padding: 1rem; border: 2px solid #E5E5EA; border-radius: 12px; transition: all 0.2s ease;' onmouseover='this.style.borderColor="#007AFF"; this.style.backgroundColor="rgba(0,122,255,0.05)"' onmouseout='this.style.borderColor="#E5E5EA"; this.style.backgroundColor="transparent"'>
                    <strong>{letter}.</strong> {option}
                </div>
                """
            options_html += "</div>"
            
            return question_html, options_html
        except Exception as e:
            return f"❌ Error generating question: {str(e)}", ""
    
    def _generate_progress_display(self) -> str:
        """Generate progress display for current domain assessment"""
        assessment_info = self.question_manager.get_assessment_info()
        questions_answered, target_questions, accuracy = self.question_manager.get_assessment_progress()

        progress_percentage = (questions_answered / target_questions) * 100

        # Determine progress bar color based on accuracy
        if accuracy >= 0.8:
            progress_class = "success"
        elif accuracy >= 0.6:
            progress_class = ""
        elif accuracy >= 0.4:
            progress_class = "warning"
        else:
            progress_class = "error"

        html = f"""
        <div class='progress-container'>
            <h4>Assessment Progress: {assessment_info['domain_name']}</h4>
            <div class='progress-bar'>
                <div class='progress-fill {progress_class}' style='width: {progress_percentage:.1f}%'></div>
            </div>
            <div style='display: flex; justify-content: space-between; margin-top: 0.5rem;'>
                <span>Questions: {questions_answered}/{target_questions}</span>
                <span>Difficulty: {assessment_info['current_difficulty']}</span>
            </div>
            <div style='display: flex; justify-content: space-between; margin-top: 0.5rem;'>
                <span>Accuracy: {accuracy * 100:.1f}%</span>
                <span>Confidence: {assessment_info['confidence_score'] * 100:.1f}%</span>
            </div>
            <div style='display: flex; justify-content: space-between; margin-top: 0.5rem; font-size: 0.9rem; color: #666;'>
                <span>Avg Response Time: {assessment_info['average_response_time']:.1f}s</span>
                <span>Knowledge Gaps: {len(assessment_info['knowledge_gaps'])}</span>
            </div>
        </div>
        """
        return html
    
    def submit_answer(self, answer_index: int, confidence: float = 0.5) -> Tuple[str, str, str, str]:
        """Submit an answer and get feedback"""
        try:
            if not self.current_question:
                return "❌ No active question!", "", "", ""

            # Submit answer with confidence level
            is_correct, explanation, is_domain_complete = self.question_manager.submit_answer(
                self.current_question, answer_index, confidence
            )

            # Generate feedback
            feedback = f"""
            <div class='feedback-card {"correct" if is_correct else "incorrect"}'>
                <h3>{'✅ Correct!' if is_correct else '❌ Incorrect'}</h3>
                <p><strong>Explanation:</strong> {explanation}</p>
            </div>
            """

            # Update progress display
            progress_display = self._generate_progress_display()

            if is_domain_complete:
                # Domain assessment completed
                domain_assessment = self.question_manager.complete_domain_assessment()
                session = self.assessment_manager.get_current_session()
                current_domain_index = session.current_domain_index

                # Complete domain in assessment manager
                completed_assessment = self.assessment_manager.complete_domain_assessment(current_domain_index)

                # Check if all assessments are complete
                if self.assessment_manager.is_assessment_complete():
                    # All domains assessed - show final summary
                    summary = self.assessment_manager.generate_final_summary()
                    summary_display = self._generate_summary_display(summary)
                    return (
                        feedback,
                        "🎉 Assessment Complete! Here's your knowledge profile:",
                        summary_display,
                        ""
                    )
                else:
                    # Domain completed, return to domain selection
                    domain_display = self._generate_domain_display()
                    stats_display = self._generate_stats_display()
                    next_domain = self.assessment_manager.get_next_domain_index()
                    next_message = f" Next: {session.domain_list[next_domain].domain_name}" if next_domain is not None else ""
                    return (
                        feedback,
                        f"� Domain assessment completed! Status: {completed_assessment.status.value}{next_message}",
                        domain_display,
                        stats_display
                    )
            else:
                # Continue with next question
                question_display, options_display = self._generate_question()
                return (
                    feedback,
                    question_display,
                    options_display,
                    progress_display
                )
                
        except Exception as e:
            return f"❌ Error: {str(e)}", "", "", ""
    
    def _generate_summary_display(self, summary) -> str:
        """Generate final assessment summary display"""
        html = f"""
        <div class='summary-container'>
            <h2>{summary.title}</h2>
            <div class='summary-stats'>
                <div class='stat-card'>
                    <div class='stat-value'>{summary.overall_score:.1f}%</div>
                    <div class='stat-label'>Overall Score</div>
                </div>
                <div class='stat-card'>
                    <div class='stat-value'>{summary.knowledge_level}</div>
                    <div class='stat-label'>Knowledge Level</div>
                </div>
                <div class='stat-card'>
                    <div class='stat-value'>{summary.total_time_minutes:.1f}m</div>
                    <div class='stat-label'>Time Taken</div>
                </div>
                <div class='stat-card'>
                    <div class='stat-value'>{summary.domains_assessed}</div>
                    <div class='stat-label'>Domains Assessed</div>
                </div>
            </div>
            <div class='summary-section'>
                <h3>💪 Your Strengths</h3>
                <ul>
                    {''.join(f'<li>{strength}</li>' for strength in summary.strengths)}
                </ul>
            </div>
            <div class='summary-section'>
                <h3>📚 Areas for Improvement</h3>
                <ul>
                    {''.join(f'<li>{area}</li>' for area in summary.areas_for_improvement)}
                </ul>
            </div>
            <div class='summary-section'>
                <h3>🎯 Recommendations</h3>
                <ul>
                    {''.join(f'<li>{rec}</li>' for rec in summary.recommendations)}
                </ul>
            </div>
        </div>
        """
        return html

# Initialize the app
app = KnowledgeAssessmentApp()

def create_interface():
    """Create the Gradio interface"""

    # Load custom CSS
    css_path = Config.CUSTOM_CSS_PATH
    custom_css = ""
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            custom_css = f.read()

    # JavaScript for interactive domain clicking and answer selection
    custom_js = """
    function() {
        // Add global function for domain selection
        window.selectDomain = function(domainIndex) {
            // Find the domain selector input and update it
            const domainInput = document.querySelector('input[data-testid="number-input"]');
            if (domainInput) {
                domainInput.value = domainIndex;
                domainInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
        };

        // Add global function for answer selection
        window.selectAnswer = function(answerLetter) {
            // Find the answer radio buttons and select the correct one
            const radioButtons = document.querySelectorAll('input[type="radio"][name*="radio"]');
            for (let radio of radioButtons) {
                if (radio.nextElementSibling && radio.nextElementSibling.textContent.trim() === answerLetter) {
                    radio.checked = true;
                    radio.dispatchEvent(new Event('change', { bubbles: true }));
                    break;
                }
            }
        };

        // Add click handlers for assessment cards
        document.addEventListener('click', function(e) {
            const card = e.target.closest('.assessment-card[data-clickable="True"]');
            if (card) {
                const domainIndex = card.getAttribute('data-domain');
                if (domainIndex !== null) {
                    selectDomain(parseInt(domainIndex));
                }
            }
        });
    }
    """

    with gr.Blocks(css=custom_css, js=custom_js, theme=gr.themes.Soft(), title="Knowledge Assessment Tool") as interface:

        # Header
        gr.HTML("""
        <div class='main-header'>
            <h1>� Knowledge Assessment Tool</h1>
            <p>AI-powered knowledge evaluation with adaptive difficulty</p>
        </div>
        """)

        # State variables
        current_state = gr.State("start")  # start, assessing, questioning

        with gr.Row():
            with gr.Column(scale=2):
                # Topic input section
                with gr.Group():
                    gr.Markdown("## 📋 Start Your Knowledge Assessment")
                    topic_input = gr.Textbox(
                        label="What knowledge area would you like to assess?",
                        placeholder="e.g., Python Programming, Algebra, World History...",
                        lines=1
                    )
                    with gr.Row():
                        num_domains = gr.Slider(
                            minimum=Config.MIN_DOMAINS,
                            maximum=Config.MAX_DOMAINS,
                            value=Config.DEFAULT_NUM_DOMAINS,
                            step=1,
                            label="Number of Knowledge Domains"
                        )
                        start_btn = gr.Button("🎯 Start Assessment", variant="primary")

                # Main content area
                status_display = gr.HTML("")
                main_content = gr.HTML("")
                secondary_content = gr.HTML("")

            with gr.Column(scale=1):
                # Side panel for stats and progress
                stats_panel = gr.HTML("")

                # Action buttons (hidden initially)
                with gr.Group(visible=False) as action_buttons:
                    gr.Markdown("### Assessment Actions")
                    domain_select = gr.Number(label="Selected Domain", value=0, visible=True)

                    # Question answering
                    answer_select = gr.Radio(
                        choices=["A", "B", "C", "D", "E", "F"],
                        label="Select Answer",
                        visible=False
                    )
                    submit_answer_btn = gr.Button("Submit Answer", visible=False)
                    next_question_btn = gr.Button("Next Question", visible=False)
                    back_to_domains_btn = gr.Button("← Back to Domains", visible=False, variant="secondary")

        # Event handlers
        def handle_start_assessment(topic, domains):
            result = app.start_assessment(topic, int(domains))
            return (
                result[0],  # status
                result[1],  # main content (domains)
                "",         # secondary content
                result[2],  # stats
                gr.update(visible=True),  # show action buttons
                "assessing"  # update state
            )

        def handle_domain_click(domain_idx):
            """Handle domain selection with sequential progression"""
            try:
                domain_index = int(domain_idx)

                # Check if domain is accessible
                if not app.assessment_manager.can_access_domain(domain_index):
                    # Return to domain selection with error message
                    domain_display = app._generate_domain_display()
                    stats_display = app._generate_stats_display()
                    return (
                        f"🔒 Domain {domain_index + 1} is locked! Complete previous domains first.",
                        domain_display,
                        "",  # clear secondary content
                        stats_display,
                        gr.update(visible=False),  # hide answer options
                        gr.update(visible=False),  # hide submit button
                        gr.update(visible=False),  # hide back button
                        "assessing"  # stay in assessing state
                    )

                # Start domain assessment
                result = app.start_domain_assessment(domain_index)
                return (
                    result[0],  # status
                    result[1],  # question
                    result[2],  # options
                    result[3],  # progress
                    gr.update(visible=True, choices=["A", "B", "C", "D", "E", "F"][:len(app.current_question.options) if app.current_question else 4]),
                    gr.update(visible=True),  # submit button
                    gr.update(visible=True),  # back to domains button
                    "questioning"  # state
                )
            except Exception as e:
                return (
                    f"❌ Error selecting domain: {str(e)}",
                    "",
                    "",
                    "",
                    gr.update(visible=False),
                    gr.update(visible=False),
                    gr.update(visible=False),
                    "assessing"
                )

        def handle_answer_submit(answer_choice):
            if not answer_choice:
                return "Please select an answer!", "", "", "", gr.update(), gr.update()

            # Convert letter to index
            answer_index = ord(answer_choice) - ord('A')
            # For now, use default confidence - could be enhanced with confidence slider
            result = app.submit_answer(answer_index, confidence=0.7)

            return (
                result[0],  # feedback
                result[1],  # next content
                result[2],  # secondary content
                result[3],  # progress/stats
                gr.update(value=None),  # clear answer selection
                gr.update(visible=True) if result[1] else gr.update(visible=False),  # next question button
                gr.update(visible=True)  # keep back button visible
            )

        def handle_back_to_domains():
            """Return to domain selection view"""
            domain_display = app._generate_domain_display()
            stats_display = app._generate_stats_display()
            return (
                "📋 Select a domain to continue your assessment:",
                domain_display,
                "",  # clear secondary content
                stats_display,
                gr.update(visible=False),  # hide answer options
                gr.update(visible=False),  # hide submit button
                gr.update(visible=False),  # hide next question button
                gr.update(visible=False),  # hide back button
                "assessing"  # return to assessing state
            )

        # Wire up events
        start_btn.click(
            handle_start_assessment,
            inputs=[topic_input, num_domains],
            outputs=[status_display, main_content, secondary_content, stats_panel, action_buttons, current_state]
        )

        # Domain selection
        domain_select.change(
            handle_domain_click,
            inputs=[domain_select],
            outputs=[status_display, main_content, secondary_content, stats_panel, answer_select, submit_answer_btn, back_to_domains_btn, current_state]
        )

        # Answer submission
        submit_answer_btn.click(
            handle_answer_submit,
            inputs=[answer_select],
            outputs=[status_display, main_content, secondary_content, stats_panel, answer_select, next_question_btn, back_to_domains_btn]
        )

        # Back to domains
        back_to_domains_btn.click(
            handle_back_to_domains,
            inputs=[],
            outputs=[status_display, main_content, secondary_content, stats_panel, answer_select, submit_answer_btn, next_question_btn, back_to_domains_btn, current_state]
        )



    return interface

if __name__ == "__main__":
    # Validate configuration
    try:
        Config.validate()
        interface = create_interface()
        interface.launch(
            server_name="127.0.0.1",
            server_port=9999,
            share=False,
            debug=True
        )
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        print("Please check your configuration and ensure you have set up your .env file correctly.")
