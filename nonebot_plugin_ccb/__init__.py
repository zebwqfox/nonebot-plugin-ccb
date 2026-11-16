"""群娛樂：和群友發生賽博 ccb 行為（NoneBot 版，功能參考 AstrBot 的 ccb / ccb_plus）。

指令前面的 / 可加可不加：`ccb @某人` 和 `/ccb @某人` 都能觸發。
"""

from __future__ import annotations

import random

from nonebot import get_plugin_config, on_message, require
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message,
    MessageSegment,
)
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.rule import Rule
from nonebot.typing import T_State
from pydantic import BaseModel

require("nonebot_plugin_localstore")
import nonebot_plugin_localstore as store

from .data import CcbStore, Rules
from .match import match_command


class Config(BaseModel):
    ccb_groups: list[int] = []
    """允許使用的群，留空表示所有群。"""
    ccb_name: str = "ccb"
    """文案裡的代號，也是指令名。"""
    ccb_show_avatar: bool = True
    """回覆時附上對方頭像。"""
    ccb_require_slash: bool = False
    """true 時必須用 /ccb 觸發；預設 ccb 和 /ccb 都可以。"""
    ccb_crit_chance: float = 0.1
    ccb_burst_step: float = 0.08
    ccb_burst_max: float = 0.6
    ccb_burst_window: int = 1800
    ccb_burst_cooldown: int = 600


config = get_plugin_config(Config)
N = config.ccb_name

__plugin_meta__ = PluginMetadata(
    name="ccb",
    description="和群友发生赛博ccb行为",
    usage=(
        f"{N} [@某人]：对 ta {N}，不 @ 就随机挑一位群友\n"
        f"{N}查询 [@某人]：查看记录\n"
        f"{N}排行 [注入|主动]：群排行榜\n"
        f"{N}nodo：开关防{N}（开启后别人不能对你{N}）\n"
        f"{N}clear：清空本群记录（群管理）\n"
        "以上指令前面加不加 / 都可以"
    ),
    type="application",
    homepage="https://github.com/zebwqfox/nonebot-plugin-ccb",
    config=Config,
    supported_adapters={"~onebot.v11"},
)

ccb_store = CcbStore(
    store.get_plugin_data_file("ccb.json"),
    Rules(
        crit_chance=config.ccb_crit_chance,
        burst_step=config.ccb_burst_step,
        burst_max=config.ccb_burst_max,
        burst_window=config.ccb_burst_window,
        burst_cooldown=config.ccb_burst_cooldown,
    ),
)


def command(*names: str) -> Rule:
    """群訊息以指令名開頭（可選 / 前綴）時觸發，剩下的文字放進 state["arg"]。"""

    async def _rule(event: GroupMessageEvent, state: T_State) -> bool:
        if config.ccb_groups and event.group_id not in config.ccb_groups:
            return False
        arg = match_command(
            event.message.extract_plain_text(), names, require_slash=config.ccb_require_slash
        )
        if arg is None:
            return False
        state["arg"] = arg
        return True

    return Rule(_rule)


def _target_from(event: GroupMessageEvent, arg: str) -> int | None:
    """從 @ 或純數字參數取得目標 QQ。"""
    for seg in event.message:
        if seg.type == "at" and str(seg.data.get("qq")) not in ("all", str(event.self_id)):
            return int(seg.data["qq"])
    return int(arg) if arg.isdigit() else None


async def _name(bot: Bot, gid: int, uid: int) -> str:
    try:
        info = await bot.get_group_member_info(group_id=gid, user_id=uid)
        return info.get("card") or info.get("nickname") or str(uid)
    except Exception:
        return str(uid)


def _avatar(uid: int | str) -> MessageSegment:
    return MessageSegment.image(f"https://q1.qlogo.cn/g?b=qq&nk={uid}&s=640")


ccb = on_message(rule=command(N, "踩踩背", "捶捶背"), priority=10, block=True)


@ccb.handle()
async def _ccb(bot: Bot, event: GroupMessageEvent, state: T_State) -> None:
    arg: str = state["arg"]
    gid, uid = event.group_id, event.user_id

    left = ccb_store.cooldown_left(gid, uid)
    if left > 0:
        await ccb.finish(f"💥你炸膛了！不能{N}了（悲）还要 {max(1, round(left / 60))} 分钟才能恢复")

    target = _target_from(event, arg)
    if target is None:
        members = await bot.get_group_member_list(group_id=gid)
        pool = [
            m["user_id"]
            for m in members
            if m["user_id"] not in (uid, event.self_id) and not ccb_store.is_nodo(gid, m["user_id"])
        ]
        if not pool:
            await ccb.finish(f"群里没有可以{N}的人了（悲）")
        target = random.choice(pool)
    elif target == uid:
        await ccb.finish(f"不能对自己{N}哦")
    elif ccb_store.is_nodo(gid, target):
        await ccb.finish(f"ta 开启了防{N}，换个人吧")

    if ccb_store.roll_burst(gid, uid):
        await ccb.finish(
            f"💥你炸膛了！不能{N}了（悲）\n"
            f"{config.ccb_burst_cooldown // 60} 分钟后才能恢复"
        )

    target_name = await _name(bot, gid, target)
    my_name = event.sender.card or event.sender.nickname or str(uid)
    r = ccb_store.do_ccb(gid, uid, my_name, target, target_name)

    vol = f" 💥 暴击！{r.ml:.2f}" if r.crit else f"{r.ml:.2f}"
    msg = Message(f"你和{target_name}发生了{r.minutes:.2f}min长的{N}行为，向ta注入了{vol}ml的生命因子")
    if config.ccb_show_avatar:
        msg += _avatar(target)
    else:
        msg += "\n"
    msg += f"这是ta的第{r.target_count}次。"
    await ccb.finish(msg)


query = on_message(rule=command(f"{N}查询", f"{N}记录"), priority=9, block=True)


@query.handle()
async def _query(bot: Bot, event: GroupMessageEvent, state: T_State) -> None:
    arg: str = state["arg"]
    gid = event.group_id
    target = _target_from(event, arg) or event.user_id
    s = ccb_store.stats(gid, target)
    name = await _name(bot, gid, target)
    if not s:
        await query.finish(f"{name} 还没有任何{N}记录")
    lines = [
        f"📋 {name} 的{N}记录",
        f"被{N}：{s['received']} 次，累计被注入 {s['received_ml']:.2f}ml",
        f"主动{N}：{s['given']} 次，累计注入 {s['given_ml']:.2f}ml",
        f"单次最高注入：{s['max_ml']:.2f}ml",
    ]
    if ccb_store.is_nodo(gid, target):
        lines.append(f"🛡️ 已开启防{N}")
    await query.finish("\n".join(lines))


RANK_KEYS = {
    "": ("received", "被{N}次数", "次"),
    "次数": ("received", "被{N}次数", "次"),
    "注入": ("received_ml", "被注入量", "ml"),
    "主动": ("given", "主动{N}次数", "次"),
}

rank = on_message(rule=command(f"{N}排行", f"{N}榜", f"{N}top"), priority=9, block=True)


@rank.handle()
async def _rank(event: GroupMessageEvent, state: T_State) -> None:
    arg: str = state["arg"]
    key, title, unit = RANK_KEYS.get(arg, RANK_KEYS[""])
    rows = ccb_store.ranking(event.group_id, key)
    if not rows:
        await rank.finish(f"本群还没有{N}记录")
    medals = ["🥇", "🥈", "🥉"]
    lines = [f"🏆 本群{title.format(N=N)}排行"]
    for i, (_, s) in enumerate(rows):
        mark = medals[i] if i < len(medals) else f"{i + 1}."
        value = f"{s[key]:.2f}" if unit == "ml" else str(s[key])
        lines.append(f"{mark} {s['name']}：{value}{unit}")
    await rank.finish("\n".join(lines))


nodo = on_message(rule=command(f"{N}nodo", f"防{N}"), priority=9, block=True)


@nodo.handle()
async def _nodo(event: GroupMessageEvent) -> None:
    on = ccb_store.toggle_nodo(event.group_id, event.user_id)
    await nodo.finish(f"🛡️ 已开启防{N}，别人不能对你{N}了" if on else f"已关闭防{N}")


clear = on_message(
    rule=command(f"{N}clear"),
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    priority=9,
    block=True,
)


@clear.handle()
async def _clear(event: GroupMessageEvent) -> None:
    ccb_store.clear(event.group_id)
    await clear.finish(f"已清空本群的{N}记录（防{N}设置保留）")
