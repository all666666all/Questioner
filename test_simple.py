"""
Simple test to check if Gradio is working
"""
import gradio as gr

def greet(name):
    return f"Hello {name}!"

# Create a simple interface
with gr.Blocks() as demo:
    gr.Markdown("# Simple Test Interface")
    name_input = gr.Textbox(label="Enter your name")
    output = gr.Textbox(label="Output")
    btn = gr.Button("Say Hello")
    btn.click(greet, inputs=name_input, outputs=output)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",  # Listen on all interfaces
        server_port=7860,
        share=False,
        debug=True
    )
