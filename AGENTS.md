## 语言设置
使用中文编写文档。

## powershell使用技巧
使用英文注释，中文会乱码
使用Get-Content xxx -Encoding UTF8 以避免乱码

## 先了解整个项目
首先阅读文档了解项目、数据格式、接口定义
即时修正文档

## 论文
论文中的修改不需要做commit

## 工作规范
安装/配置类任务不需要commit/记录PROGRESS.md。
代码/实验/环境变更需要commit并记录。

### 实施前先思考
如果有什么不清晰的，请直接问我。

#### 具体规则
- 编写脚本的时候不需要做测试
- 不要过度封装(每个函数封装不超过三层：三层抽象后最多使用底层库进行调用)
- 单个文件代码行数不要超过600行。
- 所有CLI使用default做默认赋值
- 脚本通过文件方式启动，用sys.path[0] = os.getcwd()保证当前路径为根目录
- 对于每个类和函数编写清晰的注释！

### 文件规范
- 所有临时文件放在.temp文件夹内
- 所有log文件放在.log文件夹内
- 单次使用的分析、数据脚本不做保留，用后删除

#### Type Hint
函数参数需要严格的类型注解，返回值注解：比如：hfss: Hfss。

### git规范
无需询问，在修改完成后commit（计划不需要）
提交规范优先参考项目的CONTRIBUTING.md，否则使用：
fix: xx
feat: xx
exp: xx
chore: xx
docs: xx

## 进度记录
如果你更改了系统环境、请你修改项目 AGENTS.md。
在完成一步修改后在 PROGRESS.md 中进行进展记录，格式：
```markdown
### MM-DD hh:mm
<修改/配置/实验记录>
```

## Cloudflare 工具偏好
与 Cloudflare 交互时优先使用 cf CLI；如果项目已有 Wrangler 配置文件，则保留 Wrangler 的开发、构建与部署流程。

