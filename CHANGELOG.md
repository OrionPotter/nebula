# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- 项目结构调整，将核心模块移至`stock_analyzer.core`
- 工具模块移至`stock_analyzer.utils`
- 添加了完整的中文文档和注释
- 所有接口功能测试通过

### Changed
- 包名从`nebula`更改为`stock_analyzer`
- 更新了所有模块的导入路径
- 修复了文件中的中文乱码问题
- 更新了README.md中的使用示例

### Fixed
- 修复了indicators.py模块中的中文乱码
- 修正了所有模块间的导入语句

## [0.1.0] - 2025-09-20

### Added
- Initial release of stock_analyzer
- Real-time stock quote functionality
- Historical data retrieval (daily/weekly/monthly/minute)
- Technical indicators calculation (EMA, SMA, KDJ, RSI, MACD)
- Board information retrieval
- Hot stock rankings
- Stock fundamentals information
- Cache management with Redis support
- Database integration with SQLite