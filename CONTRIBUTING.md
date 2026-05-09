# Contributing to PhishGuard

Thank you for your interest in contributing to PhishGuard! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/phishguard/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Screenshots if applicable

### Suggesting Features

1. Check existing feature requests
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Potential implementation approach
   - Any relevant examples

### Pull Requests

1. **Fork the repository**
```bash
git clone https://github.com/yourusername/phishguard.git
cd phishguard
git remote add upstream https://github.com/original/phishguard.git
```

2. **Create a feature branch**
```bash
git checkout -b feature/your-feature-name
```

3. **Make your changes**
   - Follow code style guidelines
   - Add tests for new features
   - Update documentation
   - Ensure all tests pass

4. **Commit your changes**
```bash
git add .
git commit -m "feat: add new feature description"
```

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

5. **Push to your fork**
```bash
git push origin feature/your-feature-name
```

6. **Create Pull Request**
   - Go to GitHub and create a PR
   - Fill in the PR template
   - Link related issues
   - Request review

## Development Setup

### Backend Development

1. **Install dependencies:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

2. **Run tests:**
```bash
pytest
```

3. **Run linter:**
```bash
black app/
isort app/
flake8 app/
mypy app/
```

### Frontend Development

#### Dashboard

```bash
cd dashboard
npm install
npm run dev
npm run lint
npm run type-check
```

#### Extension

```bash
cd extension
npm install
npm run dev
npm run build
```

## Code Style Guidelines

### Python (Backend)

- Follow [PEP 8](https://pep8.org/)
- Use type hints
- Maximum line length: 100 characters
- Use Black for formatting
- Use isort for import sorting

Example:
```python
from typing import Dict, Any

async def scan_url(url: str, features: Dict[str, float]) -> Dict[str, Any]:
    """
    Scan URL for phishing indicators.
    
    Args:
        url: URL to scan
        features: Extracted URL features
        
    Returns:
        Scan result dictionary
    """
    # Implementation
    pass
```

### TypeScript (Dashboard/Extension)

- Follow [TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html)
- Use functional components with hooks
- Use TypeScript strict mode
- Maximum line length: 100 characters

Example:
```typescript
interface ScanResult {
  scan_id: string;
  is_phishing: boolean;
  phishing_score: number;
}

export async function scanUrl(url: string): Promise<ScanResult> {
  // Implementation
}
```

## Testing Guidelines

### Backend Tests

```python
import pytest
from app.services.feature_extractor import URLFeatureExtractor

def test_url_length_feature():
    extractor = URLFeatureExtractor()
    features = extractor.extract_features("https://example.com")
    assert features['url_length'] == 19
```

### Frontend Tests

```typescript
import { render, screen } from '@testing-library/react';
import Dashboard from './Dashboard';

test('renders dashboard title', () => {
  render(<Dashboard />);
  expect(screen.getByText('PhishGuard Dashboard')).toBeInTheDocument();
});
```

## Documentation

- Update README.md for user-facing changes
- Update API.md for API changes
- Add docstrings to all functions
- Include code examples
- Update CHANGELOG.md

## ML Model Contributions

### Adding New Features

1. Add feature extraction in `URLFeatureExtractor`
2. Update feature list in `MLInferenceService`
3. Retrain model with new features
4. Document feature in code and docs
5. Add tests for feature extraction

### Improving Model Performance

1. Experiment with new algorithms
2. Document results and metrics
3. Compare with baseline
4. Submit PR with performance comparison

## Security

### Reporting Security Issues

**DO NOT** create public issues for security vulnerabilities.

Email security concerns to: security@phishguard.com

Include:
- Description of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Security Best Practices

- Never commit secrets or API keys
- Use environment variables
- Validate all inputs
- Sanitize outputs
- Follow OWASP guidelines

## Review Process

1. **Automated Checks**
   - CI/CD pipeline runs tests
   - Linters check code style
   - Security scanners check for vulnerabilities

2. **Code Review**
   - At least one maintainer review required
   - Address all review comments
   - Keep discussions constructive

3. **Merge**
   - Squash commits if needed
   - Update CHANGELOG.md
   - Merge to main branch

## Release Process

1. Update version in `pyproject.toml` and `package.json`
2. Update CHANGELOG.md
3. Create release tag
4. Build and publish artifacts
5. Deploy to production

## Community

- Join our [Discord](https://discord.gg/phishguard)
- Follow us on [Twitter](https://twitter.com/phishguard)
- Read our [Blog](https://blog.phishguard.com)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to:
- Open a discussion on GitHub
- Ask in Discord
- Email: contribute@phishguard.com

Thank you for contributing to PhishGuard! 🛡️
