"""``doc/conf.py`` 的原子化分组。

每个模块只承担一类配置，``conf.py`` 按依赖顺序再导出。新增配置时先判断归属：
项目元信息 → ``meta``；主题与静态资源 → ``appearance``；扩展装载 → ``extensions``；
MyST 与交叉引用 → ``myst``；``setup()`` 与守卫 → ``guard``。
"""
