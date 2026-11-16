"""ccb 紀錄的存取與遊戲邏輯（不依賴 NoneBot，可單獨測試）。"""

from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Rules:
    min_minutes: float = 1.0
    max_minutes: float = 60.0
    min_ml: float = 1.0
    max_ml: float = 20.0
    crit_chance: float = 0.1
    """暴擊機率，暴擊時注入量翻倍。"""
    burst_window: int = 1800
    """統計連續 ccb 次數的時間窗（秒）。"""
    burst_step: float = 0.08
    """時間窗內每多 ccb 一次，炸膛機率增加多少。"""
    burst_max: float = 0.6
    burst_cooldown: int = 600
    """炸膛後多久不能 ccb（秒）。"""


@dataclass
class Outcome:
    minutes: float
    ml: float
    crit: bool
    target_count: int
    target_total: float


class CcbStore:
    """按群儲存紀錄：{group: {"users": {uid: stats}, "nodo": [uid]}}。"""

    def __init__(self, path: Path, rules: Rules | None = None) -> None:
        self.path = path
        self.rules = rules or Rules()
        self.data: dict[str, Any] = {}
        # 只存在記憶體：{(group, uid): [timestamps]} 與 {(group, uid): 冷卻結束時間}
        self._recent: dict[tuple[str, str], list[float]] = {}
        self._cooldown: dict[tuple[str, str], float] = {}
        self.load()

    # ---- 持久化 ----
    def load(self) -> None:
        try:
            self.data = json.loads(self.path.read_text("utf-8"))
        except FileNotFoundError:
            self.data = {}

    def save(self) -> None:
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, ensure_ascii=False, indent=1), "utf-8")
        tmp.replace(self.path)

    def _group(self, gid: int | str) -> dict[str, Any]:
        return self.data.setdefault(str(gid), {"users": {}, "nodo": []})

    def _user(self, gid: int | str, uid: int | str) -> dict[str, Any]:
        users = self._group(gid)["users"]
        return users.setdefault(
            str(uid),
            {
                "name": str(uid),
                "received": 0,  # 被 ccb 次數
                "received_ml": 0.0,  # 被注入總量
                "given": 0,  # 主動 ccb 次數
                "given_ml": 0.0,  # 主動注入總量
                "max_ml": 0.0,  # 單次最大注入量
            },
        )

    # ---- 防 ccb 開關 ----
    def is_nodo(self, gid: int | str, uid: int | str) -> bool:
        return str(uid) in self._group(gid)["nodo"]

    def toggle_nodo(self, gid: int | str, uid: int | str) -> bool:
        """切換防 ccb，回傳切換後是否開啟。"""
        nodo: list[str] = self._group(gid)["nodo"]
        if str(uid) in nodo:
            nodo.remove(str(uid))
            on = False
        else:
            nodo.append(str(uid))
            on = True
        self.save()
        return on

    # ---- 炸膛冷卻 ----
    def cooldown_left(self, gid: int | str, uid: int | str, now: float | None = None) -> float:
        now = time.time() if now is None else now
        return max(0.0, self._cooldown.get((str(gid), str(uid)), 0.0) - now)

    def roll_burst(
        self, gid: int | str, uid: int | str, rng: random.Random | None = None,
        now: float | None = None,
    ) -> bool:
        """這次出手前判定是否炸膛；炸膛就進入冷卻並清空連續次數。"""
        rng = rng or random
        now = time.time() if now is None else now
        key = (str(gid), str(uid))
        recent = [t for t in self._recent.get(key, []) if now - t < self.rules.burst_window]
        self._recent[key] = recent
        prob = min(self.rules.burst_step * len(recent), self.rules.burst_max)
        if recent and rng.random() < prob:
            self._cooldown[key] = now + self.rules.burst_cooldown
            self._recent[key] = []
            return True
        return False

    # ---- 主邏輯 ----
    def do_ccb(
        self,
        gid: int | str,
        uid: int | str,
        uid_name: str,
        target: int | str,
        target_name: str,
        rng: random.Random | None = None,
        now: float | None = None,
    ) -> Outcome:
        rng = rng or random
        now = time.time() if now is None else now
        r = self.rules
        minutes = round(rng.uniform(r.min_minutes, r.max_minutes), 2)
        ml = round(rng.uniform(r.min_ml, r.max_ml), 2)
        crit = rng.random() < r.crit_chance
        if crit:
            ml = round(ml * 2, 2)

        giver = self._user(gid, uid)
        giver["name"] = uid_name
        giver["given"] += 1
        giver["given_ml"] = round(giver["given_ml"] + ml, 2)
        giver["max_ml"] = max(giver["max_ml"], ml)

        tgt = self._user(gid, target)
        tgt["name"] = target_name
        tgt["received"] += 1
        tgt["received_ml"] = round(tgt["received_ml"] + ml, 2)

        self._recent.setdefault((str(gid), str(uid)), []).append(now)
        self.save()
        return Outcome(minutes, ml, crit, tgt["received"], tgt["received_ml"])

    def stats(self, gid: int | str, uid: int | str) -> dict[str, Any] | None:
        return self._group(gid)["users"].get(str(uid))

    def ranking(self, gid: int | str, key: str, limit: int = 10) -> list[tuple[str, dict]]:
        users = self._group(gid)["users"].items()
        ranked = sorted(
            ((u, s) for u, s in users if s.get(key)), key=lambda x: x[1][key], reverse=True
        )
        return ranked[:limit]

    def clear(self, gid: int | str) -> None:
        group = self._group(gid)
        group["users"] = {}
        self._recent = {k: v for k, v in self._recent.items() if k[0] != str(gid)}
        self._cooldown = {k: v for k, v in self._cooldown.items() if k[0] != str(gid)}
        self.save()
