# Contributing

Thank you for considering contributing to hier-config-api! This document provides guidelines for contributions.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## How to Contribute

### Reporting Bugs

Open an issue on [GitHub Issues](https://github.com/netdevops/hier-config-api/issues) with:

- Clear title and description
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS, etc.)
- Code samples or logs if applicable

### Suggesting Features

Open an issue with:

- Clear description of the feature
- Use cases and benefits
- Potential implementation approach
- Examples of similar features

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following our guidelines
4. Add tests for new functionality
5. Ensure all tests pass
6. Run linters and formatters
7. Commit with clear messages
8. Push to your fork
9. Open a Pull Request

## Development Guidelines

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings (Google style)
- Keep functions focused and small
- Use meaningful variable names

### Testing

- Write tests for all new code
- Maintain >80% coverage
- Test both success and error cases
- Use fixtures for common test data

### Documentation

- Update relevant documentation
- Add docstrings to new functions
- Include code examples where helpful
- Update changelog

### Commit Messages

Use conventional commits format:

```
type(scope): subject

body (optional)

footer (optional)
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `style`: Formatting
- `chore`: Maintenance

Examples:
```
feat(api): add configuration validation endpoint
fix(parser): handle empty configuration files
docs(api): update remediation examples
```

## Review Process

1. Automated checks must pass (CI/CD)
2. At least one maintainer review required
3. Address review comments
4. Squash commits if requested
5. Maintainer merges when ready

## Release Process

Releases follow semantic versioning (MAJOR.MINOR.PATCH):

- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

## Getting Help

- Open a [Discussion](https://github.com/netdevops/hier-config-api/discussions) for questions
- Check existing [Issues](https://github.com/netdevops/hier-config-api/issues)
- Review the [Development Guide](development.md)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
