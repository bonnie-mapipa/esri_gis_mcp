name: Pull Request
description: Submit a pull request to contribute code changes
body:
  - type: markdown
    attributes:
      value: |
        Thanks for contributing to eThekwini ESRI GIS MCP! Please fill out this template to help us review your changes.

  - type: textarea
    id: description
    attributes:
      label: Description
      description: Describe what this pull request does
      placeholder: Brief description of the changes...
    validations:
      required: true

  - type: dropdown
    id: change-type
    attributes:
      label: Type of Change
      description: What type of change does this PR introduce?
      options:
        - Bug fix (non-breaking change that fixes an issue)
        - New feature (non-breaking change that adds functionality)
        - Breaking change (fix or feature that would cause existing functionality to not work as expected)
        - Documentation update
        - Code refactoring
        - Performance improvement
        - Test improvements
    validations:
      required: true

  - type: textarea
    id: related-issues
    attributes:
      label: Related Issues
      description: Link any related issues
      placeholder: Fixes #123, Addresses #456

  - type: textarea
    id: changes-made
    attributes:
      label: Changes Made
      description: List the specific changes made in this PR
      placeholder: |
        - Added new tool for...
        - Fixed issue with...
        - Updated documentation for...
    validations:
      required: true

  - type: textarea
    id: testing
    attributes:
      label: Testing
      description: Describe how you tested these changes
      placeholder: |
        - Ran test suite: `python tests/test_mcp_server.py`
        - Manually tested with datasets: ...
        - Verified MCP client integration: ...
    validations:
      required: true

  - type: checkboxes
    id: checklist
    attributes:
      label: Checklist
      description: Please check all applicable items
      options:
        - label: I have read the contributing guidelines
          required: true
        - label: I have tested my changes thoroughly
          required: true
        - label: I have added/updated tests for my changes
          required: false
        - label: I have updated documentation as needed
          required: false
        - label: My code follows the project coding standards
          required: true
        - label: All existing tests still pass
          required: true

  - type: textarea
    id: additional-notes
    attributes:
      label: Additional Notes
      description: Any additional information about this PR
      placeholder: Special considerations, deployment notes, etc.