"""
Atlas CI/CD Auto-Fixer Agent - Main Entry Point
Safety-first autonomous workflow error detection and self-healing
"""

import argparse
import sys
from pathlib import Path

def main():
    """Main entry point for Atlas agent"""
    parser = argparse.ArgumentParser(
        description="Atlas CI/CD Auto-Fixer Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  atlas propose --error-log error.txt       # Generate patch proposal
  atlas verify --patch patch.diff           # Verify patch in worktree
  atlas apply --patch patch.diff            # Apply verified patch
  atlas rollback --commit abc123            # Rollback applied patch
  atlas ui                                   # Launch Streamlit UI
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Atlas commands')
    
    # Propose command
    propose_parser = subparsers.add_parser('propose', help='Generate patch proposal from error logs')
    propose_parser.add_argument('--error-log', required=True, help='Path to error log file')
    propose_parser.add_argument('--output', default='suggested_patch.diff', help='Output patch file')
    propose_parser.add_argument('--dry-run', action='store_true', help='Generate proposal without saving')
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify patch in isolated worktree')
    verify_parser.add_argument('--patch', required=True, help='Path to patch file')
    verify_parser.add_argument('--repo-path', default='.', help='Target repository path')
    
    # Apply command
    apply_parser = subparsers.add_parser('apply', help='Apply verified patch to Master')
    apply_parser.add_argument('--patch', required=True, help='Path to verified patch file')
    apply_parser.add_argument('--force', action='store_true', help='Skip safety confirmation')
    
    # Rollback command
    rollback_parser = subparsers.add_parser('rollback', help='Rollback applied patch')
    rollback_parser.add_argument('--commit', required=True, help='Commit hash to revert')
    rollback_parser.add_argument('--reason', required=True, help='Rollback reason')
    
    # UI command
    ui_parser = subparsers.add_parser('ui', help='Launch Streamlit UI')
    ui_parser.add_argument('--port', type=int, default=8501, help='UI port (default: 8501)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Import and dispatch commands
    if args.command == 'propose':
        from atlas_core.tools.generate_patch import propose_patch
        propose_patch(args.error_log, args.output, args.dry_run)
    
    elif args.command == 'verify':
        from atlas_core.agents.prometheus import verify_patch
        verify_patch(args.patch, args.repo_path)
    
    elif args.command == 'apply':
        from atlas_core.agents.hephaestus import apply_patch
        apply_patch(args.patch, args.force)
    
    elif args.command == 'rollback':
        from atlas_core.agents.janus import rollback_patch
        rollback_patch(args.commit, args.reason)
    
    elif args.command == 'ui':
        from atlas_core.ui.streamlit.streamlit_app import launch_ui
        launch_ui(args.port)

if __name__ == '__main__':
    main()
