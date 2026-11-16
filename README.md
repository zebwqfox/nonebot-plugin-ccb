<div align="center">
  <a href="https://nonebot.dev/store/plugins"><img src="https://raw.githubusercontent.com/A-kirami/nonebot-plugin-template/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://raw.githubusercontent.com/A-kirami/nonebot-plugin-template/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-ccb

_✨ 和群友发生赛博 ccb 行为的群娱乐插件 ✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/zebwqfox/nonebot-plugin-ccb.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-ccb">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-ccb.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="python">
<a href="https://nonebot.dev/">
    <img src="https://img.shields.io/badge/nonebot-2.4.0+-red.svg" alt="nonebot2">
</a>
<a href="https://onebot.dev/">
    <img src="https://img.shields.io/badge/OneBot-v11-black.svg" alt="onebot">
</a>

</div>

> [!WARNING]
> 本插件文案含成人向玩笑，请只在成员都能接受的群里启用（可以用 `CCB_GROUPS` 限定群）。群友随时可以用 `ccbnodo` 拒绝被 ccb。

## 📖 介绍

在群里 `ccb @某人`，机器人会随机生成这次 ccb 的时长和「生命因子」注入量，并记录到本群的数据里。

- 🎲 **随机结果**：时长、注入量随机生成，10% 概率暴击，注入量翻倍
- 💥 **炸膛机制**：短时间内连续 ccb，炸膛概率会越来越高，炸膛后需要冷却一段时间
- 📊 **数据统计**：按群分别记录被 ccb / 主动 ccb 的次数、累计注入量、单次最高，附带排行榜
- 🛡️ **防 ccb 开关**：开启后别人无法 @ 你，随机挑人时也会跳过你
- ⌨️ **指令免前缀**：`ccb @某人` 和 `/ccb @某人` 都能触发，`ccbxyz`、`今天ccb` 这类普通聊天不会误触发

玩法参考自 AstrBot 的 [astrbot_plugin_ccb](https://github.com/tenno1174/astrbot_plugin_ccb) 及其增强版 [astrbot_plugin_ccb_plus](https://github.com/Koikokokokoro/astrbot_plugin_ccb_plus)，本插件为 NoneBot2 重新实现。

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-ccb

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>uv</summary>

    uv add nonebot-plugin-ccb
</details>
<details>
<summary>pip</summary>

    pip install nonebot-plugin-ccb
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-ccb
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-ccb
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_ccb"]

</details>

<details>
<summary>从 GitHub 安装（最新开发版）</summary>

    pip install git+https://github.com/zebwqfox/nonebot-plugin-ccb.git

</details>

## ⚙️ 配置

在 nonebot2 项目的 `.env` 文件中按需添加下表中的配置，全部为选填

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----|
| `CCB_GROUPS` | 否 | `[]` | 允许使用的群号列表，留空表示所有群 |
| `CCB_NAME` | 否 | `"ccb"` | 文案里的代号，同时也是指令名 |
| `CCB_SHOW_AVATAR` | 否 | `true` | 回复时附上对方头像 |
| `CCB_REQUIRE_SLASH` | 否 | `false` | 设为 `true` 时必须加命令前缀 `/` 才能触发 |
| `CCB_CRIT_CHANCE` | 否 | `0.1` | 暴击概率 |
| `CCB_BURST_WINDOW` | 否 | `1800` | 统计连续次数的时间窗（秒） |
| `CCB_BURST_STEP` | 否 | `0.08` | 时间窗内每多 ccb 一次，炸膛概率增加多少 |
| `CCB_BURST_MAX` | 否 | `0.6` | 炸膛概率上限 |
| `CCB_BURST_COOLDOWN` | 否 | `600` | 炸膛后的冷却时间（秒） |

<details>
<summary>配置示例</summary>

```dotenv
# 只在这两个群启用
CCB_GROUPS=[123456789, 987654321]
# 关闭头像，减少刷屏
CCB_SHOW_AVATAR=false
# 炸膛后冷却 5 分钟
CCB_BURST_COOLDOWN=300
```

</details>

## 🎉 使用

### 指令表

指令前面加不加 `/` 都可以（可用 `CCB_REQUIRE_SLASH` 改为必须加）。

| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----|
| `ccb [@某人]` | 群员 | 否 | 群聊 | 对 ta ccb，不 @ 就随机挑一位群友。别名：`踩踩背`、`捶捶背` |
| `ccb查询 [@某人]` | 群员 | 否 | 群聊 | 查看被 ccb / 主动 ccb 的次数、注入量和单次最高，不 @ 就查自己 |
| `ccb排行 [次数\|注入\|主动]` | 群员 | 否 | 群聊 | 本群排行榜，默认按被 ccb 次数 |
| `ccbnodo` | 群员 | 否 | 群聊 | 开关自己的防 ccb。别名：`防ccb` |
| `ccbclear` | 群主 / 管理员 / 超级用户 | 否 | 群聊 | 清空本群记录，防 ccb 设置会保留 |

> 表中「需要@」指是否需要 @ 机器人；`ccb` 后面的 `@某人` 是指定对象，可以省略。

### 效果图

```text
你和某某发生了35.26min长的ccb行为，向ta注入了16.71ml的生命因子
[对方头像]
这是ta的第626次。
```

```text
💥你炸膛了！不能ccb了（悲）
10 分钟后才能恢复
```

```text
🏆 本群被ccb次数排行
🥇 群友A：12次
🥈 群友B：9次
🥉 群友C：5次
```

## 📦 数据存储

记录保存在 [nonebot-plugin-localstore](https://github.com/nonebot/plugin-localstore) 提供的插件数据目录下的 `ccb.json`，按群分开存放。炸膛冷却只保存在内存中，重启后会清空。

## 📄 许可

本项目使用 [MIT](./LICENSE) 许可证。
