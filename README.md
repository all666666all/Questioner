# 🎓 Adaptive Learning System

An AI-powered adaptive learning platform that creates personalized learning paths and adjusts difficulty based on user performance.

## ✨ Features

- **🎯 AI-Generated Learning Paths**: Automatically breaks down any topic into 4-8 progressive levels
- **🎮 Gamified Experience**: Level-based progression with visual feedback and achievements
- **🧠 Adaptive Difficulty**: Questions get harder when you succeed, easier when you struggle
- **📊 Progress Tracking**: Real-time progress bars and performance statistics
- **🎨 Beautiful UI**: Modern, responsive interface with smooth animations
- **📈 Learning Analytics**: Detailed reports on strengths, weaknesses, and recommendations

## 🏗️ Architecture

The system uses a two-layer architecture:

### Outer Layer - Level Flow System
- Manages the overall learning path
- Handles level progression and unlocking
- Tracks completion status across all levels

### Inner Layer - Question Flow System  
- Generates adaptive questions within each level
- Adjusts difficulty based on performance
- Tracks progress using a progress bar system (0-100)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation

1. **Clone and setup**:
```bash
git clone <repository-url>
cd adaptive-learning-system
pip install -r requirements.txt
```

2. **Configure API keys**:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

3. **Run the application**:
```bash
python app.py
```

4. **Open your browser** to `http://localhost:7860`

## 🎮 How to Use

1. **Start Learning**: Enter any topic you want to learn (e.g., "Python Programming", "Algebra", "World History")

2. **Choose Levels**: Select how many levels you want (4-8 recommended)

3. **Progress Through Levels**: 
   - Click on unlocked levels to start
   - Answer questions to build progress (0-100)
   - Difficulty adapts based on your performance

4. **Complete Your Journey**: Get a detailed summary of your learning performance

## 🔧 Configuration

Edit `config.py` to customize:

- **AI Model**: Change OpenAI model (default: gpt-4)
- **Progress Settings**: Adjust progress targets and bonuses
- **Difficulty Settings**: Modify difficulty adjustment rates
- **Level Settings**: Change min/max number of levels

## 📁 Project Structure

```
adaptive-learning-system/
├── app.py              # Main Gradio application
├── config.py           # Configuration settings
├── models.py           # Data models (Pydantic)
├── ai_service.py       # AI prompt system
├── level_flow.py       # Level management system
├── question_flow.py    # Question generation system
├── styles.css          # Custom CSS styling
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
└── README.md          # This file
```

## 🤖 AI Prompts

The system uses three specialized AI prompts:

1. **Learning Path Planning AI**: Breaks topics into logical learning levels
2. **Question Generation AI**: Creates adaptive multiple-choice questions
3. **Learning Summary AI**: Analyzes performance and provides recommendations

## 🎨 Customization

### Styling
- Edit `styles.css` to customize the appearance
- Modify color schemes, animations, and layout

### AI Behavior
- Adjust prompts in `ai_service.py` for different question styles
- Modify difficulty algorithms in `question_flow.py`

### Progress System
- Change progress calculation in `config.py`
- Customize level completion criteria

## 🐛 Troubleshooting

**Common Issues:**

1. **API Key Error**: Make sure your OpenAI API key is set in `.env`
2. **Import Errors**: Run `pip install -r requirements.txt`
3. **Port Conflicts**: Change the port in `app.py` if 7860 is in use

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with [Gradio](https://gradio.app/) for the web interface
- Powered by OpenAI's GPT models for content generation
- Inspired by adaptive learning research and gamification principles
