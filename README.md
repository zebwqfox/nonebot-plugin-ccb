# nonebot-plugin-ccb

和群友发生赛博 ccb 行为的 [NoneBot2](https://nonebot.dev/) 群娱乐插件，适用于 OneBot V11（NapCat、LLOneBot 等）。

> ⚠️ 本插件文案含成人向玩笑，请只在成员都能接受的群里启用（可用 `CCB_GROUPS` 限定群）。群友可以随时用 `ccbnodo` 拒绝被 ccb。

## 效果

```
你和某某发生了35.26min长的ccb行为，向ta注入了16.71ml的生命因子
[对方头像]
这是ta的第626次。
```

- 随机时长和注入量，10% 概率暴击（注入量翻倍）
- 短时间内连续 ccb 会越来越容易**炸膛**，炸膛后进入冷却
- 按群分别记录次数、累计注入量、单次最高，并提供排行榜
- 防 ccb 开关：开启后别人无法 @ 你，随机挑人时也会跳过你

## 安装

```bash
nb plugin install nonebot-plugin-ccb
```

尚未发布到 PyPI 前，可以直接从 GitHub 安装：

```bash
pip install git+https://github.com/zebwqfox/nonebot-plugin-ccb.git
```

然后在 `pyproject.toml` 的 `[tool.nonebot]` 里加入 `nonebot_plugin_ccb`。

## 指令

指令前面加不加 `/` 都可以（`ccb @某人` 和 `/ccb @某人` 都能触发）。只在群聊中生效。

| 指令 | 说明 |
|---|---|
| `ccb [@某人]` | 对 ta ccb；不 @ 就随机挑一位群友。别名：`踩踩背`、`捶捶背` |
| `ccb查询 [@某人]` | 查看被 ccb / 主动 ccb 的次数、注入量和单次最高；不 @ 就查自己 |
| `ccb排行 [次数\|注入\|主动]` | 本群排行榜，默认按被 ccb 次数 |
| `ccbnodo` | 开关自己的防 ccb |
| `ccbclear` | 清空本群记录（仅群主、群管理员、超级用户），防 ccb 设置会保留 |

指令后面必须是空白、@ 或直接结束，所以 `ccbxyz`、`今天ccb` 这类普通聊天不会误触发。

## 配置

在 `.env` 中设置，全部可选：

| 配置项 | 默认值 | 说明 |
|---|---|---|
| `CCB_GROUPS` | `[]` | 允许使用的群号列表，留空表示所有群 |
| `CCB_NAME` | `"ccb"` | 文案里的代号，同时也是指令名 |
| `CCB_SHOW_AVATAR` | `true` | 回复时附上对方头像 |
| `CCB_REQUIRE_SLASH` | `false` | 设为 `true` 时必须加 `/` 才能触发 |
| `CCB_CRIT_CHANCE` | `0.1` | 暴击概率 |
| `CCB_BURST_WINDOW` | `1800` | 统计连续次数的时间窗（秒） |
| `CCB_BURST_STEP` | `0.08` | 时间窗内每多 ccb 一次，炸膛概率增加多少 |
| `CCB_BURST_MAX` | `0.6` | 炸膛概率上限 |
| `CCB_BURST_COOLDOWN` | `600` | 炸膛后的冷却时间（秒） |

记录保存在 [nonebot-plugin-localstore](https://github.com/nonebot/plugin-localstore) 的插件数据目录（`ccb.json`）；炸膛冷却只保存在内存中，重启后清空。

## 致谢

玩法参考自 AstrBot 的 [astrbot_plugin_ccb](https://github.com/tenno1174/astrbot_plugin_ccb)（灵煞）及其增强版 [astrbot_plugin_ccb_plus](https://github.com/Koikokokokoro/astrbot_plugin_ccb_plus)。本插件为 NoneBot2 重新实现，未使用上述项目的代码。

## 许可

[MIT](LICENSE)
