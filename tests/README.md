# 自动化测试框架使用指南

## 📋 目录结构

```
tests/
├── __init__.py              # 包初始化
├── conftest.py              # pytest配置和fixtures
├── test_api.py              # 后端API自动化测试
├── test_ui.py               # 前端UI自动化测试
├── test_performance.py      # 性能测试脚本
├── test_files/              # 测试文件存储目录（自动生成）
└── README.md                # 本文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 基础测试依赖
pip install pytest requests python-docx

# UI测试依赖（可选）
pip install playwright
playwright install chromium

# 性能测试增强（可选）
pip install locust
```

### 2. 启动应用

在运行测试前，确保应用已启动：

```bash
# 启动后端（终端1）
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动前端（终端2）
streamlit run app.py
```

### 3. 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 仅运行API测试
pytest tests/test_api.py -v

# 仅运行UI测试
pytest tests/test_ui.py -v

# 仅运行性能测试
pytest tests/test_performance.py -v

# 运行快速测试（跳过耗时测试）
pytest tests/ -v -m "not slow"

# 生成测试报告
pytest tests/ -v --html=report.html --self-contained-html
```

## 📊 测试类型说明

### API测试 (test_api.py)

**测试内容**:
- ✅ 健康检查端点
- ✅ 用户认证流程
- ✅ 文档转换接口
- ✅ 支付订单流程
- ✅ 用户反馈功能
- ✅ 异常处理（无效输入、缺失参数等）

**运行示例**:
```bash
# 运行所有API测试
pytest tests/test_api.py -v

# 运行特定测试类
pytest tests/test_api.py::TestHealthCheck -v

# 运行特定测试方法
pytest tests/test_api.py::TestHealthCheck::test_health_endpoint -v -s
```

**预期输出**:
```
tests/test_api.py::TestHealthCheck::test_health_endpoint PASSED
tests/test_api.py::TestUsers::test_create_user_normal PASSED
tests/test_api.py::TestConversions::test_full_conversion_workflow PASSED
...
========================= 15 passed in 45.2s =========================
```

---

### UI测试 (test_ui.py)

**测试内容**:
- ✅ 页面加载和渲染
- ✅ 文件上传功能
- ✅ 表单交互
- ✅ 响应式布局
- ✅ 错误提示显示
- ✅ 完整用户工作流

**前置要求**:
```bash
# 安装Playwright
pip install playwright
playwright install chromium
```

**运行示例**:
```bash
# 运行所有UI测试（无头模式）
pytest tests/test_ui.py -v

# 查看浏览器操作过程（有头模式）
# 修改 test_ui.py 中的 headless=False

# 运行特定测试
pytest tests/test_ui.py::TestFrontendUI::test_homepage_loads -v -s
```

**注意事项**:
- UI测试需要前端应用正在运行
- 默认使用无头模式（不显示浏览器窗口）
- 如需调试，可设置 `headless=False` 查看实际操作过程

---

### 性能测试 (test_performance.py)

**测试内容**:
- ✅ API响应时间测量
- ✅ 并发用户负载测试
- ✅ 持续压力测试
- ✅ 文档转换性能
- ✅ 数据库操作性能

**运行示例**:
```bash
# 运行所有性能测试（包含耗时测试）
pytest tests/test_performance.py -v -s

# 仅运行快速性能测试
pytest tests/test_performance.py -v -m "not slow"

# 运行压力测试
pytest tests/test_performance.py::TestAPIPerformance::test_sustained_load_performance -v -s
```

**性能指标参考**:
- API响应时间: < 1秒（平均）
- 并发成功率: > 90%
- 小文件转换: < 30秒
- 页面加载时间: < 5秒

---

## 🔧 配置选项

### 环境变量

创建 `.env.test` 文件（可选）:

```bash
# 后端API地址
BACKEND_URL=http://localhost:8000

# 前端应用地址
FRONTEND_URL=http://localhost:8501

# 测试超时时间（秒）
TEST_TIMEOUT=30
```

### pytest.ini 配置

在项目根目录创建 `pytest.ini`:

```ini
[pytest]
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    smoke: marks tests as smoke tests

testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
```

---

## 📈 测试报告

### 生成HTML报告

```bash
# 安装插件
pip install pytest-html

# 生成报告
pytest tests/ --html=report.html --self-contained-html
```

### 生成JUnit XML报告（用于CI/CD）

```bash
pytest tests/ --junitxml=test-results.xml
```

### 覆盖率报告

```bash
# 安装插件
pip install pytest-cov

# 生成覆盖率报告
pytest tests/ --cov=backend/app --cov-report=html
```

---

## 🐛 故障排查

### 问题1: 测试连接失败

**症状**: `ConnectionRefusedError`

**解决**:
```bash
# 确认后端是否运行
curl http://localhost:8000/health

# 确认前端是否运行
curl http://localhost:8501
```

### 问题2: UI测试找不到元素

**症状**: `TimeoutError: Locator expected to be visible`

**解决**:
1. 检查前端是否正常启动
2. 增加超时时间: `page.goto(url, timeout=60000)`
3. 使用有头模式调试: `headless=False`

### 问题3: 性能测试结果不稳定

**原因**: 系统负载波动

**解决**:
1. 多次运行取平均值
2. 在空闲时段运行测试
3. 关闭其他占用资源的程序

---

## 🎯 最佳实践

### 1. 定期运行测试

```bash
# 每天运行快速测试
pytest tests/ -v -m "not slow"

# 每周运行完整测试套件
pytest tests/ -v
```

### 2. CI/CD集成

在 `.github/workflows/test.yml` 中添加:

```yaml
name: Run Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest playwright
          playwright install chromium
      - name: Start backend
        run: cd backend && uvicorn app.main:app &
      - name: Start frontend
        run: streamlit run app.py &
      - name: Wait for services
        run: sleep 10
      - name: Run tests
        run: pytest tests/ -v --junitxml=test-results.xml
```

### 3. 测试数据隔离

每个测试应独立，不依赖其他测试的状态。使用fixture创建测试数据：

```python
@pytest.fixture
def test_user(base_url):
    user_id = f"test_{int(time.time())}"
    requests.post(f"{base_url}/api/users/", json={"user_id": user_id})
    yield user_id
    # 清理（可选）
    # requests.delete(f"{base_url}/api/users/{user_id}")
```

---

## 📝 添加新测试

### 添加API测试

在 `test_api.py` 中添加:

```python
class TestNewFeature:
    def test_new_endpoint(self, base_url):
        response = requests.get(f"{base_url}/api/new-feature")
        assert response.status_code == 200
```

### 添加UI测试

在 `test_ui.py` 中添加:

```python
def test_new_feature_ui(self, browser_context, frontend_url):
    page = browser_context
    page.goto(frontend_url)
    # 测试新功能的UI
```

### 添加性能测试

在 `test_performance.py` 中添加:

```python
def test_new_feature_performance(self, base_url):
    start = time.time()
    # 执行操作
    elapsed = time.time() - start
    assert elapsed < 1.0  # 性能要求
```

---

## 📞 获取帮助

- 查看pytest文档: https://docs.pytest.org/
- Playwright文档: https://playwright.dev/python/
- 项目Issues: 提交测试相关问题

---

**最后更新**: 2026-05-07
**维护者**: Lingma AI Assistant
