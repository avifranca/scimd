# Contributing to SciMD

SciMD was created by **Juan Francisco Avilés Calderón**.

Thank you for your interest in SciMD. This project exists to serve the
scientific community, and contributions from researchers, developers, and
anyone who cares about accessible knowledge are welcome.

## Ways to Contribute

### For Researchers
- **Write example documents** in your field using the `.smd` format
- **Review the specification** for gaps in your discipline's needs
- **Test with your workflow** and report friction points

### For Developers
- **Improve the parser** — add edge case handling, optimize performance
- **Build integrations** — VS Code extension, Pandoc filter, Jupyter plugin
- **Write tests** — the parser needs comprehensive test coverage
- **Build converters** — PDF→SciMD, LaTeX→SciMD, DOCX→SciMD

### For Everyone
- **Report bugs** via GitHub Issues
- **Suggest features** via GitHub Discussions
- **Improve documentation** — especially translations

## Development Setup

```bash
git clone https://github.com/scimd/scimd.git
cd scimd
pip install -r parser/requirements.txt
python parser/scimd_parser.py examples/full-paper.smd
python parser/scimd_validator.py examples/full-paper.smd
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Run the validator against all examples
5. Submit a PR with a clear description

## Specification Changes

Changes to the specification (`spec/SPECIFICATION.md`) require:

1. An RFC issue describing the proposed change
2. Community discussion period (minimum 2 weeks)
3. At least 2 approvals from maintainers
4. Backward compatibility analysis

## Code of Conduct

Be kind. Be constructive. Remember that this project serves science.

## License

By contributing, you agree that your contributions will be licensed under
the MIT License.
