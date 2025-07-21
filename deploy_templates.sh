#!/bin/bash
# A script to create GitHub issue templates in the correct directory.

# Exit immediately if a command fails
set -e

# Define the target directory
TEMPLATE_DIR=".github/ISSUE_TEMPLATE"

# 1. Create the directory structure
echo "✅ Ensuring directory '$TEMPLATE_DIR' exists..."
mkdir -p "$TEMPLATE_DIR"

# 2. Create the Bug Report template
echo "📄 Creating bug_report.md..."
cat > "$TEMPLATE_DIR/bug_report.md" <<'EOF'
---
name: 🐛 Bug Report
about: Create a report to help us fix something that is broken.
title: "[BUG] "
labels: bug
---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Run script '...' with arguments '...'
3. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots or Logs**
If applicable, add screenshots or logs to help explain your problem.

**Environment:**
 - OS: [e.g. macOS, Windows, Linux]
 - Python Version: [e.g. 3.9]
 - Key Library Versions: [e.g. `torch==2.0`, `librosa==0.10.1`]

**Additional context**
Add any other context about the problem here.
EOF

# 3. Create the Feature Request template
echo "📄 Creating feature_request.md..."
cat > "$TEMPLATE_DIR/feature_request.md" <<'EOF'
---
name: ✨ Feature Request
about: Suggest a new idea, analysis technique, or feature for the project.
title: "[FEATURE] "
labels: enhancement
---

**Is your feature request related to a problem? Please describe.**
A clear description of the problem. Ex. "I'm always frustrated when..."

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
A clear description of any alternative solutions you've considered.

**Additional context**
Add any other context or mockups here.
EOF

# 4. Create the Documentation Issue template
echo "📄 Creating documentation.md..."
cat > "$TEMPLATE_DIR/documentation.md" <<'EOF'
---
name: 📚 Documentation Issue
about: Report an error or suggest an improvement in the documentation.
title: "[DOCS] "
labels: documentation
---

**Which part of the documentation is affected?**
Please provide a link to the section or the name of the file.

**Describe the issue**
A clear description of what is wrong or missing.

**Suggested improvement**
How do you think the documentation could be improved?
EOF

echo -e "\n🎉 Success! Templates deployed to '$TEMPLATE_DIR'."
echo "You can now commit the '.github' folder to your repository."