# 贡献指南

感谢您对 mystx 项目的关注！我们欢迎各种形式的贡献，包括但不限于 bug 修复、功能增强、文档改进等。

## 开发环境设置

### 1. 克隆仓库

首先，克隆项目仓库到您的本地机器：

```bash
# 使用 HTTPS
git clone https://github.com/xinetzone/mystx.git
# 或者使用 SSH
# git clone git@github.com:xinetzone/mystx.git

# 进入项目目录
cd mystx
```

### 2. 安装开发依赖

项目使用 PDM 作为构建后端，您可以安装开发依赖进行主题开发：

```bash
# 安装开发依赖
pip install -e "[dev]"

# 安装文档构建依赖
pip install -e "[doc]"
```

## 开发流程

### 1. 创建分支

在开始开发前，请创建一个新的分支：

```bash
# 从 main 分支创建新分支
git checkout -b feature/your-feature-name
# 或者用于修复 bug
# git checkout -b fix/your-bugfix-name
```

### 2. 编写代码

请遵循以下代码规范：

- 确保代码风格与项目一致
- 添加适当的文档字符串和注释
- 确保新功能有足够的测试覆盖

### 3. 测试您的更改

在提交代码前，请确保您的更改通过了所有测试：

```bash
# 构建文档进行测试
cd doc
sphinx-build -b html . _build/html
```

### 4. 提交更改

使用清晰的提交信息描述您的更改：

```bash
# 添加您的更改
git add .

# 提交更改
git commit -m "简明扼要的提交信息"
```

提交信息应简洁明了，描述更改的内容和原因。

### 5. 推送到远程仓库

将您的更改推送到远程仓库：

```bash
# 推送到远程仓库
git push origin feature/your-feature-name
```

### 6. 创建 Pull Request

在 GitHub 上创建一个新的 Pull Request，描述您的更改内容和目的。

## 报告问题

如果您发现了 bug 或者有新功能的建议，请在 GitHub Issues 页面创建一个新的 issue：

1. 确保 issue 尚未被报告
2. 使用清晰的标题和详细的描述
3. 对于 bug 报告，请包含复现步骤和预期行为
4. 如果可能，附上相关的截图或错误信息

## 代码规范

- 遵循 Python PEP 8 代码风格指南
- 为所有公共函数和类添加文档字符串
- 使用类型提示提高代码可读性
- 确保测试覆盖关键功能

## 文档贡献

文档改进也是非常重要的贡献：

- 修正拼写或语法错误
- 改进现有文档的清晰度
- 添加缺失的文档
- 提供使用示例

## 行为准则

请尊重所有贡献者，保持友好和建设性的交流。

## 许可证

通过向本项目贡献代码，您同意您的贡献将在项目的许可证（Apache License 2.0）下发布。

感谢您的贡献！