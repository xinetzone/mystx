"""作者个人专属的站点取值：社交账号链接与 intersphinx 源偏好。

边界：

* 本模块是**作者身份**的可复用取值，跨项目稳定；本站画像（``doc/conf.py``）
  只负责把它们组装进去，不复制内容；
* 取值按调用新建：同一进程内多次装配互不共享容器，扩展就地改写列表或字典时
  不会波及另一份装配；
* 不从包门面导出——它是个人配置，不是库的公共预设。
"""


def icon_links() -> list[dict[str, str]]:
    """返回作者各平台的图标链接（侧栏 ``icon_links`` 取值）。"""
    return [
        {
            "name": "知乎",
            "url": "https://www.zhihu.com/people/xinetzone",
            "icon": "fa-brands fa-zhihu",
            "type": "fontawesome",
        },
        {
            "name": "简书",
            "url": "https://www.jianshu.com/u/4302480a3e8e",
            "icon": "fa-solid fa-book",
            "type": "fontawesome",
        },
        {
            "name": "B站",
            "url": "https://space.bilibili.com/252192181",
            "icon": "fa-brands fa-bilibili",
            "type": "fontawesome",
        },
        {
            "name": "博客园",
            "url": "https://www.cnblogs.com/q735613050/",
            "icon": "https://xinetzone.github.io/xinetzone/media/xinetzone.jpg",
            "type": "url",
        },
        {
            "name": "领英",
            "url": "https://www.linkedin.com/in/xinet",
            "icon": "fa-brands fa-linkedin",
            "type": "fontawesome",
        },
    ]


def intersphinx_mapping() -> dict[str, tuple[str, str | None]]:
    """返回作者的 intersphinx 源表，含本地清单缓存偏好。

    第二项给本地清单文件名（相对 srcdir）：``docs.python.org`` 的 TLS 握手
    实测约 40s，取回一次后落盘复用；Python 版本升级时重新下载
    ``_inv/python.inv``。
    """
    return {
        "python": ("https://docs.python.org/3.14", "_inv/python.inv"),
        "sphinx": ("https://daobook.github.io/sphinx/", None),
        "pst": ("https://daobook.github.io/pydata-sphinx-theme/", None),
        "sbt": ("https://daobook.github.io/sphinx-book-theme/", None),
        "myst-nb": ("https://daobook.github.io/MyST-NB/", None),
        "myst-parser": ("https://daobook.github.io/MyST-Parser/", None),
    }
