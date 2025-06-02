# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - 2025-05-31

### Fixed
- **MCP error -32000: Connection closed** when connecting from different directories
- Path resolution issues that prevented server from working outside project directory
- Environment file loading from relative paths
- Log file creation in wrong directory when server started remotely

### Added
- Automatic project root detection using `Path(__file__).parent.absolute()`
- Support for running MCP server from any directory
- `test_remote_connection.py` - automated test script for remote connections
- `REMOTE_CONNECTION_GUIDE.md` - comprehensive guide for remote connections
- Enhanced troubleshooting section in README.md

### Changed
- Environment file paths now resolve relative to project root instead of current working directory
- Log files are now always created in project directory regardless of startup location
- Improved error handling and path resolution throughout the codebase

### Technical Details
- Added `sys.path.insert(0, str(project_root))` to ensure proper module imports
- Modified `load_environment()` function to handle relative paths correctly
- Updated logging configuration to use absolute paths for log files
- All relative imports now work correctly from any directory

### Migration Notes
- No breaking changes for existing installations
- Server can now be referenced with absolute paths in MCP client configurations
- Existing relative path configurations will continue to work when run from project directory
