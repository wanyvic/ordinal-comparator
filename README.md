# Ordinal Comparator

比较不同Ordinal和BRC20索引器实现的工具。支持比特币和Fractal区块链。

## 功能特点

- 比较不同索引器的区块收据以识别差异
- 支持Ordinal铭文和BRC20代币协议
- 支持比特币和Fractal区块链
- 多线程并行处理提高效率
- 优雅的错误处理和中断恢复

## 安装

```bash
# 从源代码安装
git clone https://github.com/yourusername/ordinal-comparator.git
cd ordinal-comparator
pip install -e .
```

## 用法

```bash
# 基本用法
ordinal-comparator -p https://primary-indexer.com -s https://secondary-indexer.com -m ordinal -c bitcoin

# 使用自定义块范围
ordinal-comparator -p https://primary-indexer.com -s https://secondary-indexer.com -m brc20 -c bitcoin --start-block 780000 --end-block 785000

# 调整并发工作线程数
ordinal-comparator -p https://primary-indexer.com -s https://secondary-indexer.com -m ordinal -c bitcoin --threads 50

# 使用详细日志记录
ordinal-comparator -p https://primary-indexer.com -s https://secondary-indexer.com -m brc20 -c bitcoin --log-level DEBUG --log-file comparison.log
```

## 命令行参数

**必需参数:**
- `-p, --primary-endpoint`: 主索引器URL（作为参考）
- `-s, --secondary-endpoint`: 次要索引器URL（用于验证）
- `-m, --protocol`: 要比较的协议（ORDINAL或BRC20）
- `-c, --chain`: 要比较的区块链（BITCOIN或FRACTAL）

**可选参数:**
- `--start-block`: 起始区块高度（默认：每个协议的首个有效区块）
- `--end-block`: 结束区块高度（默认：两个节点共同的最新区块）
- `--threads`: 并发工作线程数（默认：100）
- `--log-level`: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- `--log-file`: 日志文件路径（默认：输出到控制台）

## 项目结构

```
ordinal_comparator/
├── api/            # API客户端
├── cli/            # 命令行界面
├── core/           # 核心功能
├── protocols/      # 协议特定实现
└── utils/          # 工具函数
```

## 贡献

欢迎贡献！请随时提交问题或拉取请求。

## 许可证

MIT 