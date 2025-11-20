# Contributing to eThekwini ESRI GIS MCP

We welcome contributions to the eThekwini ESRI GIS MCP project! This document provides guidelines for contributing to the project.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct:

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain a professional environment

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Basic understanding of GIS concepts and ArcGIS REST API
- Familiarity with Model Context Protocol (MCP)

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/bonnie-mapipa/ethekwini-gis-mcp.git
   cd ethekwini-gis-mcp
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run tests to ensure everything works**
   ```bash
   python tests/test_mcp_server.py
   ```

## How to Contribute

### Reporting Issues

Before creating an issue, please:

1. Check if the issue already exists in our [issue tracker](https://github.com/bonnie-mapipa/ethekwini-gis-mcp/issues)
2. Use the appropriate issue template
3. Provide clear reproduction steps
4. Include relevant logs and error messages

### Suggesting Features

We welcome feature suggestions! Please:

1. Open a new issue with the "feature request" label
2. Describe the feature and its benefits clearly
3. Consider implementation complexity and maintainability
4. Discuss with maintainers before starting major features

### Submitting Changes

#### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the coding standards (see below)
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   python tests/test_mcp_server.py
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: brief description of your changes"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a pull request**
   - Use a clear, descriptive title
   - Fill out the pull request template
   - Link related issues
   - Add screenshots/examples if applicable

#### Commit Message Guidelines

Use clear, descriptive commit messages:

- **Add**: New features or functionality
- **Fix**: Bug fixes
- **Update**: Changes to existing functionality
- **Remove**: Removing code or features
- **Docs**: Documentation updates
- **Test**: Adding or updating tests
- **Refactor**: Code refactoring without functional changes

Examples:
```
Add: new tool for querying municipal boundaries
Fix: handle timeout errors in dataset discovery
Update: improve error messages for invalid queries
Docs: add examples for spatial query usage
```

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use meaningful variable and function names
- Add docstrings to all public functions and classes
- Keep functions focused and concise

### Code Organization

- **src/**: Main source code
- **tests/**: Test files
- **examples/**: Usage examples
- **docs/**: Documentation files

### Documentation

- Update README.md for new features
- Add docstrings for new functions/classes
- Include usage examples
- Update API documentation

### Testing

- Write tests for new functionality
- Ensure existing tests continue to pass
- Include both positive and negative test cases
- Test error handling and edge cases

## Development Guidelines

### Adding New Tools

When adding new MCP tools:

1. Follow the existing tool pattern in `src/ethekwini_gis_mcp.py`
2. Add comprehensive error handling
3. Include parameter validation
4. Add tests in `tests/test_mcp_server.py`
5. Update documentation

### Working with GIS Data

- Handle different coordinate systems appropriately
- Validate spatial queries and parameters
- Consider performance implications of large datasets
- Test with real eThekwini data when possible

### Error Handling

- Use descriptive error messages
- Handle network timeouts gracefully
- Provide fallback options where appropriate
- Log errors appropriately

## Release Process

### Version Numbers

We use [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. Update version numbers in `pyproject.toml` and `package.json`
2. Update CHANGELOG.md with new features and fixes
3. Run full test suite
4. Create release notes
5. Tag the release

## Community

### Getting Help

- Check the [documentation](README.md)
- Search [existing issues](https://github.com/your-username/ethekwini-gis-mcp/issues)
- Ask questions in new issues with the "question" label

### Communication

- Be respectful and professional
- Focus on technical merit
- Provide constructive feedback
- Help others when possible

## Recognition

We appreciate all contributions! Contributors will be:

- Listed in the project README
- Mentioned in release notes
- Credited in commit history

Thank you for contributing to the eThekwini ESRI GIS MCP project!