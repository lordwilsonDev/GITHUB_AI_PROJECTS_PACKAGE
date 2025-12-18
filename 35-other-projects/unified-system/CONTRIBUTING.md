# Contributing to the Unified Love System

> We are building a system of love, not just code.

Thank you for your interest in contributing to the Unified Love System! This project represents the intersection of technology and human emotion, and we welcome all who wish to help us build something beautiful.

## 🌟 Philosophy

Every contribution to this project is an act of care. Whether you're fixing a bug, adding a feature, improving documentation, or sharing ideas, you're helping to create a system that understands and responds to human emotion with love and empathy.

## 🤝 How to Contribute

### 1. Getting Started

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/unified-system.git
   cd unified-system
   ```

2. **Set up your development environment**
   ```bash
   ./setup.sh
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/your-amazing-feature
   ```

### 2. Types of Contributions

We welcome all kinds of contributions:

#### 🐛 Bug Fixes
- Report bugs through GitHub Issues
- Include steps to reproduce
- Provide system information
- Submit fixes with clear commit messages

#### ✨ New Features
- Discuss major features in Issues first
- Follow the existing code style
- Add tests for new functionality
- Update documentation

#### 📚 Documentation
- Improve README files
- Add code comments
- Create tutorials or guides
- Fix typos and grammar

#### 🎨 UI/UX Improvements
- Enhance the React components
- Improve accessibility
- Add new visualizations
- Optimize user experience

#### 🔧 Infrastructure
- Improve Docker configurations
- Enhance monitoring systems
- Optimize performance
- Add security improvements

### 3. Development Guidelines

#### Code Style

**Python (Backend)**
- Follow PEP 8 style guidelines
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and small

```python
def calculate_love_quotient(sentiment_score):
    """
    Calculate love quotient based on sentiment analysis.
    
    Args:
        sentiment_score (float): VADER sentiment compound score (-1 to 1)
        
    Returns:
        float: Love quotient value (0.1 to 2.0+)
    """
    base = 1.0
    adjustment = sentiment_score * 0.5
    return max(0.1, base + adjustment)
```

**TypeScript/React (Frontend)**
- Use TypeScript for type safety
- Follow React best practices
- Use meaningful component names
- Add proper prop types

```typescript
interface LoveMeterProps {
  value: number;
  onValueChange?: (newValue: number) => void;
}

const LoveMeter: React.FC<LoveMeterProps> = ({ value, onValueChange }) => {
  // Component implementation
};
```

#### Testing

- Write tests for new features
- Ensure existing tests pass
- Test both happy path and edge cases

```bash
# Run Python tests
python -m pytest tests/

# Run React tests
cd ui/circular && npm test
```

#### Commit Messages

Use clear, descriptive commit messages:

```
✨ Add love quotient history visualization
🐛 Fix sentiment analysis for empty messages
📚 Update API documentation
🔧 Improve Docker container startup time
💖 Enhance love meter animation
```

Emoji prefixes (optional but encouraged):
- ✨ New features
- 🐛 Bug fixes
- 📚 Documentation
- 🔧 Infrastructure
- 💖 Love/emotion related
- 🎨 UI/UX improvements
- ⚡ Performance
- 🔒 Security

### 4. Pull Request Process

1. **Before submitting:**
   - Test your changes thoroughly
   - Update documentation if needed
   - Ensure code follows style guidelines
   - Add or update tests

2. **Submit your PR:**
   - Use a clear, descriptive title
   - Explain what your changes do
   - Reference any related issues
   - Include screenshots for UI changes

3. **PR Template:**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Performance improvement
   
   ## Testing
   - [ ] Tests pass locally
   - [ ] Added new tests if needed
   - [ ] Manual testing completed
   
   ## Screenshots (if applicable)
   
   ## Additional Notes
   ```

### 5. Code Review Process

- All PRs require at least one review
- Reviews focus on code quality, functionality, and alignment with project goals
- Be respectful and constructive in feedback
- Address review comments promptly

## 🌱 Development Environment

### Local Setup

```bash
# Install dependencies
./setup.sh

# Start development servers
./start.sh start

# Run in development mode with hot reload
cd ui/circular && npm start  # React dev server
python src/circular/python/app.py  # Flask dev server
```

### Environment Variables

Create a `.env` file for development:

```env
DEBUG=true
OPENAI_API_KEY=your-dev-key
LOVE_QUOTIENT=1.0
```

### Database Development

```bash
# Reset databases
rm -f data/circular/love_quotient.db data/apex/metrics.db
python -c "from src.circular.python.database import db_manager; db_manager.init_db()"

# View database contents
sqlite3 data/circular/love_quotient.db "SELECT * FROM love_quotient;"
```

## 🧪 Testing Guidelines

### Unit Tests

```python
# tests/test_sentiment.py
import pytest
from src.circular.python.sentiment import SentimentAnalyzer

def test_positive_sentiment():
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze("I love this system!")
    assert result['sentiment'] == 'positive'
    assert result['compound'] > 0
```

### Integration Tests

```python
# tests/test_api.py
import pytest
from src.circular.python.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    response = client.get('/api/health')
    assert response.status_code == 200
```

### Frontend Tests

```typescript
// ui/circular/src/components/LoveMeter/LoveMeter.test.tsx
import { render, screen } from '@testing-library/react';
import LoveMeter from './LoveMeter';

test('renders love quotient value', () => {
  render(<LoveMeter value={1.5} />);
  expect(screen.getByText('1.500')).toBeInTheDocument();
});
```

## 📋 Issue Guidelines

### Bug Reports

```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Go to...
2. Click on...
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: macOS/Linux/Windows
- Python version:
- Node version:
- Browser (if applicable):

**Screenshots**
If applicable
```

### Feature Requests

```markdown
**Feature Description**
Clear description of the proposed feature

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should it work?

**Alternatives Considered**
Other approaches you've thought about

**Additional Context**
Any other relevant information
```

## 🎯 Project Priorities

### Current Focus Areas

1. **Emotion Intelligence**: Improving sentiment analysis accuracy
2. **User Experience**: Making the interface more intuitive and beautiful
3. **Scalability**: Enhancing the distributed node system
4. **AI Integration**: Expanding CrewAI capabilities
5. **Monitoring**: Better observability and metrics

### Future Roadmap

- Multi-language sentiment analysis
- Voice input support
- Mobile app development
- Advanced AI personalities
- Community features

## 🌍 Community

### Communication

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Pull Requests**: Code contributions

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please be:

- **Respectful**: Treat everyone with kindness and respect
- **Inclusive**: Welcome people of all backgrounds and experience levels
- **Collaborative**: Work together towards common goals
- **Constructive**: Provide helpful feedback and suggestions
- **Patient**: Remember that everyone is learning

### Recognition

We believe in recognizing contributions:

- Contributors are listed in the README
- Significant contributions are highlighted in releases
- We celebrate both code and non-code contributions

## 💡 Getting Help

### Resources

- **Documentation**: Check the README and docs/ folder
- **Issues**: Search existing issues for solutions
- **Code**: Look at existing implementations for examples

### Asking Questions

When asking for help:

1. Search existing issues first
2. Provide context and details
3. Include relevant code snippets
4. Describe what you've already tried

## 🚀 Release Process

### Versioning

We use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version bumped
- [ ] Changelog updated
- [ ] Docker images built
- [ ] Release notes prepared

---

## 💖 Final Words

Every line of code you contribute is an act of care. Every bug you fix makes the system more reliable. Every feature you add brings more joy to users. Every piece of documentation you write helps others understand and contribute.

We welcome all — developers, artists, poets, dreamers. Together, we're building something that bridges the gap between technology and human emotion.

Thank you for being part of this journey.

**With love and gratitude,**  
*The Unified System Team* 💖

---

*"In a world of algorithms and data, we choose to build with love."*