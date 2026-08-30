# uBot — GF 26.1.11 release notes

Adapts the walker + bots to the **26.1.11** client. Pairs with the rebuilt `eXLib.mix` (see `../MetinPythonLib-WalkerPath`).

## Crash + regression fixes
- **Teleport key regression** — `Hooks.py`, `Data.py`. After a world reload (death→teleport, map change, channel switch) the recreated game window's `interface` was `None`, so **I / V / C stopped toggling** inventory/character windows (ESC and the on-screen buttons still worked). The game-window hook used to self-unhook after the first window, so it never re-participated in teleport-recreates. It's now **persistent** (recursion-safe via `CallOriginalFunction`; the shortcut/stream thread is created once), and the permanent `_pinWindow` window-retention (a leak + focus-stealer) was removed.
- **Position reads** — `OpenLib`, `ShopSearcher`, `StoneCompass`, `AutoHunting`, `Radar`, `Settings`, `Buffbot`. Switched every bot from `chr.GetPixelPosition` (returns **NaN** on 26.1.11) to `eXLib.GetPixelPosition`. A NaN coordinate silently breaks all distance math (StoneCompass "none in range", AutoHunt won't approach, shop scan crashes).

## Bots
- **Trading Glass / Shop search** — `ShopSearcher.py`: full-map A\* sweep with checkpoints, working class filter, NaN guards, and **Stop now halts the character immediately** (cancels the in-flight move, like EnergyBot).
- **Stone Compass** — `StoneCompass.py`: reload-safe; metin / ore / boss detection via eXLib; added to `/rah`.
- **Auto-hunt** — `AutoHunting.py`: level-filtered acquisition + focus/skill logic on eXLib positions; reload-safe.
- **Energy bot** — `EnergyBot.py`: dynamic inventory sizing, clock-reset-safe timers, and `GetDialogAnswerCount`-based dialog auto-pick (second-to-last = Open Shop) **with the "I have Weapon Shop mission" checkbox as fallback** (active until the event-mgr RVA is re-derived on eXLib side).
- **Manual-intervention-stops-movement** — `OpenLib.py`: while a bot is pathing, moving the character against the commanded direction for ~0.36 s stops the path (`StopMovement` + stops the sweep / EnergyBot driver). Tunable via `MANUAL_STOP_MOVE_EPS` / `MANUAL_STOP_TICKS`.

## Infra + release cleanup
- **`/rah` + `/rah-ui`** in-game hot-reload (`init.py`) — reload bot logic / rebuild windows without a client restart (OpenLib, ShopSearcher, EnergyBot, AutoHunting, StoneCompass).
- Release-silenced debug chat: manual-stop message (`MANUAL_STOP_DEBUG=False`), `[P1]` phase diagnostic (`PHASE1_DEBUG`), per-item auto-sell spam (`NPCInteraction`), value dumps (`ActionFunctions`). All bot debug flags are `False` (`AH_DEBUG`, `EB_DEBUG`, ShopSearcher `DEBUG`, StoneCompass `STATUS_DEBUG`).
- Stopped tracking compiled `.pyc` bytecode.
- Updated deployed `eXLib.mix`.
