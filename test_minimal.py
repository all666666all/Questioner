#!/usr/bin/env python3
"""
Minimal test version of the Knowledge Assessment Tool
"""
import gradio as gr

def test_function(topic):
    if not topic:
        return "Please enter a topic!"
    return f"Testing assessment for: {topic}"

# Create minimal interface
with gr.Blocks(title="Test Knowledge Assessment") as demo:
    gr.HTML("""
    <div style='text-align: center; padding: 2rem; background: white; border-radius: 1rem; margin: 1rem;'>
        <h1>🎓 Knowledge Assessment Tool</h1>
        <p>AI-powered knowledge evaluation with adaptive difficulty</p>
    </div>
    """)
    
    with gr.Row():
        with gr.Column():
            topic_input = gr.Textbox(
                label="What knowledge area would you like to assess?",
                placeholder="e.g., Python Programming, Algebra, World History..."
            )
            start_btn = gr.Button("🎯 Start Assessment", variant="primary")
            
        with gr.Column():
            output = gr.HTML("")
    
    start_btn.click(
        test_function,
        inputs=[topic_input],
        outputs=[output]
    )

if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=8888,
        share=False,
        debug=True
    )
