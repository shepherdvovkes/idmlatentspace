#!/bin/bash

# Synthesizer Performance Analyzer - File Organization Script
# This script organizes files according to the README.md project structure

set -e  # Exit on any error

echo "🎵 Synthesizer Performance Analyzer - File Organization Script"
echo "============================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_action() {
    echo -e "${BLUE}[ACTION]${NC} $1"
}

# Create the main directory structure
create_directories() {
    print_status "Creating directory structure..."
    
    # Main directories from README.md structure
    mkdir -p AbletonProjects
    mkdir -p Samples
    mkdir -p sysex-toolkit/sysex_toolkit
    mkdir -p sysex-toolkit/examples
    mkdir -p sysex-toolkit/tests
    mkdir -p results
    mkdir -p cache
    
    print_status "Directory structure created successfully!"
}

# Move MIDI files to AbletonProjects
organize_midi_files() {
    print_status "Organizing MIDI files..."
    
    # Find and move any .mid files that aren't already in AbletonProjects
    if ls *.mid 2>/dev/null; then
        for midi_file in *.mid; do
            if [[ -f "$midi_file" ]]; then
                print_action "Moving $midi_file to AbletonProjects/"
                mv "$midi_file" AbletonProjects/
            fi
        done
    else
        print_warning "No MIDI files found in root directory"
    fi
    
    # Check for Ableton Live project files
    if ls *.als 2>/dev/null; then
        for als_file in *.als; do
            if [[ -f "$als_file" ]]; then
                print_action "Moving Ableton project $als_file to AbletonProjects/"
                mv "$als_file" AbletonProjects/
            fi
        done
    fi
}

# Organize SysEx files
organize_sysex_files() {
    print_status "Organizing SysEx files..."
    
    # Move .syx files to sysex-toolkit/examples (if they're not toolkit source files)
    if ls *.syx 2>/dev/null; then
        for sysex_file in *.syx; do
            if [[ -f "$sysex_file" ]]; then
                print_action "Moving $sysex_file to sysex-toolkit/examples/"
                mv "$sysex_file" sysex-toolkit/examples/
            fi
        done
    fi
    
    # Move related SysEx text files
    if ls *.txt 2>/dev/null; then
        for txt_file in *.txt; do
            if [[ "$txt_file" == *"preset"* ]] || [[ "$txt_file" == *"sysex"* ]]; then
                print_action "Moving $txt_file to sysex-toolkit/examples/"
                mv "$txt_file" sysex-toolkit/examples/
            fi
        done
    fi
}

# Organize analysis and data files
organize_data_files() {
    print_status "Organizing data and analysis files..."
    
    # Create results subdirectory
    mkdir -p results/analysis
    mkdir -p results/reports
    
    # Move JSON analysis files
    if ls *analysis*.json 2>/dev/null; then
        for json_file in *analysis*.json; do
            if [[ -f "$json_file" ]]; then
                print_action "Moving $json_file to results/analysis/"
                mv "$json_file" results/analysis/
            fi
        done
    fi
    
    # Move other JSON data files
    for json_file in *.json; do
        if [[ -f "$json_file" ]] && [[ "$json_file" != *"package.json"* ]]; then
            print_action "Moving $json_file to results/analysis/"
            mv "$json_file" results/analysis/
        fi
    done
    
    # Move CSV files (analysis results)
    if ls *.csv 2>/dev/null; then
        for csv_file in *.csv; do
            if [[ -f "$csv_file" ]]; then
                print_action "Moving $csv_file to results/analysis/"
                mv "$csv_file" results/analysis/
            fi
        done
    fi
    
    # Move report files
    if ls *report*.txt 2>/dev/null; then
        for report_file in *report*.txt; do
            if [[ -f "$report_file" ]]; then
                print_action "Moving $report_file to results/reports/"
                mv "$report_file" results/reports/
            fi
        done
    fi
    
    # Move other analysis text files
    if ls cc_automation_report.txt 2>/dev/null; then
        print_action "Moving cc_automation_report.txt to results/reports/"
        mv cc_automation_report.txt results/reports/
    fi
}

# Organize development and build files
organize_dev_files() {
    print_status "Organizing development files..."
    
    # Keep main Python files in root (as per README structure)
    print_status "Main Python files are already in correct location:"
    for py_file in main.py pipeline.py gui.py data_processor.py model.py utils.py apa.py audio_ml_analyzer.py preset_differential_analyzer.py; do
        if [[ -f "$py_file" ]]; then
            echo "  ✓ $py_file"
        fi
    done
    
    # Move debug files to a separate directory
    mkdir -p debug
    if ls debug*.py 2>/dev/null; then
        for debug_file in debug*.py; do
            if [[ -f "$debug_file" ]]; then
                print_action "Moving $debug_file to debug/"
                mv "$debug_file" debug/
            fi
        done
    fi
    
    # Move package creation script to a tools directory
    mkdir -p tools
    if [[ -f "package_creator_script.sh" ]]; then
        print_action "Moving package_creator_script.sh to tools/"
        mv package_creator_script.sh tools/
    fi
    
    if [[ -f "package_files.py" ]]; then
        print_action "Moving package_files.py to tools/"
        mv package_files.py tools/
    fi
    
    if [[ -f "updated_preset_analyzer.py" ]]; then
        print_action "Moving updated_preset_analyzer.py to tools/"
        mv updated_preset_analyzer.py tools/
    fi
}

# Organize documentation files
organize_docs() {
    print_status "Organizing documentation..."
    
    # Keep README.md in root as expected
    if [[ -f "README.md" ]]; then
        echo "  ✓ README.md is in correct location"
    fi
    
    # Move PDF files to docs directory
    mkdir -p docs
    if ls *.pdf 2>/dev/null; then
        for pdf_file in *.pdf; do
            if [[ -f "$pdf_file" ]]; then
                print_action "Moving $pdf_file to docs/"
                mv "$pdf_file" docs/
            fi
        done
    fi
}

# Set appropriate permissions
set_permissions() {
    print_status "Setting file permissions..."
    
    # Make Python files executable if they have main functions
    for py_file in main.py pipeline.py; do
        if [[ -f "$py_file" ]]; then
            chmod +x "$py_file"
            print_action "Made $py_file executable"
        fi
    done
    
    # Make shell scripts executable
    if [[ -f "tools/package_creator_script.sh" ]]; then
        chmod +x tools/package_creator_script.sh
        print_action "Made tools/package_creator_script.sh executable"
    fi
    
    # Set read permissions for data files
    find results/ -type f -name "*.json" -o -name "*.csv" -o -name "*.txt" | xargs chmod 644 2>/dev/null || true
    find AbletonProjects/ -type f -name "*.mid" -o -name "*.als" | xargs chmod 644 2>/dev/null || true
    find sysex-toolkit/examples/ -type f -name "*.syx" -o -name "*.txt" | xargs chmod 644 2>/dev/null || true
}

# Verify the organization
verify_structure() {
    print_status "Verifying project structure..."
    
    echo ""
    echo "📁 Final Project Structure:"
    echo "=========================="
    
    # Use tree if available, otherwise use find
    if command -v tree &> /dev/null; then
        tree -I '.git|__pycache__|*.pyc' --dirsfirst
    else
        echo "📁 synthesizer-performance-analyzer/"
        find . -type d -not -path "./.git*" -not -path "./__pycache__*" | sort | sed 's/^/  /'
        echo ""
        echo "Key files in root:"
        ls -la *.py *.yaml *.md 2>/dev/null | grep "^-" | awk '{print "  " $9}' || true
    fi
    
    echo ""
    print_status "Organization complete! ✨"
    echo ""
    echo "Next steps:"
    echo "1. Run: python main.py (for GUI)"
    echo "2. Run: python pipeline.py (for command line analysis)"
    echo "3. Place your MIDI files in AbletonProjects/"
    echo "4. Configure settings in config.yaml"
}

# Main execution
main() {
    echo "Starting file organization..."
    echo ""
    
    # Check if we're in the right directory
    if [[ ! -f "README.md" ]]; then
        print_error "README.md not found. Please run this script from the project root directory."
        exit 1
    fi
    
    # Create backup of current state
    print_status "Creating backup of current file locations..."
    mkdir -p .backup
    ls -la > .backup/file_list_before_organization.txt
    
    # Execute organization steps
    create_directories
    organize_midi_files
    organize_sysex_files
    organize_data_files
    organize_dev_files
    organize_docs
    set_permissions
    
    # Create final file list
    ls -la > .backup/file_list_after_organization.txt
    
    verify_structure
    
    echo ""
    print_status "File organization completed successfully! 🎉"
    print_warning "Backup of original file locations saved in .backup/"
}

# Run the main function
main "$@"