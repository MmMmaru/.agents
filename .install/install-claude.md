需要创建~/.claude/CLAUDE.md，并写入
```markdown
@~/.agents/AGENTS.md
```

使用文件链接~/.agents/skills到~/.claude/skills

修改~/.claude/settings.json，添加
{
  "permissions": {
    "defaultMode": "bypassPermissions"
  }
}