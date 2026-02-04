# Contributing to TriAI Compare

First off, thank you for considering contributing to TriAI Compare! 🎉

## How Can I Contribute?

### 🐛 Reporting Bugs

**Before submitting a bug report:**
- Check the [Issues](https://github.com/YOUR_USERNAME/triai-compare/issues) to see if it's already reported
- Make sure you're using the latest version

**When submitting a bug report, include:**
- Clear, descriptive title
- Steps to reproduce the issue
- Expected vs. actual behavior
- Screenshots if applicable
- Your environment (OS, Python version, browser)

### 💡 Suggesting Features

We love feature ideas! Please:
- Check [Discussions](https://github.com/YOUR_USERNAME/triai-compare/discussions) first
- Explain the problem you're trying to solve
- Describe your proposed solution
- Provide examples or mockups if possible

### 🔧 Pull Requests

1. **Fork the repo** and create your branch from `main`
2. **Test your changes** thoroughly
3. **Follow the code style** (PEP 8 for Python)
4. **Write clear commit messages**
5. **Update documentation** if needed

#### Good Pull Request Examples:
- Adding a new Council Mode role
- Improving UI/UX
- Fixing bugs
- Adding tests
- Improving documentation

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/triai-compare.git
cd triai-compare

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env with your API keys
cp .env.example .env

# Run locally
python app.py
```

## Code Style

- **Python**: Follow PEP 8
- **JavaScript**: Use consistent indentation (2 spaces)
- **CSS**: Use BEM naming convention where applicable
- **Comments**: Add comments for complex logic

## Adding New Council Roles

To add a new expert role to Council Mode:

1. Edit `council_roles.py`
2. Add your role to the `COUNCIL_ROLES` dictionary:

```python
"role_key": {
    "name": "Role Name",
    "prompt": "Detailed system prompt for this role...",
    "emoji": "🎯",
    "default_model": "openai"  # or anthropic, google, perplexity
}
```

3. Test it thoroughly
4. Submit a PR with examples of the role in action

## Testing

Before submitting a PR:

```bash
# Test API connections
python test_apis.py

# Test the full application
python app.py
# Navigate to http://localhost:5000 and test manually
```

## Commit Message Guidelines

Use clear, descriptive commit messages:

```
feat: Add legal expert to Council Mode
fix: Resolve image upload bug in file processor
docs: Update README with deployment instructions
style: Format code with Black formatter
refactor: Simplify query_google function
```

Prefixes:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code formatting
- `refactor:` Code restructuring
- `test:` Adding tests
- `chore:` Maintenance tasks

## Need Help?

- **Questions?** Open a [Discussion](https://github.com/YOUR_USERNAME/triai-compare/discussions)
- **Stuck?** Comment on the related Issue
- **Want to chat?** Reach out via [email/discord/twitter]

## Recognition

Contributors will be added to our README! We appreciate every contribution, no matter how small.

---

**Thank you for making TriAI Compare better! 🚀**
