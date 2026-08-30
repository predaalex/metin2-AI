
import sys
_chr = chr

import __builtin__ as buildin
try:
	import time
except:
	pass

def HasArguments(module, attrlist):
    for attr in attrlist:
        if not buildin.hasattr(module, attr):
            return False
    return True

# GF native auto-hunt module: registered name is randomized each release, found by a marker method.
autoHunting = None

for modulename, module in iter(sys.modules.items()):
    if HasArguments(module, ['clock']):time = module
    if HasArguments(module, ['GetPlayTime']):player = module
    if HasArguments(module, ['GetNameByVID']):chr = module
    if HasArguments(module, ['DirectEnter']):net = module
    if HasArguments(module, ['SetCameraMaxDistance']):app = module
    if HasArguments(module, ['ArrangeShowingChat']):chat = module
    if HasArguments(module, ['GetCurrentMapName']):background = module
    if HasArguments(module, ['GetGradeByVID']):nonplayer = module
    if HasArguments(module, ['GetSkillCoolTime', 'GetSkillLevelUpPoint']):skill = module
    if HasArguments(module, ['ScriptWindow']):ui = module
    if HasArguments(module, ['SendRequestAutoHuntingOnoff']):autoHunting = module
    if HasArguments(module, ['ClearSlot']):wndMgr = module
    if HasArguments(module, ['GetItemName', 'SelectItem']):item = module

import UIComponents
from BotBase import BotBase
import OpenLib, eXLib, FileManager, Data, Movement, Settings, Hooks

# 1:1 clone of the GF AutoHuntingWindow (UIScript/AutoHuntingWindow.py exact coordinates). Attack +
# Focus(range) run on the client's OWN native engine; uBot layers potions/skills/revive for free.

# ===== EXACT official layout constants (GF-25.1.6.0 UIScript/AutoHuntingWindow.py) =====
BOARD_W, BOARD_H                = 254, 490
SKILL_BAR_X, SKILL_BAR_Y        = 14, 36
SKILL_TEXT_X, SKILL_TEXT_Y      = 9, 2
SKILL_SLOT_X, SKILL_SLOT_Y      = 15, 59
SLOT_DX, SLOT_DY                = 38, 54
SLOT_W, SLOT_H                  = 32, 32
POTION_BAR_X, POTION_BAR_Y      = 14, 118   # Potions section shifted UP to the old Skills row-2 top (was 171)
POTION_SLOT_X, POTION_SLOT_Y    = 15, 140   # header+23 to match Skills' header->slot gap (55-34); 3 rows
SETTING_BAR_X, SETTING_BAR_Y    = 14, 306
SETTING_TEXT_X, SETTING_TEXT_Y  = 9, 2
SET_BAR_X                       = 3
SET_ROW_Y                       = [20, 47, 74, 101, 128]   # attack/range/potion/skill/restart
AUTO_BTN_X, AUTO_BTN_BASE_Y, AUTO_BTN_DY = 194, 327, 27
OPT_BTN_DX                      = 42
SAVE_X, START_X, END_X, BOTTOM_Y = 10, 88, 166, 459.5
SK_COOL_X, SK_COOL_Y, SK_COOL_DY = 15, 93, 54
PO_COOL_X, PO_COOL_Y, PO_COOL_DY = 20, 173.5, 54   # = POTION_SLOT_Y+34 -> icon->input gap == input->next-icon gap
# =====================================================================================

# official .sub images
IMG_SLOT_BASE = 'd:/ymir work/ui/public/Slot_Base.sub'
IMG_SMALL     = ('d:/ymir work/ui/public/Small_Button_01.sub', 'd:/ymir work/ui/public/Small_Button_02.sub', 'd:/ymir work/ui/public/Small_Button_03.sub')
IMG_BOTTOM    = ('d:/ymir work/ui/game/windows/auto_system_bottom_button_01.sub', 'd:/ymir work/ui/game/windows/auto_system_bottom_button_02.sub', 'd:/ymir work/ui/game/windows/auto_system_bottom_button_03.sub')
IMG_OPT       = ('d:/ymir work/ui/game/auto_hunting/option_window_open_button_01.sub', 'd:/ymir work/ui/game/auto_hunting/option_window_open_button_02.sub', 'd:/ymir work/ui/game/auto_hunting/option_window_open_button_03.sub')

COLOR_HDR = (255, 200, 80)
COLOR_TXT = (255, 255, 255)

DEFAULT_RANGE   = 4000   # 40m (the GF focus default); slider 20-80m
POTION_TICK     = 0.5
SKILL_TICK      = 0.4
BUFF_PARK_MAX   = 3.0    # hard wall-clock cap on how long combat may pause to land ONE buff cast. After
                        # this the buff's timer is force-advanced so the attack loop can never hang on a
                        # buff that won't register (was the "1 hit then the bot freezes with buffs on").
OFF_ANIM        = 1.8    # assumed offensive-skill animation length. A buff won't cast until this long
                        # after the last offensive cast, so its ClickSkillSlot isn't eaten mid-animation
                        # (the warrior-mental "buff never called while an offensive skill is in queue").
BUFF_GCD        = 3.0    # min gap between a buff cast and ANY prior skill cast (buff OR offensive). Casting
                        # inside the previous skill's cast ANIMATION is silently dropped -> the optimistic
                        # timer then skips that buff a whole cycle. The animation length isn't in any table
                        # (it's baked into the granny .gr2), and berserk's runs >2s, so 3s empirically. Bump
                        # higher if a long-animation buff (e.g. berserk) still skips the next buff (aura).
NATIVE_ATTACK_ONLY = False  # face-snap + approach/melee (reliable); +0x34B44 route proven not to drive facing
                            # committed, just call NEW_Attack (it has its own native move-to-attack + smooth
                            # face + attack). If this looks native -> our pathfinding/hand-off caused the
                            # pivot. If it STILL pivots -> NEW_Attack itself / the retarget. Set False to restore.
# _swingAt faces the target (chr.SetRotation) immediately before NEW_Attack so the frontal-arc attack
# lands. Smooth per-frame facing isn't reachable from python (the client owns per-frame rotation).
# Buffs recast at their skill DURATION + 2s (the box value), gated by an SP check so a buff we can't
# afford never parks the attack loop (no stop-start with 0 SP). See _doSkills.
REVIVE_TICK     = 3.0
REVIVE_GRACE    = 5.0    # after a revive, wait this long before attacking again (potions still run) so a
                        # char rezzed with low HP doesn't instantly re-engage and die in a loop while farming.
NATIVE_TICK     = 2.0
AH_FUNC_ENGINE  = 0
AH_FUNC_ATTACK  = 1
AH_FUNC_RANGE   = 4
RANGE_MIN_U, RANGE_MAX_U, RANGE_NATIVE_U = 2000, 8000, 10000
EFFECT_RECYCLE  = 2.0
STUCK_SECS      = 2.0   # stationary this long while the focused target is out of range = blocked
APPROACH_TICK   = 1.5   # throttle re-issuing uBot's collision-aware walk-to-target
USE_CUSTOM_ENGINE = True   # PURE CUSTOM: uBot picks nearest + walks to it + attacks via packet (proven
                           # damage) PLUS chr.PushOnceMotion for the visible swing animation. No native
                           # engine (it bricked when mixed with uBot movement control).
# The swing animation: chr.PushOnceMotion(motionMode, MOTION_NORMAL_ATTACK) plays the LOCAL attack motion
# (what SetAttackKeyState would -- but that's dead on GF). motionMode is read from the ACTUAL equipped
# weapon subtype (NOT class -- a shaman holds bell OR fan, a warrior 1H OR 2H). See _weaponMode().
MOTION_NORMAL_ATTACK = 13
HYBRID_STEER    = False  # DEAD END: the native engine ignores SetTarget (re-selects its own target every
                         # frame by category priority), so steering just caused focus!=attacked-mob. Off.
STEER_TICK      = 0.5    # (unused while HYBRID_STEER is off)
SWING_TICK      = 0.30  # cadence of the attack while a target is in melee range
ACQUIRE_TICK    = 0.4   # how often to (re)pick the nearest in-zone target when we have none
COMBAT_MAX      = 460   # enter/stay-in melee out to this dist (mob body radius + reach). Once in melee we
                        # commit to attacking (no dancing around the ATTACK_RANGE ring); the mob closes in.
# BOW: a bow shoots from range, so we should NOT walk into melee for it. When the equipped weapon is a bow
# we engage (start shooting) at BOW_ENGAGE and keep shooting until the mob flees past BOW_STAY, instead of
# ATTACK_RANGE/COMBAT_MAX. Melee weapons are untouched.
# CLIENT-SOURCE EXACT: CInstanceBase::__GetBowRange() = 2500-100 = 2400 (+POINT_BOW_DISTANCE from bow-range
# skills/affects), and it's compared against GetDistance() -- the SAME value player.GetCharacterDistance
# returns. So 2400 IS the true max shooting range in our dist units. Engage a touch inside it so shots
# land; STAY out to the max. (If a char has bow-distance skills the real max is higher -> raise these.)
BOW_ENGAGE      = 2200
BOW_STAY        = 2400
# Attack-filter categories: panel checkboxes [cat1, cat2, cat3, cat4, cat5, Boss, Metin] (flags 0-6).
# The CLIENT'S OWN live mob table gives us the data (same source as the target bar "Lv.X (Categoria Y)"):
#   nonplayer.GetGradeByVID(vid) -> the mob RANK byte (0=PAWN,1=S_PAWN,2=KNIGHT,3=S_KNIGHT,4=BOSS,5=KING)
#   nonplayer.GetLevelByVID(vid) -> the mob level
# No mob_proto.txt to maintain, always current. GRADE_TO_FLAG maps that rank byte -> the checkbox index
# (BOSS->Boss, KING->cat5 since metins are rank KING). VERIFY the exact grade<->Categoria numbers live
# (AH_DEBUG logs grade+lvl per acquired mob).
GRADE_TO_FLAG = {0: 0, 1: 1, 2: 2, 3: 3, 4: 5, 5: 4}
ACTIVE_SKILL_IDS = set([109,110,111,174,175,19,34,49,63,64,65,78,79,94,95,96,3,4])

# Fallback skill icon (vnum -> (class folder, icon name)) for when the client's skilldesc.txt is
# missing/malforming a row so SKILL_INFORMATION[id] KeyErrors -> blank icon (seen: id5/tanhwan).
# Body-warrior set (confirmed from the reference skilldesc); add other class skills here if needed.
SKILL_ICON_FALLBACK = {
    1: ('warrior', 'samyeon'),   2: ('warrior', 'palbang'),    3: ('warrior', 'jeongwi'),
    4: ('warrior', 'geomgyeong'),5: ('warrior', 'tanhwan'),    6: ('warrior', 'gihyeol'),
    170: ('wolfman', 'split_slash'),   171: ('wolfman', 'wind_death'),     172: ('wolfman', 'reef_attack'),
    173: ('wolfman', 'wreckage'),      174: ('wolfman', 'red_possession'), 175: ('wolfman', 'blue_possession'),
}

# ============================ HARDCODED HELPER CONSUMABLES =============================
# Potion slots 2..11. {name, ids[], type('cooldown'|'interval'), time(secs)}. Fill with your items:
#   {'name': 'Bravery Cape', 'ids': [27989, 27990, 71092], 'type': 'interval', 'time': 300},
#   {'name': 'Water of Life','ids': [50026],               'type': 'cooldown', 'time': 1800},
HELPER_ITEMS = [
]
# ======================================================================================


CONFIG_AH = eXLib.PATH + 'OpenBot/Saves/autohunt.bot'   # persisted Auto-Hunt settings (key=value lines)

AH_DEBUG = False   # ON -> _dbg mirrors diagnostics to in-game chat. Off for release.
AH_BUILD = "2026-07-12h"   # bump every edit -> logged on (re)load so we KNOW /rah actually loaded new code


def _dbg(msg):
    if AH_DEBUG:
        try:
            chat.AppendChat(3, msg)
        except:
            pass


def _info(msg):
    # user-facing status line -- ALWAYS shown (not gated by AH_DEBUG), for things the bot user should
    # see (e.g. the post-revive countdown explaining why it isn't attacking yet).
    try:
        chat.AppendChat(3, msg)
    except:
        pass


def __PhaseCallback(phase, phaseWnd):
    if phase == OpenLib.PHASE_GAME:
        try:
            instance.onReenter()
        except:
            pass


class RangePreviewWindow(ui.ScriptWindow):
    def __init__(self, owner):
        ui.ScriptWindow.__init__(self)
        self.owner = owner
        self._attached = False
        self._lastAttach = 0.0
        self.Show()

    def _scale(self):
        # live: follow the Focus slider as it moves (not the last-confirmed huntRange)
        try:
            u = self.owner.focusPanel._val() * 100
        except:
            u = self.owner.huntRange
        u = max(RANGE_MIN_U, min(RANGE_MAX_U, u))
        return u / float(RANGE_NATIVE_U)

    def _detach(self):
        if self._attached:
            self._attached = False
            ah = self.owner._getAutoHunting()
            if ah is not None:
                try:
                    ah.DettachHuntingRangeEffectInstance()
                except:
                    pass

    def OnUpdate(self):
        # Auto-refresh the owner's skill section when it changes (skills unlocked at level-up, or a
        # character switch) so it updates without close+reopen. CRITICAL: only rebuild when the world
        # is STABLE (map name unchanged >= 1.5s) -- churning widgets mid-load corrupts the client GC
        # and crashes. This runs via the client pump (regardless of bot state), which is dropped during
        # the load anyway, so pairing it with the settle gate keeps rebuilds out of the danger window.
        try:
            now = OpenLib.GetTime()
            o = self.owner
            mp = background.GetCurrentMapName()
            if mp != getattr(o, '_lastMap', None):
                o._lastMap = mp
                o._mapChangedAt = now
            stable = o._inGame() and (now - getattr(o, '_mapChangedAt', 0.0) >= 1.5)
            if stable and now - getattr(self, '_lastSkChk', 0.0) > 1.0:
                self._lastSkChk = now
                try:
                    _race = net.GetMainActorRace()
                    Data.mainRace = _race
                    Data.mainSkillGroup = net.GetMainActorSkillGroup()
                except:
                    _race = 0
                # CRASH GUARD: only act on the actor data when it is VALID. race==0 means "no actor /
                # mid world-load" -- e.g. the 15-min-dead auto-revive to city. During that unload the OLD
                # map name still reads back (settle gate above thinks it's stable) while race momentarily
                # drops to 0 -> _skillSignature() flips to NONE != _builtSig -> a rebuild would fire and
                # churn widgets DURING the world teardown -> client GC use-after-free (_PyObject_GC_UNTRACK)
                # crash. A live teleport keeps race valid+unchanged so it never tripped this; only the
                # dead->revive reload did. When race==0 we simply SKIP the rebuild (not return -- the
                # effect-cleanup below must still run to drop the freed range effect); _skillsDirty stays
                # set so the deferred rebuild still fires on the next tick once race is valid & in-world.
                # `_race and ...` also short-circuits _skillSignature()/GetClass() away from bad data.
                # Rebuild whenever the class/learned-skill signature changed (or we were flagged dirty by a
                # world re-entry). Rebuild IMMEDIATELY -- no "confirm twice" gate: after a char switch the
                # new char's skills load progressively, so the signature changes for several ticks, and a
                # confirm-twice gate never fired -> the ONLY build was the early one while the class was
                # still unresolved (which clears to empty) -> "no skills work after switching character".
                # Pre-choice warrior-icon flashes are prevented by the mainSkillGroup==0 guard in
                # resetSkillsUI, not here, so immediate rebuild is safe.
                if _race and (getattr(o, '_skillsDirty', False) or o._skillSignature() != getattr(o, '_builtSig', None)):
                    o._skillsDirty = False
                    o.resetSkillsUI(force=True)
                    o.resetPotionsUI(force=True)
        except:
            pass
        # NEVER touch native effect instances outside the game phase. During a ch-switch/world load
        # the effect + python-GC systems are torn down/rebuilt; attaching/detaching effects then
        # corrupts the GC list (use-after-free -> crash in _PyObject_GC_UNTRACK on world load). The
        # world unload already frees our effect, so just forget it and re-attach fresh in-game.
        try:
            if OpenLib.GetCurrentPhase() != OpenLib.PHASE_GAME:
                self._attached = False
                return
        except:
            return
        # GF behaviour: the range circle only shows while the Focus-range sub-window is open
        try:
            preview = self.owner.focusPanel.Board.IsShow()
        except:
            preview = False
        if not preview:
            self._detach()
            return
        ah = self.owner._getAutoHunting()
        if ah is None:
            return
        now = OpenLib.GetTime()
        if not self._attached:
            self._attached = True
            self._lastAttach = now
            try:
                ah.AttachHuntingRangeEffectInstance(self._scale())
            except:
                pass
        elif now - self._lastAttach >= EFFECT_RECYCLE:
            self._lastAttach = now
            try:
                ah.DettachHuntingRangeEffectInstance()
            except:
                pass
            try:
                ah.AttachHuntingRangeEffectInstance(self._scale())
            except:
                pass
        try:
            ah.ControlHuntingRagneEffect(self._scale())
        except:
            pass


class FocusPanel(ui.ScriptWindow):
    # GF range sub-window: slider 20-80m (default 40), non-editable 'NM' readout, Confirm applies it.
    def __init__(self, owner):
        ui.ScriptWindow.__init__(self)
        self.owner = owner
        c = UIComponents.Component()
        self._keep = []
        self.Board = ui.BoardWithTitleBar()
        self.Board.SetSize(220, 114)
        self.Board.SetTitleName('Focus Range')
        self.Board.SetCloseEvent(self._close)
        self.Board.AddFlag('float')
        val = owner.huntRange // 100
        frac = max(0.0, min(1.0, (val - 20) / 60.0))
        self.slider = c.SliderBar(self.Board, frac, self._onSlide, 20, 40)
        self._keep.append(self.slider)
        self.valBar = ui.SlotBar()
        try:
            self.valBar.SetParent(self.Board)
            self.valBar.SetSize(54, 16)
            self.valBar.SetPosition(83, 63)
            self.valBar.Show()
            self._keep.append(self.valBar)
        except:
            pass
        self.valLbl = c.TextLine(self.Board, str(val) + 'M', 83 + 27, 65, c.RGB(*COLOR_TXT))
        try:
            self.valLbl.SetHorizontalAlignCenter()
        except:
            pass
        self._keep.append(self.valLbl)
        self.confirmBtn = c.Button(self.Board, 'Confirm', '', 75, 85, self._onConfirm, *IMG_BOTTOM)
        self.Board.Hide()
        self.Show()

    def _val(self):
        try:
            return int(round(20 + self.slider.GetSliderPos() * 60))
        except:
            return 40

    def _onSlide(self):
        try:
            self.valLbl.SetText(str(self._val()) + 'M')
        except:
            pass

    def _onConfirm(self):
        self.owner.huntRange = self._val() * 100
        ah = self.owner._getAutoHunting()
        if ah is not None:
            try:
                ah.SetHuntingRange(self.owner._rangeUnits())
            except:
                pass
        a = self.owner._pos(player.GetMainCharacterIndex())   # anchor the circle at the confirm position
        if a is not None:
            self.owner._anchor = a
            self.owner._confirmedAnchor = a   # this is now the center a later Focus ON re-applies
        self.Board.Hide()

    def _close(self):
        self.Board.Hide()

    def Open(self):
        try:
            self.owner.attackPanel.Board.Hide()   # only one side panel open at a time
        except:
            pass
        try:
            x, y = self.owner.Board.GetGlobalPosition()
            self.Board.SetPosition(int(x) + 251, int(y) + BOARD_H - 114)
        except:
            self.Board.SetPosition(310, 380)
        self.Board.Show()


class AttackPanel(ui.ScriptWindow):
    # GF attack-filter sub-window: monster category toggles (Level 1-5 = easy..hard rank), Boss,
    # Metin Stone, plus a player-level-diff filter (-X / +X). Wired to the native attack filters.
    LABELS = ['Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5', 'Boss', 'Metin Stone']

    def __init__(self, owner):
        ui.ScriptWindow.__init__(self)
        self.owner = owner
        c = UIComponents.Component()
        self.comp = c
        self._keep = []
        # restore persisted category filter (default all-on) + level-diff range
        self.flags = [owner._cfgBool('flag%d' % i, True) for i in range(7)]
        self.Board = ui.BoardWithTitleBar()
        self.Board.SetSize(200, 258)
        self.Board.SetTitleName('Attack Settings')
        self.Board.SetCloseEvent(self._close)
        self.Board.AddFlag('float')
        for n in range(7):
            y = 34 + 24 * n
            self._ilabel(self.LABELS[n], 14, y, 120, 16, tx=6)
            self._flagToggle(150, y - 1, n)
        yl = 34 + 24 * 7 + 6
        self._ilabel('Level', 14, yl, 44, 16, center=True)
        self._keep.append(c.TextLine(self.Board, '-', 64, yl + 3, c.RGB(*COLOR_TXT)))
        self.slotMinus, self.editMinus = c.EditLine(self.Board, owner._cfg.get('lvlMinus', '15'), 72, yl, 30, 16, 3)
        self._keep.append(c.TextLine(self.Board, '+', 110, yl + 3, c.RGB(*COLOR_TXT)))
        self.slotPlus, self.editPlus = c.EditLine(self.Board, owner._cfg.get('lvlPlus', '15'), 118, yl, 30, 16, 3)
        self.confirmBtn = c.Button(self.Board, 'Confirm', '', 60, yl + 22, self._onConfirm, *IMG_BOTTOM)
        self.Board.Hide()
        self.Show()

    def _ilabel(self, text, x, y, w, h, tx=6, center=False):
        try:
            bar = ui.SlotBar(); bar.SetParent(self.Board); bar.SetSize(w, h); bar.SetPosition(x, y); bar.Show()
            self._keep.append(bar)
        except:
            pass
        if center:
            tl = self.comp.TextLine(self.Board, text, x + w // 2, y + 2, self.comp.RGB(*COLOR_TXT))
            try:
                tl.SetHorizontalAlignCenter()
            except:
                pass
        else:
            tl = self.comp.TextLine(self.Board, text, x + tx, y + 2, self.comp.RGB(*COLOR_TXT))
        self._keep.append(tl)

    def _flagToggle(self, x, y, idx):
        def apply():
            try:
                holder['btn'].SetText('On' if self.flags[idx] else 'Off')
                holder['btn'].SetUpVisual(IMG_SMALL[2] if self.flags[idx] else IMG_SMALL[0])
            except:
                pass
        def onclick():
            self.flags[idx] = not self.flags[idx]
            apply()
        holder = {'btn': self.comp.Button(self.Board, 'Off', '', x, y, onclick, *IMG_SMALL)}
        apply()
        self._keep.append(holder['btn'])

    def _onConfirm(self):
        # the engine reads the mask live each frame, so re-applying takes effect immediately
        ah = self.owner._getAutoHunting()
        if ah is not None:
            self.owner._applyAttackFilter(ah)
        self.Board.Hide()

    def _close(self):
        self.Board.Hide()

    def Open(self):
        try:
            self.owner.focusPanel.Board.Hide()   # only one side panel open at a time
        except:
            pass
        try:
            x, y = self.owner.Board.GetGlobalPosition()
            self.Board.SetPosition(int(x) + 251, int(y) + BOARD_H - 258)
        except:
            self.Board.SetPosition(310, 240)
        self.Board.Show()


class AutoHunting(BotBase):

    def __init__(self):
        # onlyGamePhase=False: BotBase.OnUpdate normally gates Frame on Hooks.CURRENT_PHASE==GAME, but
        # that phase global goes stale after a teleport on the walker build (the SetPhaseWindow game
        # re-entry is missed) -> Frame would never run again, killing pots/skills/native-redrive/leash
        # while the native engine self-sustains. We drop the gate and guard in-game ourselves (_inGame).
        BotBase.__init__(self, 0.2, onlyGamePhase=False, waitIsPlayerDead=False)

        self._loadCfg()   # persisted settings -> defaults below fall back to these
        self.autoAttack  = self._cfgBool('autoAttack',  True)
        self.autoRange   = self._cfgBool('autoRange',   True)
        self.autoPotion  = self._cfgBool('autoPotion',  True)
        self.autoSkill   = self._cfgBool('autoSkill',   True)
        self.autoRestart = self._cfgBool('autoRestart', True)

        self.huntRange   = self._cfgInt('range', DEFAULT_RANGE)
        self.hpThreshold = self._cfgInt('hp', 50)
        self.spThreshold = self._cfgInt('sp', 30)

        self.skillSet = []
        self.helperState = []
        self.potionIcons = []
        self._keep = []   # MUST hold refs to TextLine/ExpandedImage or python GC destroys them

        self._nativeOn   = False
        self._lastNativeReq = 0.0
        self._lastPotion = 0.0
        self._lastSkill  = 0.0
        self._lastRevive = 0.0
        self._lastPos = None
        self._stillSince = 0.0
        self._lastApproach = 0.0
        self._anchor = None            # fixed hunt-zone center (anti map-drift); set on Start/confirm
        self._confirmedAnchor = None   # last CONFIRMED center; restored when Focus is toggled back ON
        self._prevFoc = True           # tracks Focus edges to re-apply the leash on OFF->ON
        self._approachTgt = 0
        self._approachGoalPos = None   # last walk-order goal; only re-issue when the target moves (anti-jitter)
        self._approachMinDist = 1e9
        self._noProgressSince = 0.0
        self._approachFails = 0
        self._blacklist = {}           # vid -> expiry time for unreachable targets
        self._castRestartAt = 0.0      # hold the native engine off until this time after a skill cast
        self._leashing = False         # actively pulling back inside the anchored focus zone
        self._toggleDone = set()       # toggle-aura buffs already enabled this life (don't recast -> toggle off)

        self.BuildWindow()
        self.resetSkillsUI()
        self.resetPotionsUI()
        self.rangePreview = RangePreviewWindow(self)
        self.focusPanel = FocusPanel(self)
        self.attackPanel = AttackPanel(self)

    # ---------------------------------------------------------------- UI ----
    def BuildWindow(self):
        c = UIComponents.Component()
        self.comp = c
        self.Board = ui.BoardWithTitleBar()
        self.Board.SetSize(BOARD_W, BOARD_H)
        self.Board.SetPosition(60, 30)
        self.Board.AddFlag('movable')
        self.Board.AddFlag('float')
        self.Board.SetTitleName('Auto-Hunt')
        self.Board.SetCloseEvent(self.switch_state)

        # section headers (official puts these inside horizontalbars; text position is exact)
        self._inputLabel('Skills',   SKILL_BAR_X,   SKILL_BAR_Y,   226, 17, tx=SKILL_TEXT_X,   color=COLOR_HDR)
        self._inputLabel('Potions',  POTION_BAR_X,  POTION_BAR_Y,  226, 17, tx=SKILL_TEXT_X,   color=COLOR_HDR)
        self._inputLabel('Settings', SETTING_BAR_X, SETTING_BAR_Y, 226, 17, tx=SETTING_TEXT_X, color=COLOR_HDR)

        # slot frames (per-slot images; NOT ui.SlotWindow -- it draws over siblings + shows no frame)
        self._buildFrames(SKILL_SLOT_X, SKILL_SLOT_Y, 6)    # Skills: 1 row (2nd row removed -- unused)
        self._buildFrames(POTION_SLOT_X, POTION_SLOT_Y, 18)  # Potions: 3 rows (3rd is empty, for future use)

        # 5 setting rows: centered label (left) + On/Off button (x=194), GF-style
        labels = ['Attack', 'Focus', 'Potions', 'Skills', 'Resurrection']
        funcs  = [self._setAttack, self._setRange, self._setPotion, self._setSkill, self._setRestart]
        defs   = [self.autoAttack, self.autoRange, self.autoPotion, self.autoSkill, self.autoRestart]
        self.toggleHolders = []
        for n in range(5):
            by = AUTO_BTN_BASE_Y + AUTO_BTN_DY * n
            self._inputLabel(labels[n], SETTING_BAR_X + SET_BAR_X, by + 2, 173, 16, center=True)
            self._mkToggle(AUTO_BTN_X, by, defs[n], funcs[n])

        # option arrows: Attack -> filter panel, Focus -> range slider panel (open to the right)
        self.btnAttackOpt = c.Button(self.Board, '', '', AUTO_BTN_X + OPT_BTN_DX + 1, AUTO_BTN_BASE_Y + 1.5, self._openAttackOptions, *IMG_OPT)
        self.btnFocusOpt  = c.Button(self.Board, '', '', AUTO_BTN_X + OPT_BTN_DX + 1, AUTO_BTN_BASE_Y + AUTO_BTN_DY + 1.7, self._openFocusPanel, *IMG_OPT)

        # bottom: Save / Start / End
        self.saveBtn  = c.Button(self.Board, 'Save',  '', SAVE_X,  BOTTOM_Y, self._onSave,  *IMG_BOTTOM)
        self.startBtn = c.Button(self.Board, 'Start', '', START_X, BOTTOM_Y, self._onStart, *IMG_BOTTOM)
        self.endBtn   = c.Button(self.Board, 'Stop',  '', END_X,   BOTTOM_Y, self._onEnd,   *IMG_BOTTOM)
        self._setRunVisual(False)   # stopped by default -> Stop pressed

        self.Board.Hide()

    def _buildFrames(self, x, y, count=12):
        for i in range(count):
            sx, sy = self._slotAbs(x, y, i)
            try:
                self._keep.append(self.comp.ExpandedImage(self.Board, sx, sy, IMG_SLOT_BASE))
            except:
                pass

    def _slotAbs(self, baseX, baseY, idx):
        return baseX + (idx % 6) * SLOT_DX, baseY + (idx // 6) * SLOT_DY

    def _itemIcon(self, vnum):
        try:
            item.SelectItem(vnum)
            return item.GetIconImage()
        except:
            pass
        try:
            return item.GetIconImageFileName()
        except:
            return None

    def _addPotionIcon(self, idx, vnum):
        # item icons only render via SlotWindow.SetItemSlot (GetIconImage returns a handle, not a
        # path). Use a tiny 1-slot SlotWindow per potion -- 32x32, so it won't cover the input below.
        if not vnum:
            return
        sx, sy = self._slotAbs(POTION_SLOT_X, POTION_SLOT_Y, idx)
        try:
            sw = ui.SlotWindow()
            sw.SetParent(self.Board)
            sw.SetPosition(sx, sy)
            sw.SetSize(SLOT_W, SLOT_H)
            sw.AppendSlot(0, 0, 0, SLOT_W, SLOT_H)
            sw.SetItemSlot(0, vnum, 0)
            sw.Show()
            self.potionIcons.append(sw)
        except Exception, e:
            try:
                _dbg("[AH] poticon err: " + str(e))
            except:
                pass

    def _skillState(self, sid, slot):
        # current level + grade (0=normal,1=M,2=G,3=P). player.GetSkillLevel/Grade take the skill
        # VNUM (CE-confirmed: vnum-keyed map lookup), so sid is correct; still fall back to the slot
        # and PREFER whichever arg reports the skill as learned (lv>0 or grade>0) -- returning the
        # first non-raising arg even when it read 0 was dropping learned skills to "unlearned".
        best = (0, 0, sid)
        for arg in (sid, slot):
            try:
                lv = int(player.GetSkillLevel(arg))
            except:
                continue
            gr = 0
            try:
                gr = int(player.GetSkillGrade(arg))
            except:
                pass
            if lv > 0 or gr > 0:
                return lv, gr, arg
            best = (lv, gr, arg)
        return best

    def _isBuffSkill(self, sid):
        # A self-buff = STANDING and NOT ATTACK. skill.IsStandingSkill alone is WRONG: several offensive
        # skills are ATTACK_SKILL|STANDING_SKILL (warrior 18/21, assassin 51, sura 62/77/78) and would
        # be flagged as buffs. Use the static flag sets (client-skilldesc-independent); fall back to the
        # client API only for ids we don't have (7th/horse/guild skills).
        if sid in OpenLib.SKILL_BUFFS:
            return True
        if sid in OpenLib.SKILL_ATTACKS:
            return False
        try:
            return bool(skill.IsStandingSkill(sid))
        except:
            return False

    def _skillNeedsTarget(self, sid):
        # Offensive skills WITHOUT the NEED_TARGET flag (AoE / self-centered, e.g. sura Dragon Swirl,
        # lycan Wolf's Breath) fire with no focused target -> cast them whenever a mob is in range.
        return sid not in OpenLib.SKILL_NO_TARGET_ATTACK

    def _isBow(self):
        # True when the equipped weapon is a bow. Cached ~1s (weapon rarely changes) so the combat hot
        # path stays cheap. OpenLib.IsWeaponArch reads the weapon via the EQUIPMENT window (GetItemIndex(2,
        # EQUIPMENT_WEAPON)) which can silently return 0 on this client; the client's own code reads equip
        # slots via the INVENTORY window + the absolute equip cell (see __HasEnoughArrow). So try BOTH
        # windows here and accept whichever returns the weapon -> reliable bow detection.
        now = OpenLib.GetTime()
        if getattr(self, '_bowChk', 0.0) and now - self._bowChk < 1.0:
            return self._bowCache
        self._bowChk = now
        res = False
        try:
            # [APP] diag PROVED on this client: GetItemIndex(EQUIPMENT, EQUIPMENT_WEAPON) returns the
            # equipped weapon (EQUIPMENT_WEAPON is the LOCAL wear cell = 4 here, NOT 94; the INVENTORY
            # window returns a different slot). We test ONLY the subtype == WEAPON_BOW -- the weapon slot
            # already guarantees it's a weapon, and the old `GetItemType()==ITEM_TYPE_WEAPON` gate FAILED
            # (that module constant != what GetItemType() returns on this build) which is what broke it.
            idx = player.GetItemIndex(getattr(player, 'EQUIPMENT', 2), getattr(item, 'EQUIPMENT_WEAPON', 4))
            if idx:
                item.SelectItem(idx)
                if item.GetItemSubType() == getattr(item, 'WEAPON_BOW', 2):
                    res = True
        except:
            res = False
        self._bowCache = res
        return res

    def _attackRange(self):
        # (enter, stay) engagement distances. A bow shoots from afar -> larger ring so we don't run into
        # melee; every other weapon keeps ATTACK_RANGE/COMBAT_MAX so melee behaviour is unchanged.
        if self._isBow():
            return BOW_ENGAGE, BOW_STAY
        return OpenLib.ATTACK_RANGE, COMBAT_MAX

    def _skillSignature(self):
        # lightweight fingerprint of the current class + which skills are learned. Changes when the
        # class changes OR a skill gets learned (points added) -> used to trigger a skill rebuild.
        try:
            cls = OpenLib.GetClass()
        except:
            return None
        if cls == OpenLib.SKILL_SET_NONE:
            return ('NONE',)
        try:
            ids = OpenLib.GetClassSkillIDs(cls)
        except:
            return (cls,)
        sig = [cls]
        for i, sid in enumerate(ids):
            lv, gr, _a = self._skillState(sid, i + 1)
            sig.append((sid, lv > 0 or gr > 0))
        return tuple(sig)

    def _skillDuration(self, sid, lvlArg, lvl, slot=None):
        # buff duration (sec) via the client's own skill.GetDuration(id, kPower). CE + live [BUFF] log
        # confirmed the kPower MUST come from GetSkillCurrentEfficientPercentage(SLOT) -- feeding it the
        # vnum gives a wrong % and a too-low duration (Aura read 32 vs the real 37). arg2 is a FLOAT
        # power coefficient, NOT the raw level (level-as-k over-extrapolates the curve).
        if lvl <= 0:
            return 0.0
        try:
            k = float(player.GetSkillCurrentEfficientPercentage(slot if slot is not None else lvlArg))
        except:
            k = 0.0
        dur = 0.0
        for args in ((sid, k), (lvlArg, k)):   # k-based only; level-as-k over-extrapolates the curve
            try:
                d = float(skill.GetDuration(*args))
                if d > 0:
                    dur = d
                    break
            except:
                continue
        return dur

    def _hideAllSkillWidgets(self):
        # Hide EVERY skill widget: the flat tracked list AND whatever self.skillSet still references. The
        # skillSet sweep matters right after a /rah -- widgets built by the OLD build aren't in the flat
        # list, and without this they orphan on screen ("previous char's icons stay showing"). Covers
        # toggle/icon/edit + the edit-box background '_sb'.
        widgets = list(getattr(self, '_skillWidgets', []))
        for s in getattr(self, 'skillSet', []):
            try:
                for k in ('toggle', 'icon', 'edit', '_sb'):
                    w = s.get(k)
                    if w is not None:
                        widgets.append(w)
            except:
                pass
        for w in widgets:
            try:
                w.Hide()
            except:
                pass
        self._skillWidgets = []

    def resetSkillsUI(self, force=False):
        # GetClass() reads Data.mainRace/mainSkillGroup, which uBot only refreshes on the PHASE_GAME
        # callback -> stale if the skill group was picked this session (or our callback ran before
        # Data's). Pull straight from the net layer so a freshly-learned class is detected on open.
        try:
            Data.mainRace = net.GetMainActorRace()
            Data.mainSkillGroup = net.GetMainActorSkillGroup()
        except:
            pass
        try:
            cls = OpenLib.GetClass()
        except Exception, e:
            try:
                _dbg("[AH] GetClass err: " + str(e))
            except:
                pass
            return
        # NO SKILL GROUP CHOSEN -> the char has NO active skills yet, so show NOTHING on ANY race until
        # after the choice (per request). GetClass() already returns NONE when mainSkillGroup==0, but we
        # also gate on the raw group so a transient/odd race read can never resolve to another class's
        # icons pre-choice. A learned char always has group != 0.
        if cls == OpenLib.SKILL_SET_NONE or not getattr(Data, 'mainSkillGroup', 0):
            # classless (fresh char, or switched to a low-level char with no skills yet) -> CLEAR the
            # section. Hide EVERY widget we ever made (not just what's in self.skillSet) -- the previous
            # char's icons were staying on screen because a widget (e.g. the edit-box background '_sb', or
            # a widget dropped from skillSet without being hidden) was orphaned.
            self._hideAllSkillWidgets()
            self.skillSet = []
            self._builtClass = cls
            self._builtSig = ('NONE',)
            return
        # Only rebuild the skill widgets when the class actually changed (first build or char switch).
        # On a same-char teleport the widgets are fine and eXLib drives Frame directly, so there's no
        # reason to destroy+recreate them every world reload -- and destroying widgets the client UI
        # may still reference is a use-after-free (GC-crash) risk. Levels refresh live via
        # _refreshSkillDurations. `force` (window open) always rebuilds.
        if self.skillSet and getattr(self, '_builtClass', None) == cls and not force:
            return
        prevOn = {}
        for s in self.skillSet:
            try:
                tgl = s.get('toggle')
                prevOn[s.get('id')] = bool(tgl.isOn) if tgl is not None else False
            except:
                pass
        self._hideAllSkillWidgets()   # hide ALL old widgets (incl. orphans) before building the new class
        self.skillSet = []
        try:
            skillIds = OpenLib.GetClassSkillIDs(cls)
        except Exception, e:
            try:
                _dbg("[AH] GetClassSkillIDs err: " + str(e))
            except:
                pass
            return
        try:
            _dbg("[AH] build cls=%s race=%s grp=%s ids=%s" % (
                str(cls), str(getattr(Data, 'mainRace', '?')),
                str(getattr(Data, 'mainSkillGroup', '?')), str(list(skillIds))))
        except:
            pass
        c = self.comp
        pos = 0
        for i, sid in enumerate(skillIds):
            # show ALL class skills in the slots (learned -> toggle, unlearned -> dimmed icon)
            ix, iy = self._slotAbs(SKILL_SLOT_X, SKILL_SLOT_Y, pos)
            ex = SK_COOL_X + (pos % 6) * SLOT_DX
            ey = SK_COOL_Y + (pos // 6) * SK_COOL_DY
            slot = i + 1
            lvl, grade, lvlArg = self._skillState(sid, slot)
            learned = lvl > 0 or grade > 0   # mastered skills can report level 0 within their grade
            try:
                _dbg("[AH] sk sid=%d slot=%d lv=%d gr=%d %s" % (sid, slot, lvl, grade, 'tgl' if learned else 'dim'))
            except:
                pass
            # icon tier follows the in-game grade: normal -> _01, Master -> _02, Grand/Perfect -> _03.
            # (was hardcoded _03, which is missing for un-mastered skills -> blank icon, e.g. id5.)
            iconGrade = 1 + min(max(grade, 0), 2)
            try:
                icon = OpenLib.GetSkillIconPath(sid, iconGrade)
            except:
                icon = None
            if not icon and sid in SKILL_ICON_FALLBACK:   # skilldesc row missing -> rebuild the path
                folder, name = SKILL_ICON_FALLBACK[sid]
                icon = "d:/ymir work/ui/skill/%s/%s_0%d.sub" % (folder, name, iconGrade)
            if not icon:
                try:
                    _dbg("[AH] icon id%d STILL None (needs SKILL_ICON_FALLBACK)" % sid)
                except:
                    pass
            # lastCast=-1e9 (NOT 0): after a char switch GetTime() resets to a small value, so a fresh
            # 0.0 makes "now - lastCast < dur+2" TRUE -> the buff reads as still-active and is skipped for
            # a whole duration ("buffs stop working after switching character"). A huge-negative stamp is
            # always "due" on (re)build regardless of the clock.
            entry = {'id': sid, 'slot': slot, 'learned': learned, 'level': lvl, 'grade': grade, 'lastCast': -1.0e9}
            if learned:
                entry['toggle'] = c.OnOffButton(self.Board, '', '', ix, iy, image=icon, defaultValue=False)
                self._skillWidgets.append(entry['toggle'])
                # keep toggles across rebuilds (ch switch this session); on first build use the saved
                # persisted state (sk_<id>_on) as the default.
                wantOn = prevOn.get(sid, None)
                if wantOn is None:
                    wantOn = self._cfgBool('sk_%d_on' % sid, False)
                if wantOn:
                    try:
                        if not entry['toggle'].isOn:
                            entry['toggle'].OnChange()
                    except:
                        pass
            else:
                try:
                    entry['icon'] = c.ExpandedImage(self.Board, ix, iy, icon)
                    self._skillWidgets.append(entry['icon'])
                except:
                    pass
            # buff vs offensive from the STANDING-skill flag (not GetDuration>0, which also fires on
            # offensive DoTs). Recast box = the buff duration + 2s; offensive skills show 0 (no recast).
            isBuff = self._isBuffSkill(sid)
            entry['isBuff'] = isBuff
            dur = self._skillDuration(sid, lvlArg, lvl, slot) if (learned and isBuff) else 0.0
            entry['dur'] = dur   # remembered so a toggled buff with a blank recast box can still recast
            defText = str(int(round(dur))) if dur > 0 else '0'   # show the real duration (recast fires ~2s early)
            sb, el = c.EditLine(self.Board, defText, ex, ey, 34, 18, 4)
            entry['edit'] = el
            entry['_sb'] = sb
            self._skillWidgets.append(el)
            self._skillWidgets.append(sb)
            entry['autoText'] = defText   # baseline for the live duration refresh
            # NOTE: no longer restore a persisted sk_<id>_dur into the box -- the box is now a DURATION
            # READOUT (recast timing uses the fresh client duration, not the box), so a stale saved value
            # would just show the wrong number. Always display the freshly-computed duration.
            self.skillSet.append(entry)
            pos += 1
            try:
                _dbg("[AH] skill sid=%d slot=%d lvl=%d grade=%d dur=%.1f" % (sid, slot, lvl, grade, dur))
            except:
                pass
        try:
            _dbg("[AH] skills built: %d" % len(self.skillSet))
        except:
            pass
        self._builtClass = cls
        self._builtSig = self._skillSignature()

    def resetPotionsUI(self, force=False):
        # Build potion widgets once; don't churn them on every teleport (same reasoning + UAF risk as
        # resetSkillsUI). `force` (window open) rebuilds.
        if getattr(self, '_potionsBuilt', False) and not force:
            return
        c = self.comp
        for w in getattr(self, 'potionIcons', []):
            try:
                w.Hide()
            except:
                pass
        self.potionIcons = []
        for h in self.helperState:
            try:
                h['label'].Hide()
            except:
                pass
        self.helperState = []
        try:
            self._addPotionIcon(0, list(Settings.instance.RED_POTIONS_IDS)[0])
        except:
            pass
        try:
            self._addPotionIcon(1, list(Settings.instance.BLUE_POTIONS_IDS)[0])
        except:
            pass
        if not hasattr(self, 'editHP'):
            self.slotHP, self.editHP = c.EditLine(self.Board, str(self.hpThreshold), PO_COOL_X, PO_COOL_Y, 22, 18, 3)
            self._keep.append(c.TextLine(self.Board, '%', PO_COOL_X + 25, PO_COOL_Y + 2, c.RGB(*COLOR_TXT)))
            self.slotSP, self.editSP = c.EditLine(self.Board, str(self.spThreshold), PO_COOL_X + SLOT_DX, PO_COOL_Y, 22, 18, 3)
            self._keep.append(c.TextLine(self.Board, '%', PO_COOL_X + SLOT_DX + 25, PO_COOL_Y + 2, c.RGB(*COLOR_TXT)))
            # Empty placeholder inputs for every OTHER potion slot across all 3 rows (HP=slot0, SP=slot1
            # already have theirs). Start after any helper slots so they never overlap the helper inputs
            # below. Same "create once" lifetime as HP/SP (kept via emptyPotInputs; rebuilt on /rah-ui via
            # the delattr in _rebuildWindow). Values persist through pot_<idx>_val in _onSave/_loadCfg.
            self.emptyPotInputs = []
            _firstEmpty = 2 + len(HELPER_ITEMS[:10])
            for idx in range(_firstEmpty, 18):
                lx = PO_COOL_X + (idx % 6) * SLOT_DX
                ly = PO_COOL_Y + (idx // 6) * PO_COOL_DY
                sb, el = c.EditLine(self.Board, '', lx, ly, 22, 18, 5)
                saved = self._cfg.get('pot_%d_val' % idx)
                if saved is not None:
                    try: el.SetText(saved)
                    except: pass
                self.emptyPotInputs.append({'slotIdx': idx, 'edit': el, '_sb': sb})
        for n, hentry in enumerate(HELPER_ITEMS[:10]):
            idx = 2 + n
            vnum = (hentry.get('ids') or [0])[0]
            self._addPotionIcon(idx, vnum)
            lx = PO_COOL_X + (idx % 6) * SLOT_DX
            ly = PO_COOL_Y + (idx // 6) * PO_COOL_DY
            sb, el = c.EditLine(self.Board, str(hentry.get('time', 1)), lx, ly, 22, 18, 5)
            saved = self._cfg.get('helper_%d_time' % idx)   # restore persisted interval
            if saved is not None:
                try:
                    el.SetText(saved)
                except:
                    pass
            self._keep.append(c.TextLine(self.Board, 's', lx + 24, ly, c.RGB(*COLOR_TXT)))
            self.helperState.append({'entry': hentry, 'slotIdx': idx, 'lastUse': 0.0, 'edit': el, '_sb': sb})
        self._potionsBuilt = True

    # --------------------------------------------------------- toggles ----
    def _setAttack(self, val):
        self.autoAttack = val
        if not val:
            self._stopNative()
    def _setRange(self, val):
        # Toggling Focus live: ON -> (re)anchor the zone here so the leash confines us; OFF -> drop the
        # anchor + leash so we hunt anywhere unrestricted. Mirrors StartBot's autoRange handling.
        self.autoRange = val
        self._leashing = False
        if val:
            try:
                self._anchor = self._pos(player.GetMainCharacterIndex())
            except:
                self._anchor = None
        else:
            self._anchor = None
    def _setPotion(self, val):  self.autoPotion  = val
    def _setSkill(self, val):   self.autoSkill   = val
    def _setRestart(self, val): self.autoRestart = val

    def _mkToggle(self, x, y, default, setter):
        # GF-style On/Off button (Small_Button whose label flips). Off shows the pressed-in (down)
        # image as its idle visual, On shows the normal raised image.
        holder = {'on': bool(default), 'btn': None}
        def apply():
            try:
                holder['btn'].SetText('On' if holder['on'] else 'Off')
                # On = pressed-in (down image), Off = normal (raised)
                holder['btn'].SetUpVisual(IMG_SMALL[2] if holder['on'] else IMG_SMALL[0])
            except:
                pass
        def onclick():
            holder['on'] = not holder['on']
            apply()
            try:
                setter(holder['on'])
            except:
                pass
        btn = self.comp.Button(self.Board, 'On' if default else 'Off', '', x, y, onclick, *IMG_SMALL)
        holder['btn'] = btn
        apply()
        self.toggleHolders.append(holder)
        return holder

    def _inputLabel(self, text, x, y, w, h, tx=6, color=None, center=False):
        # non-editable SlotBar (same beveled input box as the % fields) with the label text inside
        try:
            bar = ui.SlotBar()
            bar.SetParent(self.Board)
            bar.SetSize(w, h)
            bar.SetPosition(x, y)
            bar.Show()
            self._keep.append(bar)
        except:
            pass
        col = color if color is not None else COLOR_TXT
        if center:
            tl = self.comp.TextLine(self.Board, text, x + w // 2, y + 2, self.comp.RGB(*col))
            try:
                tl.SetHorizontalAlignCenter()
            except:
                pass
        else:
            tl = self.comp.TextLine(self.Board, text, x + tx, y + 2, self.comp.RGB(*col))
        self._keep.append(tl)
        return tl

    def _openAttackOptions(self):
        # arrow toggles its side window: open if closed, close (acts like the X) if already open
        try:
            p = self.attackPanel
            p.Board.Hide() if p.Board.IsShow() else p.Open()
        except:
            pass

    def _openFocusPanel(self):
        try:
            p = self.focusPanel
            p.Board.Hide() if p.Board.IsShow() else p.Open()
        except:
            pass

    def _readSettings(self):
        self.hpThreshold = self._toInt(self.editHP.GetText(),   self.hpThreshold)
        self.spThreshold = self._toInt(self.editSP.GetText(),   self.spThreshold)

    @staticmethod
    def _toInt(txt, default):
        try:
            return int(str(txt).strip())
        except:
            return default

    def _onStart(self):
        self._readSettings()
        self.Start()
        self._setRunVisual(True)

    def _onEnd(self):
        self.Stop()
        self._setRunVisual(False)

    def _setRunVisual(self, running):
        # Start/Stop behave like On/Off: the active one is pressed-in, only one at a time
        try:
            self.startBtn.SetUpVisual(IMG_BOTTOM[2] if running else IMG_BOTTOM[0])
            self.endBtn.SetUpVisual(IMG_BOTTOM[2] if not running else IMG_BOTTOM[0])
        except:
            pass

    # -------------------------------------------------- config persistence ----
    def _loadCfg(self):
        # read the persisted settings file into a flat {key: str} dict (missing file -> empty)
        self._cfg = {}
        try:
            f = open(CONFIG_AH, 'r')
            for line in f:
                line = line.strip()
                if '=' in line:
                    k, v = line.split('=', 1)
                    self._cfg[k] = v
            f.close()
        except:
            pass

    def _cfgBool(self, key, default):
        v = self._cfg.get(key)
        return default if v is None else (v in ('1', 'True', 'true'))

    def _cfgInt(self, key, default):
        v = self._cfg.get(key)
        try:
            return int(v)
        except:
            return default

    def _onSave(self):
        self._readSettings()
        c = getattr(self, '_cfg', {})
        c['autoAttack']  = '1' if self.autoAttack  else '0'
        c['autoRange']   = '1' if self.autoRange   else '0'
        c['autoPotion']  = '1' if self.autoPotion  else '0'
        c['autoSkill']   = '1' if self.autoSkill   else '0'
        c['autoRestart'] = '1' if self.autoRestart else '0'
        c['range'] = str(self.huntRange)
        c['hp'] = str(self.hpThreshold)
        c['sp'] = str(self.spThreshold)
        try:   # attack filter: 7 category flags + player-level-diff range
            for i, fl in enumerate(self.attackPanel.flags):
                c['flag%d' % i] = '1' if fl else '0'
            c['lvlMinus'] = str(self._toInt(self.attackPanel.editMinus.GetText(), 15))
            c['lvlPlus']  = str(self._toInt(self.attackPanel.editPlus.GetText(), 15))
        except:
            pass
        try:   # per-skill toggle + recast duration, keyed by skill id (class-agnostic)
            for s in self.skillSet:
                tg = s.get('toggle')
                c['sk_%d_on' % s['id']] = '1' if (tg is not None and getattr(tg, 'isOn', False)) else '0'
                c['sk_%d_dur' % s['id']] = str(s['edit'].GetText())
        except:
            pass
        try:   # helper-consumable interval per slot
            for h in self.helperState:
                c['helper_%d_time' % h['slotIdx']] = str(h['edit'].GetText())
        except:
            pass
        try:   # empty potion-slot inputs (placeholders) -> keep whatever the user typed
            for p in getattr(self, 'emptyPotInputs', []):
                c['pot_%d_val' % p['slotIdx']] = str(p['edit'].GetText())
        except:
            pass
        self._cfg = c
        try:
            f = open(CONFIG_AH, 'w')
            for k in sorted(c.keys()):
                f.write('%s=%s\n' % (k, c[k]))
            f.close()
            _dbg("[AH] saved %d keys" % len(c))
        except:
            pass

    # ----------------------------------------------------- BotBase hooks ----
    def StartBot(self):
        self._stopNative()          # clean stop first so a stuck engine gets a fresh SendRequest(1)
        self._lastNativeReq = 0.0
        self._nativeOn = False
        self._leashing = False
        self._castRestartAt = 0.0   # clear any stale cast-hold that would keep _startNative gated off
        self._blacklist = {}
        self._approachTgt = 0       # clear stale approach/unstuck state (was a "bricked after restart")
        self._approachFails = 0
        self._noProgressSince = 0.0
        self._huntTarget = 0        # custom engine: our chosen attack target
        self._lastSwing = 0.0
        self._lastAcquire = 0.0
        self._inMelee = False       # melee-hysteresis state (attacking vs approaching)
        self._handedOff = False     # hybrid: char handed to the native engine for the animated attack
        self._toggleDone = set()    # re-enable toggle auras on a fresh Start
        # FOCUS(range) ON -> anchor the hunt zone here so the leash + zone confine us to huntRange. FOCUS
        # OFF -> NO anchor: no leash, no zone cap, no distance cap -> hunt anywhere unrestricted (matches
        # the official auto-hunt's Focus toggle). autoRange is re-applied live in _setRange too.
        self._leashing = False
        _startPos = self._pos(player.GetMainCharacterIndex())
        self._anchor = _startPos if self.autoRange else None
        self._confirmedAnchor = _startPos     # remember it so a later Focus ON re-anchors here
        self._prevFoc = self.autoRange
        if self.autoAttack and not USE_CUSTOM_ENGINE:
            self._startNative()

    def StopBot(self):
        self._stopNative()

    # ------------------------------------------------ native auto-hunt drive ----
    def _getAutoHunting(self):
        global autoHunting
        if autoHunting is not None:
            return autoHunting
        for mn, m in iter(sys.modules.items()):
            try:
                if m is not None and buildin.hasattr(m, 'SendRequestAutoHuntingOnoff'):
                    autoHunting = m
                    return m
            except:
                continue
        return None

    def _rangeUnits(self):
        return max(RANGE_MIN_U, min(RANGE_MAX_U, self.huntRange))

    def _applyAttackFilter(self, ah):
        # The attackable-category bitmask is client-side (singleton+0x58); the engine reads it every
        # frame. ClearAttackableMonsterOption is a MISNOMER -> it turns ALL 7 bits ON, and
        # SetAttackableMonsterFlag can only OR bits in. So to honor the checkboxes: start all-on then
        # Remove the unchecked categories (RemoveAttackableMonsterFlag does mask &= ~(1<<i)).
        try:
            ah.ClearAttackableMonsterOption()
        except:
            pass
        flags = getattr(self.attackPanel, 'flags', None) or [True] * 7
        for i in range(7):
            if not flags[i]:
                try:
                    ah.RemoveAttackableMonsterFlag(i)
                except:
                    pass
        try:
            lvl = int(player.GetStatus(player.LEVEL))
            ap = self.attackPanel
            minus = self._toInt(ap.editMinus.GetText(), 0)
            plus  = self._toInt(ap.editPlus.GetText(), 0)
            ah.SetAttackAbleMonsterMinLevel(max(1, lvl - minus))
            ah.SetAttackAbleMonsterMaxLevel(lvl + plus)
        except:
            pass

    def _startNative(self):
        # Re-apply every tick (throttled) until the native attack function is CONFIRMED on. The
        # native Set* calls silently no-op until the auto-hunt subsystem is ready, and the engine
        # only swings once func 0 (engine) AND func 1 (attack) are both on -- doing this once at
        # Start was why uBot used to need the GF window opened first. SendRequest (server auth)
        # fires once; everything else is client-side singleton state so re-applying is cheap.
        now = OpenLib.GetTime()
        if now < self._castRestartAt:
            return   # a skill cast is in progress -> keep the engine off until the anim finishes
        if self._leashing:
            return   # outside the zone -> engine stays off while we walk back (see _navAssist)
        if now - self._lastNativeReq < NATIVE_TICK:
            return
        self._lastNativeReq = now
        ah = self._getAutoHunting()
        if ah is None:
            return
        self._applyAttackFilter(ah)
        for f in (AH_FUNC_ENGINE, AH_FUNC_ATTACK):
            try:
                ah.SetFunctionOnOff(f, 1)
            except:
                pass
        try:
            if self.autoRange:
                ah.SetHuntingRange(self._rangeUnits())
                ah.SetFunctionOnOff(AH_FUNC_RANGE, 1)
            else:
                ah.SetFunctionOnOff(AH_FUNC_RANGE, 0)
        except:
            pass
        try:
            if not self._nativeOn and ah.CanStartAutoHunting():
                ah.SendRequestAutoHuntingOnoff(1)
        except:
            pass
        try:
            self._nativeOn = bool(ah.IsAutoHuntingFunctionOn(AH_FUNC_ATTACK))
        except:
            self._nativeOn = True

    def _stopNative(self):
        ah = self._getAutoHunting()
        if ah is None:
            self._nativeOn = False
            return
        try:
            ah.SetFunctionOnOff(AH_FUNC_ATTACK, 0)
        except:
            pass
        try:
            ah.SendRequestAutoHuntingOnoff(0)
        except:
            pass
        self._nativeOn = False

    # ------------------------------------------------------- the engine ----
    def onReenter(self):
        # Called by eXLib on world re-entry (teleport / char-switch). Clear stale per-world state and
        # rebase timers. Do NOT rebuild the skill/potion widgets here -- the world is still loading and
        # churning widgets during the load corrupts the client GC (use-after-free crash on char-switch).
        # Mark it dirty + record the transition time; the stable-gated check (RangePreviewWindow) does
        # the rebuild once the map has settled.
        now = OpenLib.GetTime()
        try:
            self._approachTgt = 0
            self._blacklist = {}
            self._anchor = None
            self._confirmedAnchor = None    # old center is meaningless on a new map -> re-establish here
            self._lastPos = None
            self._castRestartAt = 0.0
            self._nativeOn = False
            self._leashing = False
            self._inMelee = False
            self._huntTarget = 0
            self._buffParkId = None          # drop any in-flight buff-park deadline from the old world
            self._toggleDone = set()         # on/off auras don't carry across a char switch -> re-enable
            self._rebaseTimers(now)          # GetTime reset on this map-load -> rebase throttles
            self._mapChangedAt = now         # transition timestamp (settle gate)
            self._skillsDirty = True         # rebuild skills/potions once stable
        except:
            pass
        try:
            self.rangePreview._attached = False
            # GetTime() reset on this map-load: the refresh throttle stamp is from the old (large)
            # timeline, so "now - _lastSkChk > 1.0" stays false for ~1-2min and the rebuild never fires.
            self.rangePreview._lastSkChk = 0.0
            self.rangePreview._lastMap = None    # force the settle-gate to re-arm for the new world
        except:
            pass

    def _rebaseTimers(self, now):
        # app.GetTime() RESETS/jumps backward on map-load (teleport). Our throttle stamps are from the
        # previous world (large), so every "now - _lastX < TICK" gate blocks for ~1-2min until real
        # time climbs GetTime() back past them -> skills/pots/nav all frozen while native attack (self-
        # sustaining) keeps going. Rebase every stamp onto the new timeline so nothing stays blocked.
        for a in ('_lastHb', '_lastSkill', '_lastNativeReq', '_lastPotion', '_lastApproach',
                  '_lastRevive', '_lastSkDbg', '_lastDurRefresh', '_lastPotDbg', '_castRestartAt',
                  '_lastBuffCastAt', '_lastCbDbg', '_lastTickDbg', '_bowChk', '_lastBowDbg',
                  '_lastBuffDbg', '_reviveGraceUntil'):
            setattr(self, a, 0.0)
        for a in ('_stillSince', '_noProgressSince', '_deadSince'):
            setattr(self, a, now)
        # _lastOffCast is a "last offensive cast" stamp; leaving it huge (old timeline) makes the buff's
        # "wait for the offensive animation" gate think a skill is FOREVER mid-animation after a switch ->
        # buff parks + returns -> offensive never runs -> "no skills at all after switching character".
        # A huge-negative value = "no recent offensive" = no wait.
        self._lastOffCast = -1.0e9
        try:
            # force buffs to re-cast immediately on the new map: lastCast=0 would make "now - 0 < dur"
            # true (small now after the reset) and skip the buff for ~its whole duration.
            for s in self.skillSet:
                s['lastCast'] = -1.0e9
        except:
            pass

    # NOTE: no OnUpdate override -- eXLib's callAutoHunting("OnUpdate") reaches BotBase.OnUpdate -> Frame
    # -> _tick, which drives the skill/potion window refresh (stable-gated, in-game only). Driving
    # rangePreview.OnUpdate from an every-frame OnUpdate override churned widgets DURING world-load and
    # crashed the client GC (_PyObject_GC_UNTRACK on char-switch).

    def Frame(self):
        try:
            self._tick()
        except Exception:
            pass

    def _isPlayerDead(self):
        # HP<=0 (with stats loaded) = dead. BUT during a portal/map transition HP momentarily reads 0
        # while stats are still valid -> a spurious "dead" that fired a bogus revive/restart on
        # teleport. Guard it: require HP<=0 to persist ~1.5s before treating it as a real death.
        dead = False
        try:
            if int(player.GetStatus(player.MAX_HP)) > 0 and int(player.GetStatus(player.HP)) <= 0:
                dead = True
        except:
            pass
        if not dead:
            try:
                dead = bool(eXLib.IsDead(player.GetMainCharacterIndex()))
            except:
                dead = False
        now = OpenLib.GetTime()
        if not dead:
            self._deadSince = 0.0
            return False
        if getattr(self, '_deadSince', 0.0) <= 0.0:
            self._deadSince = now
            return False   # just saw HP<=0 -> wait to confirm it's a real death, not a load transient
        return (now - self._deadSince) >= 1.5

    def _autoPotActive(self, slot):
        # slot 0 = HP, slot 1 = SP. GetAutoPotionInfo returns (activeByte, curPool, maxPool, ...).
        # Require the active flag AND a non-empty pool: on a character switch the client can carry the
        # PREVIOUS char's auto-pot slot for a moment (stale active flag) -> without the pool check that
        # would wrongly suppress our %-potions on the new char forever (the "dead potions" bug).
        try:
            info = player.GetAutoPotionInfo(slot)
            return bool(info) and bool(info[0]) and len(info) > 1 and int(info[1]) > 0
        except:
            return False

    def _inGame(self):
        # Robust in-game check that does NOT depend on Hooks.CURRENT_PHASE -- the net.SetPhaseWindow
        # hook misses the game-phase re-entry on this walker build (login AND teleport), leaving the
        # phase global stuck non-GAME so BotBase.OnUpdate would never call Frame again after a warp.
        # The background map name is empty outside the world and set once the map is loaded.
        try:
            if not background.GetCurrentMapName():
                return False
        except:
            pass
        try:
            return player.GetMainCharacterIndex() != 0
        except:
            return True

    def _tick(self):
        if not self._inGame():
            return
        now0 = OpenLib.GetTime()
        # app.GetTime() jumps backward on map-load (teleport) -> rebase all throttle stamps onto the
        # new timeline, otherwise every "now - _lastX < TICK" gate blocks for ~1-2min (skills/pots/nav
        # frozen) until real time climbs back. This is THE teleport-dead-zone fix.
        if now0 < getattr(self, '_lastNow', 0.0) - 1.0:
            self._rebaseTimers(now0)
        self._lastNow = now0
        mainVID = player.GetMainCharacterIndex()
        if self._isPlayerDead():
            self._wasDead = True       # remember, so we can hold off attacking for a grace period on revive
            self._nativeOn = False
            self._huntTarget = 0
            self._toggleDone = set()   # auras drop on death -> re-enable them after revive
            if self.autoRestart:
                now = OpenLib.GetTime()
                if now - self._lastRevive > REVIVE_TICK:
                    self._lastRevive = now
                    try:
                        _dbg("[AH] dead -> revive")
                    except:
                        pass
                    try:
                        # OpenLib.Revive() runs player.SetAttackKeyState first, which is DEAD on GF
                        # (raises) so the restart packet was never sent. Send "restart here" directly.
                        net.SendCommandPacket(net.PLAYER_CMD_RESTART, 1)
                    except:
                        pass
            return
        # JUST REVIVED (dead last tick, alive now) -> hold off ATTACKING for REVIVE_GRACE so we don't
        # instantly re-engage with ~0 HP and die in a loop. Potions/skills keep running so HP recovers
        # during the grace (only _customCombat's engagement is gated, below).
        if getattr(self, '_wasDead', False):
            self._wasDead = False
            self._reviveGraceUntil = now0 + REVIVE_GRACE
            self._huntTarget = 0
            self._inMelee = False
            try:
                _dbg("[AH] revived -> %.0fs grace before attacking" % REVIVE_GRACE)
            except:
                pass
        self._updateMotion()
        if AH_DEBUG and (now0 - getattr(self, '_lastTickDbg', 0.0) > 2.0):
            self._lastTickDbg = now0
            mnt = '?'
            try: mnt = int(player.IsMountingHorse())
            except: pass
            try:
                _dbg("[TICK] aa=%s mvid=%s park=%.1f melee=%s tgt=%s mount=%s" % (
                    int(self.autoAttack), mainVID, max(0.0, getattr(self, '_castRestartAt', 0.0) - now0),
                    int(getattr(self, '_inMelee', False)), getattr(self, '_huntTarget', 0), mnt))
            except:
                pass
        if self.autoAttack:
            if USE_CUSTOM_ENGINE:
                self._customCombat(mainVID)   # uBot picks + approaches + attacks (no native engine)
            else:
                self._startNative()   # throttled internally; keeps re-applying until func1 confirmed on
                if HYBRID_STEER:
                    self._hybridSteer(mainVID)
                self._navAssist()
        elif self._nativeOn:
            self._stopNative()
        if self.autoPotion:
            self._doPotions()
        if self.autoSkill:
            self._doSkills(mainVID)
            self._refreshSkillDurations()
        # Skill/potion window refresh (level-up / char-switch) -- driven HERE (the in-game-guarded frame
        # already bailed above if not in-world) instead of an every-frame OnUpdate, so it can never
        # churn widgets mid-world-load. Extra settle margin past the last map change; rebuild inside is
        # itself stable-gated + throttled.
        if (now0 - getattr(self, '_mapChangedAt', 0.0)) > 3.0:
            try:
                self.rangePreview.OnUpdate()
            except:
                pass

    def _findNearestMob(self, mainVID):
        best_vid = 0
        best_dist = self.huntRange if self.autoRange else 1e9
        try:
            vids = list(eXLib.InstancesList)
        except:
            return 0
        for vid in vids:
            if vid == mainVID:
                continue
            try:
                if eXLib.IsDead(vid):
                    continue
                chr.SelectInstance(vid)
                if chr.GetInstanceType(vid) != OpenLib.MONSTER_TYPE:
                    continue
                d = player.GetCharacterDistance(vid)
            except:
                continue
            if d < best_dist:
                best_dist = d
                best_vid = vid
        return best_vid

    def _doPotions(self):
        now = OpenLib.GetTime()
        if now - self._lastPotion < POTION_TICK:
            return
        self._lastPotion = now
        # read thresholds LIVE from the edit boxes each tick -> survives ch-switch / reload without
        # relying on _readSettings having run (that was the "not reliable" part).
        hpT = self.hpThreshold
        spT = self.spThreshold
        try:
            hpT = self._toInt(self.editHP.GetText(), hpT)
            spT = self._toInt(self.editSP.GetText(), spT)
        except:
            pass
        # Fire %-potions purely off the HP/SP thresholds. We USED to also suppress them while an auto-pot
        # Elixir (Sun/Moon) read "active" via GetAutoPotionInfo, but that flag false-positived (stale slot
        # after a char switch / world reload -> thinks an HP elixir is running when none is) and killed
        # potting entirely -- the regression in the screenshot. It was also redundant: if the Elixir keeps
        # the bar up, HP/SP stays above the threshold so no %-pot fires anyway; if the bar drops below the
        # threshold the Elixir isn't coping and we SHOULD pot. So threshold alone is both correct and safe.
        try:
            maxhp = float(player.GetStatus(player.MAX_HP))
            hp = float(player.GetStatus(player.HP))
            if maxhp > 0 and hpT > 0 and (hp / maxhp * 100.0) < hpT:
                OpenLib.UseAnyItemByID(Settings.instance.RED_POTIONS_IDS)
        except:
            pass
        try:
            maxsp = float(player.GetStatus(player.MAX_SP))
            sp = float(player.GetStatus(player.SP))
            if maxsp > 0 and spT > 0 and (sp / maxsp * 100.0) < spT:
                OpenLib.UseAnyItemByID(Settings.instance.BLUE_POTIONS_IDS)
        except:
            pass
        for h in self.helperState:
            entry = h['entry']
            t = self._toInt(h['edit'].GetText(), entry.get('time', 0))
            if t <= 0:
                continue
            # 'cooldown' = item effect duration -> re-use 10s after it expires; 'interval' = every t
            interval = (t + 10) if entry.get('type') == 'cooldown' else t
            if now - h['lastUse'] >= interval:
                try:
                    used = OpenLib.UseAnyItemByID(entry.get('ids', []))
                except:
                    used = False
                if used:
                    h['lastUse'] = now

    def _updateMotion(self):
        # Track movement so other logic can tell "moving" from "stationary". _stillSince = the time
        # of the last detected movement.
        now = OpenLib.GetTime()
        try:
            pos = player.GetMainCharacterPosition()
            x, y = float(pos[0]), float(pos[1])
        except:
            return
        prev = self._lastPos
        self._lastPos = (x, y)
        if prev is None:
            self._stillSince = now
            return
        dx, dy = x - prev[0], y - prev[1]
        if (dx * dx + dy * dy) > 4.0:
            self._stillSince = now

    def _zoneRadius(self):
        return self.huntRange + 300   # small slack beyond the hunt range so edge targets are reachable

    def _navAssist(self):
        # Drive the movement the native engine won't:
        #   1) LEASH  -> if we've drifted outside the anchored zone, walk back to the anchor (no map
        #               drift over hours; the circle stays where it was set, GF-style).
        #   2) APPROACH a focused, in-zone, out-of-range target with collision-aware pathing.
        #   3) UNSTUCK -> if we stop making progress (an entity-collision obstacle the pathfinder
        #               can't see), nudge sideways; after a few fails BLACKLIST the target and head
        #               back to the zone so the engine re-focuses a reachable one (fixes the brick).
        now = OpenLib.GetTime()
        if now < self._castRestartAt:
            return   # don't drive movement while a skill cast is finishing
        try:
            p = player.GetMainCharacterPosition()
            px, py = float(p[0]), float(p[1])
        except:
            return
        # 1) LEASH -- checked EVERY tick (NOT behind the approach throttle). A fast class covers a lot
        # of ground in the 1.5s throttle window, so the engine must be stopped the INSTANT we cross the
        # circle or it runs way outside. Re-issue the walk-back throttled (don't re-path every frame).
        if self._anchor is not None:
            ax, ay = self._anchor
            d2 = (px - ax) ** 2 + (py - ay) ** 2
            R = float(self.huntRange)
            if not self._leashing and d2 > R * R:
                self._leashing = True
                self._stopNative()
                self._lastApproach = 0.0   # walk back immediately
            if self._leashing:
                if d2 <= (R * 0.5) ** 2:
                    self._leashing = False   # back well inside -> _startNative re-enables next tick
                else:
                    if now - self._lastApproach >= APPROACH_TICK:
                        self._lastApproach = now
                        try:
                            Movement.GoToPositionAvoidingObjects(ax, ay)
                        except:
                            pass
                    return
        # 2/3) APPROACH a focused, in-zone, out-of-range target + UNSTUCK -- throttled.
        if now - self._lastApproach < APPROACH_TICK:
            return
        self._lastApproach = now
        try:
            tvid = player.GetTargetVID()
        except:
            tvid = 0
        if not tvid or eXLib.IsDead(tvid):
            self._approachTgt = 0
            return
        if self._blacklist.get(tvid, 0.0) > now:
            return
        try:
            dist = player.GetCharacterDistance(tvid)
        except:
            return
        if dist <= OpenLib.ATTACK_RANGE:
            self._approachTgt = 0
            return
        if (now - self._stillSince) < STUCK_SECS:
            return   # the engine is still moving us -> don't interfere
        try:
            tx, ty, tz = eXLib.GetPixelPosition(tvid)
        except:
            return
        if self._anchor is not None:
            ax, ay = self._anchor
            if (tx - ax) ** 2 + (ty - ay) ** 2 > self._zoneRadius() ** 2:
                return   # target outside the anchored zone -> ignore (anti-drift)
        if tvid != self._approachTgt:
            self._approachTgt = tvid
            self._approachMinDist = dist
            self._noProgressSince = now
            self._approachFails = 0
        elif dist < self._approachMinDist - 50:
            self._approachMinDist = dist
            self._noProgressSince = now
        if now - self._noProgressSince > 3.0:     # not getting closer -> obstacle
            self._noProgressSince = now
            self._approachFails += 1
            if self._approachFails >= 3:
                self._blacklist[tvid] = now + 15.0
                self._approachTgt = 0
                try:
                    if self._anchor is not None:
                        Movement.GoToPositionAvoidingObjects(self._anchor[0], self._anchor[1])
                except:
                    pass
                return
            self._nudge(px, py, tx, ty)
            return
        # Path to a REACHABLE point just inside attack range of the target, NOT its center cell -- a
        # metin/mob cell is blocked collision, so pathing to (tx,ty) fails and the char stops dead at a
        # tree. Aiming short lets the collision-aware pathfinder route AROUND the obstacle to open
        # ground within range (fixes "focuses a blocked metin, walks, stops, never reaches/attacks").
        dx, dy = px - tx, py - ty
        L = (dx * dx + dy * dy) ** 0.5 or 1.0
        r = OpenLib.ATTACK_RANGE * 0.8
        gx, gy = tx + (dx / L) * r, ty + (dy / L) * r
        try:
            Movement.GoToPositionAvoidingObjects(gx, gy)
        except:
            pass

    def _nudge(self, px, py, tx, ty):
        # step ~5m perpendicular to the target to slip around an invisible (entity) obstacle
        dx, dy = tx - px, ty - py
        L = (dx * dx + dy * dy) ** 0.5 or 1.0
        s = 1.0 if (self._approachFails % 2) else -1.0
        nx, ny = px + (-dy / L) * s * 500.0, py + (dx / L) * s * 500.0
        try:
            Movement.GoToPositionAvoidingObjects(nx, ny)
        except:
            pass

    def _hybridSteer(self, mainVID):
        # HYBRID: keep the native engine (reliable attack + facing) but STEER its target -- focus the
        # nearest in-zone mob ourselves each tick. If the engine attacks the client's focused target,
        # this fixes it grabbing border/outside-leash mobs. (Live test: does SetTarget override the
        # engine's own pick?) Don't fight a valid in-range focus; only re-point when ours is nearer.
        now = OpenLib.GetTime()
        if now < self._castRestartAt:
            return   # a buff cast is parked -> don't touch targeting
        if now - getattr(self, '_lastSteer', 0.0) < STEER_TICK:
            return
        self._lastSteer = now
        nv = self._acquireTarget(mainVID, now)   # nearest live monster inside the anchored zone
        if not nv:
            return
        try:
            cur = player.GetTargetVID()
        except:
            cur = 0
        if nv == cur:
            return
        # keep a currently-focused, in-range, in-zone target (avoid thrash); only override if ours is
        # meaningfully closer or the current focus is invalid.
        if cur and not eXLib.IsDead(cur):
            try:
                if self._validTarget(cur, now) and player.GetCharacterDistance(cur) <= OpenLib.ATTACK_RANGE:
                    if player.GetCharacterDistance(nv) >= player.GetCharacterDistance(cur) - 100:
                        return
            except:
                pass
        try:
            player.SetTarget(nv)
        except:
            pass

    def _pos(self, vid):
        # Position of an instance as (x, y), or None. The NO-ARG player.GetMainCharacterPosition() is broken on this
        # client (raises even after SelectInstance -> the custom-engine no-op). The working forms (proven
        # in Settings.py, and same coord space there): player.GetMainCharacterPosition() for our OWN char,
        # eXLib.GetPixelPosition(vid) for any other instance.
        try:
            if vid and vid == player.GetMainCharacterIndex():
                p = player.GetMainCharacterPosition()
            else:
                p = eXLib.GetPixelPosition(vid)
            return (float(p[0]), float(p[1]))
        except:
            return None

    def _ensureNativeAttack(self, now):
        # HYBRID: keep the native auto-hunt engine ON with a SMALL engage range -> it performs the
        # ANIMATED melee (approach + swing) that a pure-packet attack cannot (SetAttackKeyState is dead,
        # client attack-motion fn not exposed). Re-applied every NATIVE_TICK until func-attack confirms
        # on (the Set* calls no-op until the subsystem is ready). Off during buff casts + leash walk-back.
        if now < self._castRestartAt or self._leashing:
            return
        if now - self._lastNativeReq < NATIVE_TICK:
            return
        self._lastNativeReq = now
        ah = self._getAutoHunting()
        if ah is None:
            return
        self._applyAttackFilter(ah)
        for f in (AH_FUNC_ENGINE, AH_FUNC_ATTACK):
            try:
                ah.SetFunctionOnOff(f, 1)
            except:
                pass
        try:
            ah.SetHuntingRange(NATIVE_ENGAGE_RANGE)
            ah.SetFunctionOnOff(AH_FUNC_RANGE, 1)
        except:
            pass
        try:
            if not self._nativeOn and ah.CanStartAutoHunting():
                ah.SendRequestAutoHuntingOnoff(1)
        except:
            pass
        try:
            self._nativeOn = bool(ah.IsAutoHuntingFunctionOn(AH_FUNC_ATTACK))
        except:
            self._nativeOn = True

    def _customCombat(self, mainVID):
        # HYBRID combat: uBot picks the NEAREST mob + walks the char to it; the native engine (small
        # engage range) does the ANIMATED approach+swing. uBot's navigation feeds the engine its target;
        # the small range keeps the engine's category-priority pick from running off to far mobs.
        now = OpenLib.GetTime()
        # POST-REVIVE GRACE: just came back to life -> don't acquire/approach/attack for REVIVE_GRACE so
        # HP can recover first (potions still run in _tick), avoiding the "revive -> instant re-death" loop.
        if now < getattr(self, '_reviveGraceUntil', 0.0):
            self._huntTarget = 0
            if now - getattr(self, '_lastGraceLog', 0.0) >= 1.0:
                self._lastGraceLog = now
                _info("[Auto-Hunt] Recovering from resurrection, resuming attack in %ds" % (
                    int(round(self._reviveGraceUntil - now)) or 1))
            return
        dbg = AH_DEBUG and (now - getattr(self, '_lastCbDbg', 0.0) > 2.0)
        if dbg:
            self._lastCbDbg = now
            _dbg("[CC] aa=%s foc=%s anchor=%s hold=%.1f bow=%s" % (
                self.autoAttack, int(self.autoRange), self._anchor is not None,
                max(0.0, self._castRestartAt - now), int(self._isBow())))
        if now < self._castRestartAt:
            return   # a skill cast (buff park) is finishing -> hold position + attacks
        p = self._pos(mainVID)
        if p is None:
            if dbg: _dbg("[CC] player pos FAILED (select+GetPixelPosition)")
            return
        px, py = p
        # FOCUS anchor management -- done in LIVE code so it's immune to a hot-reloaded stale toggle
        # closure. When Focus is ON we need a hunt-center: prefer the LAST CONFIRMED center so toggling
        # Focus back ON re-applies the SAME circle (not one re-centered wherever we roamed while Focus was
        # off -- that would keep us attacking the very mob we walked out to). On the OFF->ON transition we
        # also drop the committed target so it re-acquires inside the re-applied zone (a target grabbed
        # while Focus was off is likely outside it, and the leash won't fire if we're still inside it).
        # FOCUS OFF just leaves the center remembered and the leash/zone gated off (unrestricted).
        prevFoc = getattr(self, '_prevFoc', self.autoRange)
        if self.autoRange:
            if self._anchor is None:
                self._anchor = getattr(self, '_confirmedAnchor', None) or (px, py)
            self._confirmedAnchor = self._anchor
            if not prevFoc:                 # OFF -> ON this tick -> re-apply the leash cleanly
                self._huntTarget = 0
                self._approachTgt = 0
                self._leashing = False
                self._approachGoalPos = None
                try:
                    Movement.StopMovement()  # HALT the in-flight walk toward the out-of-zone mob; else the
                except:                      # char keeps its old move order even after we drop the target
                    pass
                _dbg("[FOC] ON: re-anchor=%s dropTgt R=%.0f" % (self._anchor, float(self.huntRange)))
        if AH_DEBUG and self.autoRange != getattr(self, '_focLogged', None):
            self._focLogged = self.autoRange
            _dbg("[FOC] foc=%d anchor=%s confAnchor=%s" % (
                int(self.autoRange), self._anchor, getattr(self, '_confirmedAnchor', None)))
        self._prevFoc = self.autoRange
        # 1) LEASH -- every tick: outside the anchored circle -> walk back, don't hunt. GATE ON autoRange
        # (Focus), NOT just the anchor: toggling Focus OFF must drop the leash LIVE even if _anchor is
        # still set (e.g. a hot-reloaded toggle closure that updated autoRange but not the anchor). Focus
        # is the single source of truth for "is the hunt range-limited".
        if self.autoRange and self._anchor is not None:
            ax, ay = self._anchor
            d2 = (px - ax) ** 2 + (py - ay) ** 2
            R = float(self.huntRange)
            if not self._leashing and d2 > R * R:
                self._leashing = True
                self._huntTarget = 0
                self._lastApproach = 0.0
                self._stopNative()   # don't let the native engine attack outside the zone while we walk back
                _dbg("[LEASH] ON dist=%.0f R=%.0f -> walking back" % (d2 ** 0.5, R))
            if self._leashing:
                if d2 <= (R * 0.5) ** 2:
                    self._leashing = False   # back well inside -> resume hunting next tick
                    _dbg("[LEASH] OFF (back inside) -> resume hunt")
                else:
                    if now - self._lastApproach >= APPROACH_TICK:
                        self._lastApproach = now
                        try:
                            Movement.GoToPositionAvoidingObjects(ax, ay)
                        except:
                            pass
                    return
        # 2) TARGET -- COMMIT to the current target while it's alive (fixes the thrashing); re-pick only
        # when it's gone, IMMEDIATELY (no throttle -> no post-kill idle). FOCUS it now, during approach
        # too, so the UI shows it + offensive skills can use it (fixes "focus only when right next to it").
        tgt = self._validTarget(self._huntTarget, now)
        if not tgt:
            _old = self._huntTarget
            tgt = self._acquireTarget(mainVID, now)   # nearest FILTERED in-zone
            self._huntTarget = tgt
            self._approachTgt = 0
            self._inMelee = False   # fresh target -> re-approach it from scratch
            if _old != tgt:
                _dbg("[TGT] %s -> %s (re-acquired)" % (_old, tgt))   # rapid flip = the 'goes to another mob' jitter
        if dbg:
            try: ninst = len(list(eXLib.InstancesList))
            except: ninst = -1
            _dbg("[CC] tgt=%s instances=%d leash=%s" % (tgt, ninst, self._leashing))
        if not tgt:
            return   # nothing to hunt in-zone
        try:
            player.SetTarget(tgt)   # focus early (approach + attack) -> UI + skills track the committed target
        except:
            pass
        if NATIVE_ATTACK_ONLY:
            # pure NEW_Attack: no uBot movement at all -> it does its OWN native move-to-attack + smooth
            # face + attack. Isolates whether our pathfinding/hand-off is what causes the retarget pivot.
            if now - getattr(self, '_lastSwing', 0.0) >= SWING_TICK:
                self._lastSwing = now
                self._swingAt(tgt)
            return
        # 3) RANGE -> approach if far, else attack
        try:
            dist = player.GetCharacterDistance(tgt)
        except:
            self._huntTarget = 0
            return
        # MELEE HYSTERESIS: ENTER melee when within ATTACK_RANGE, OR when stalled close (can't path the
        # last step -- mob body collision -> was "stuck in APPROACH 1-2 steps away"). STAY in melee
        # (attacking, no re-approach -> no oscillation/turning around the ring) until the mob flees past
        # COMBAT_MAX. NEW_Attack + the mob closing the gap lands the hits.
        enterR, stayR = self._attackRange()   # bow -> shoot from range; melee -> ATTACK_RANGE/COMBAT_MAX
        stalled = (now - self._stillSince) >= 0.4
        if not getattr(self, '_inMelee', False):
            if dist <= enterR or (dist <= stayR and stalled):
                self._inMelee = True
                try:
                    Movement.StopMovement()   # clear OUR path so NEW_Attack's native move-to-attack +
                except:                       # smooth facing owns the engagement (no fighting = no pivot)
                    pass
                self._approachGoalPos = None
        elif dist > stayR:
            self._inMelee = False
        if dbg:
            _dbg("[CC] dist=%.0f bow=%s enter=%d melee=%s stalled=%s -> %s" % (
                dist, int(self._isBow()), enterR, self._inMelee, stalled,
                "ATTACK" if self._inMelee else "APPROACH"))
        if not self._inMelee:
            self._approachTarget(tgt, px, py, now)   # walk toward the committed target
            return
        # IN MELEE -> attack via the client's animated attack on cadence.
        self._approachTgt = 0
        if now - getattr(self, '_lastSwing', 0.0) >= SWING_TICK:
            self._lastSwing = now
            self._swingAt(tgt)

    def _validTarget(self, vid, now):
        # COMMIT: keep the current target while it's ALIVE + not blacklisted. Do NOT re-run the
        # type/zone/position checks here every tick -- those belong to ACQUIRE only. Re-checking them on
        # a moving/far target kept dropping it -> re-acquire -> the "nearest" thrashed as the char moved
        # (zigzag, late focus, wrong facing, post-kill idle). Leash handles the char drifting out of zone.
        if not vid:
            return 0
        try:
            if eXLib.IsDead(vid):
                return 0
            if self._blacklist.get(vid, 0.0) > now:
                return 0
        except:
            return 0
        return vid

    def _acquireTarget(self, mainVID, now):
        # NEAREST live monster inside the anchored zone (+ hunt range), skipping blacklisted ones.
        best_vid = 0
        best_dist = self.huntRange if self.autoRange else 1e9
        passed = 0                      # candidates that cleared type+filter (reached the distance test)
        nearD, nearV = 1e18, 0          # nearest such candidate, to see if a range CAP is what's excluding
        ax = ay = None
        # zone-filter targets ONLY when Focus is on (gate on autoRange, not just the anchor -- see leash).
        if self.autoRange and self._anchor is not None:
            ax, ay = self._anchor
        zr2 = self._zoneRadius() ** 2
        # FULL attack filter from the panel: category (cat1-5 / Boss via the mob's RANK) + Metin (by type)
        # + level range. Rank + level come from the CLIENT'S OWN live mob table via nonplayer -- the same
        # data the target bar shows, always current, no mob_proto.txt to maintain.
        flags = getattr(self.attackPanel, 'flags', None) or [True] * 7
        wantMonster = any(flags[0:6])
        wantMetin = flags[6]
        try:
            plvl = int(player.GetStatus(player.LEVEL))
        except:
            plvl = 0
        try:
            lo = max(1, plvl - self._toInt(self.attackPanel.editMinus.GetText(), 15))
            hi = plvl + self._toInt(self.attackPanel.editPlus.GetText(), 15)
        except:
            lo, hi = 1, 999
        try:
            vids = list(eXLib.InstancesList)
        except:
            return 0
        for vid in vids:
            if vid == mainVID or self._blacklist.get(vid, 0.0) > now:
                continue
            try:
                if eXLib.IsDead(vid):
                    continue
                chr.SelectInstance(vid)
                t = chr.GetInstanceType(vid)
                if t == OpenLib.METIN_TYPE:
                    if not wantMetin:
                        continue
                    # METIN LEVEL (verified via client RE): GetLevelByVID returns -1 for stones -- their
                    # instance +0x54 level field is 0 and the by-VID path doesn't resolve stone instances.
                    # So resolve the metin's VNUM, then read the mob-TABLE level directly with
                    # nonplayer.GetLevel(vnum) (= CPythonNonPlayer::GetTable(vnum)->level, and the table
                    # HAS metins 8001-8012 e.g. 8003->15). VNUM: GetVnumByVID first, else eXLib's
                    # packet-tracked race (independent of the client's by-VID instance map).
                    try:
                        vn = 0
                        try:
                            vn = nonplayer.GetVnumByVID(vid)
                        except:
                            vn = 0
                        if not vn or vn <= 0:
                            try:
                                vn = eXLib.GetInstanceRace(vid)
                            except:
                                vn = 0
                        ml = 0
                        if vn and vn > 0:
                            try:
                                ml = nonplayer.GetLevel(vn)
                            except:
                                ml = 0
                        if now - getattr(self, '_lastMetinDbg', 0.0) > 3.0:
                            self._lastMetinDbg = now
                            _dbg("[FILT-METIN] vid=%s vnum=%s tableLvl=%s window=%s-%s plvl=%s" % (vid, vn, ml, lo, hi, plvl))
                        if plvl > 0 and ml > 0 and not (lo <= ml <= hi):
                            continue
                    except:
                        pass
                elif t == OpenLib.MONSTER_TYPE:
                    if not wantMonster:
                        continue
                    # rank(category) + level from the CLIENT's mob table (nonplayer); -1 = unknown ->
                    # don't over-filter. Metins are rank KING but filtered by TYPE above, not here.
                    try:
                        g = nonplayer.GetGradeByVID(vid)
                        fIdx = GRADE_TO_FLAG.get(g)
                        if fIdx is not None and not flags[fIdx]:
                            continue                       # this category checkbox is off
                        ml = nonplayer.GetLevelByVID(vid)
                        if plvl > 0 and ml > 0 and not (lo <= ml <= hi):
                            continue                       # outside the level range
                        if now - getattr(self, '_lastGradeDbg', 0.0) > 3.0:
                            self._lastGradeDbg = now
                            _dbg("[FILT] vid=%s grade=%s lvl=%s -> catFlag=%s" % (vid, g, ml, fIdx))
                    except:
                        pass
                else:
                    continue   # not an attackable mob/metin
                d = player.GetCharacterDistance(vid)
                passed += 1
                if 0 <= d < nearD:
                    nearD, nearV = d, vid
                if ax is not None:
                    tx, ty, tz = eXLib.GetPixelPosition(vid)   # (vid) form works; no-arg raises
                    if (tx - ax) ** 2 + (ty - ay) ** 2 > zr2:
                        continue   # outside the anchored zone -> ignore (anti-drift)
            except:
                continue
            if d < best_dist:
                best_dist = d
                best_vid = vid
        if best_vid == 0 and AH_DEBUG and (now - getattr(self, '_lastAcqDbg', 0.0) > 2.0):
            self._lastAcqDbg = now
            _dbg("[ACQ] none inst=%d passedFilter=%d nearest=(d%.0f v%s) cap=%.0f foc=%d anch=%d" % (
                len(vids), passed, nearD if nearD < 1e17 else -1, nearV, best_dist,
                int(self.autoRange), int(self._anchor is not None)))
        return best_vid

    def _approachTarget(self, tgt, px, py, now):
        # collision-aware walk toward a REACHABLE point near the target + unstuck/blacklist (same
        # strategy as the old _navAssist, but toward OUR chosen target instead of the engine's focus).
        if now - self._lastApproach < APPROACH_TICK:
            return
        self._lastApproach = now
        tp = self._pos(tgt)
        if tp is None:
            return
        tx, ty = tp
        if tgt != self._approachTgt:
            self._approachTgt = tgt
            self._approachMinDist = 1e9
            self._noProgressSince = now
            self._approachFails = 0
            self._approachGoalPos = None      # new target -> force a fresh walk order
        try:
            dist = player.GetCharacterDistance(tgt)
        except:
            return
        if dist < self._approachMinDist - 50:
            self._approachMinDist = dist
            self._noProgressSince = now
        if now - self._noProgressSince > 3.0:   # not getting closer -> an (entity-collision) obstacle
            self._noProgressSince = now
            self._approachFails += 1
            if self._approachFails >= 3:
                self._blacklist[tgt] = now + 15.0   # give up on this one; acquire another next tick
                self._huntTarget = 0
                self._approachTgt = 0
                return
            self._nudge(px, py, tx, ty)
            self._approachGoalPos = None       # nudged -> re-issue the walk next time
            return
        # JITTER FIX: aim straight at the TARGET cell with maxDist as the in-range stop, and only (re)issue
        # the walk when the target has actually MOVED (or we have no order yet). The old code recomputed a
        # goal point OFF the live player position every tick, so eXLib.FindPath re-pathed to a slightly
        # different point each APPROACH_TICK and emitted a different FIRST waypoint -> the "1-2 steps
        # sideways" while chasing. A stable destination = one stable path; FindPath still routes around
        # trees, and maxDist stops us inside attack range.
        g = getattr(self, '_approachGoalPos', None)
        moved = 1e9 if g is None else OpenLib.dist(tx, ty, g[0], g[1])
        if g is None or moved > 70:
            self._approachGoalPos = (tx, ty)
            enterR = self._attackRange()[0]
            _dbg("[APP] walk dist=%.0f bow=%d stop=%d" % (dist, int(self._isBow()), int(enterR * 0.8)))
            try:
                Movement.GoToPositionAvoidingObjects(tx, ty, maxDist=int(enterR * 0.8))
            except:
                pass

    def _swingAt(self, tgt):
        # Animated attack via the CLIENT'S OWN attack: eXLib.NewAttack() -> CPythonPlayer::NEW_Attack(),
        # the exact "hold Space" code path. We set + face the target; the client then plays the real
        # swing animation (bow or melee, correct for the equipped weapon) AND deals the damage. No packet
        # or motion faking -- fully legit to us and to nearby players.
        # CE-PROVEN: NEW_Attack deals damage to the +0x34B44 target but does NOT turn the char -- the smooth
        # native facing is the client's per-frame attack-STATE rotation (holding the attack key / click-to-
        # attack), which a field write does not trigger (set +0x34B44 to a valid VID -> still attacked
        # forward). So we face the mob ourselves right before the swing so the frontal-arc hit lands. Snap,
        # but reliable. (Truly native turning would need replicating that per-frame attack-state machine.)
        tp = self._pos(tgt)
        if tp is not None:
            try:
                OpenLib.RotateMainCharacter(tp[0], tp[1])
            except:
                pass
        try:
            eXLib.NewAttack()
        except:
            pass

    def _weaponMode(self):
        # motion mode from the ACTUAL equipped weapon subtype -> the correct attack swing for ANY weapon
        # (sword 1H/2H, dagger, bow, fan, bell, claw). Reads the equipped weapon like OpenLib.IsWeaponArch.
        # Cached ~2s (weapon rarely changes; avoids per-swing item churn). Falls back to GENERAL(1).
        now = OpenLib.GetTime()
        if getattr(self, '_wmCache', None) is not None and now - getattr(self, '_wmChk', 0.0) < 2.0:
            return self._wmCache
        self._wmChk = now
        mode = 1   # GENERAL (unarmed / unknown)
        try:
            idx = player.GetItemIndex(2, item.EQUIPMENT_WEAPON)
            if idx:
                item.SelectItem(idx)
                if item.GetItemType() == item.ITEM_TYPE_WEAPON:
                    st = item.GetItemSubType()
                    # weapon subtype -> MOTION_MODE_* (getattr so one missing const can't break the rest)
                    for sub_name, mode_val in (('WEAPON_SWORD', 2), ('WEAPON_TWO_HANDED', 3),
                                               ('WEAPON_DAGGER', 4), ('WEAPON_BOW', 5), ('WEAPON_FAN', 6),
                                               ('WEAPON_BELL', 7), ('WEAPON_CLAW', 17)):
                        if st == getattr(item, sub_name, -999):
                            mode = mode_val
                            break
        except:
            mode = 1
        self._wmCache = mode
        return mode

    def _doSkills(self, mainVID):
        # Buffs are STANDING skills -> ClickSkillSlot is IGNORED by the client while the character is
        # moving. During auto-hunt the char is usually chasing, so casts landed only by luck (the
        # "random" misfires). Fix: when a buff is due, STOP the engine, wait until the char is actually
        # STILL, then cast. One buff at a time (animations don't stack). Offensive skills cast while
        # attacking a target in range (char is stationary-attacking then, so no stop needed).
        now = OpenLib.GetTime()
        if now - self._lastSkill < SKILL_TICK:
            return
        self._lastSkill = now
        if player.IsMountingHorse():
            return

        # --- BUFFS: standing self-buffs (ClickSkillSlot is ignored while the char is moving). When a buff
        # is due AND actually castable (off its cooldown/GCD), briefly PARK combat so the char settles,
        # then cast it -- one per ~1s so the animations don't clobber each other. CRITICAL: we only park
        # for a buff that is READY to cast right now. A buff that's "due" but still on its own cooldown
        # does NOT hold here -> it can never starve the offensive skills below. That starvation (the old
        # code returned while ANY buff was due, even one stuck on cooldown) was why rolling dagger / Dragon
        # Swirl never fired and why the 2nd buff seemed to "wait minutes".
        dueReady = None
        for s in self.skillSet:
            if not s.get('learned') or not s.get('isBuff'):
                continue
            tg = s.get('toggle')
            if tg is None or not tg.isOn:
                continue
            if s['id'] in OpenLib.SKILL_TOGGLE:
                # on/off aura -> enable ONCE, never on a timer (recasting toggles it OFF). Resets on Start/death.
                if s['id'] in self._toggleDone:
                    continue
            else:
                # REAL duration from the client, read with the SLOT-based efficient % (CE + live [BUFF]
                # log confirmed: GetDuration(id, GetSkillCurrentEfficientPercentage(SLOT)) = the true
                # tooltip value, e.g. Aura 37; the stale recast box read too low -> recast fired while the
                # buff was still active, which the client ignores, so it never refreshed). Recast at
                # duration + 2 so it fires just AFTER expiry and actually lands.
                try:
                    dur = int(round(float(skill.GetDuration(s['id'], player.GetSkillCurrentEfficientPercentage(s['slot'])))))
                except:
                    dur = 0
                if dur <= 0:
                    dur = self._toInt(s['edit'].GetText(), 0) or int(round(s.get('dur', 0) or 0)) or 20
                if now - s['lastCast'] < dur + 2:
                    continue          # still active
            try:
                if player.IsSkillCoolTime(s['slot']):
                    continue          # on cooldown/GCD -> can't recast yet; let offensive run
            except:
                continue
            # SP GATE: never PARK the attack loop to cast a buff we can't afford -- with no SP the cast does
            # nothing, so the char stop-starts (stop, fail, resume, repeat -- the reported jank). If SP is
            # short, skip the buff and keep attacking; retry once SP regens. Offensive skills stay ungated
            # (attacking continues regardless of SP).
            try:
                curSp = int(player.GetStatus(player.SP))
                maxSp = int(player.GetStatus(player.MAX_SP))
                try:
                    needSp = int(skill.GetSkillNeedSP(s['id'], player.GetSkillCurrentEfficientPercentage(s['slot'])))
                except:
                    needSp = 0
                if not (0 < needSp <= maxSp):
                    needSp = int(maxSp * 0.15)   # GetSkillNeedSP unreliable -> low-SP floor guard
                if curSp < needSp:
                    continue                     # not enough SP -> skip, keep attacking, retry on regen
            except:
                pass
            dueReady = s
            break

        # DIAG: dump every toggled-on buff's state so we can see why a 2nd buff won't recast. tog=in
        # SKILL_TOGGLE (cast-once aura), done=already enabled, dur=recast box (0 = auto-recast OFF ->
        # SKIPPED), since=sec since last cast, cd=on cooldown/gcd.
        if AH_DEBUG and (now - getattr(self, '_lastBuffDbg', 0.0) > 2.0):
            self._lastBuffDbg = now
            rows = []
            for s in self.skillSet:
                if not s.get('isBuff'):
                    continue
                tg = s.get('toggle')
                dur = self._toInt(s['edit'].GetText(), 0) if s.get('edit') else -1
                cd = '?'
                try: cd = int(bool(player.IsSkillCoolTime(s['slot'])))
                except: pass
                # GetDuration is INDEX-keyed; we pass the vnum. Log both vnum-arg and slot-arg results so
                # we can see which one matches the real tooltip duration -> pin the correct index.
                gV = gS = '?'
                try:
                    k = player.GetSkillCurrentEfficientPercentage(s['slot'])
                    gV = int(skill.GetDuration(s['id'], k))
                    gS = int(skill.GetDuration(s['slot'], k))
                except: pass
                rows.append("id%s(L%s T%s tog%s done%s dur%s since%d cd%s gV%s gS%s slot%s)" % (
                    s['id'], int(bool(s.get('learned'))), int(bool(tg is not None and tg.isOn)),
                    int(s['id'] in OpenLib.SKILL_TOGGLE), int(s['id'] in self._toggleDone),
                    dur, int(now - s.get('lastCast', 0.0)), cd, gV, gS, s['slot']))
            _dbg("[BUFF] dueReady=%s | %s" % (dueReady['id'] if dueReady else None, " ".join(rows)))

        # BUFF CAST -- deliberately SIMPLE + OPTIMISTIC. Every "smart" version (wait-for-stationary,
        # IsSkillCoolTime "landed" check, retry loop, wall-clock deadline) regressed: IsSkillCoolTime does
        # NOT reliably read as on-cooldown right after a buff cast, so `landed` stayed False, so the bot
        # re-clicked and PARKED for seconds while the buff appeared "not called". So: when a buff is due
        # AND we're not mid-approach, pause the swing for ONE brief beat, ClickSkillSlot it ONCE, advance
        # its timer immediately, and move on. It refreshes on its own dur+2 schedule. Combat can NEVER
        # hang (lastCast always advances) and multiple buffs are spaced so their animations don't collide.
        approaching = bool(getattr(self, '_huntTarget', 0)) and not getattr(self, '_inMelee', False)
        if dueReady is not None and not approaching:
            bid = dueReady['id']
            # GCD-SAFE spacing: do NOT cast a buff within BUFF_GCD of ANY skill cast (buff OR offensive). A
            # ClickSkillSlot fired inside the previous skill's global-cooldown / animation is silently
            # dropped, and our optimistic timer then skips that buff a whole duration -- that's BOTH the
            # "2 of 3 buffs land, the 3rd is skipped (rotating)" case AND the warrior-mental "offensive
            # animation swallows the buff". Offensive stays UNGATED (it casts on its own cooldown). Inside
            # the window we fall through and keep attacking; the buff lands in the next gap between skills.
            if (now - getattr(self, '_lastSkillCast', -1.0e9)) >= BUFF_GCD:
                self._castRestartAt = now + 0.6      # one brief beat so the cast animates cleanly
                if getattr(self, '_nativeOn', False):
                    self._stopNative()
                try:
                    Movement.StopMovement()
                except:
                    pass
                self._approachGoalPos = None
                try:
                    player.ClickSkillSlot(dueReady['slot'])
                except:
                    pass
                if bid in OpenLib.SKILL_TOGGLE:
                    self._toggleDone.add(bid)        # on/off aura -> fire once, never recast (would toggle OFF)
                dueReady['lastCast'] = now           # optimistic: recast at dur+2 keeps it refreshed
                self._lastBuffCastAt = now
                self._lastSkillCast = now
                _dbg("[BUFFCAST] id=%s slot=%s fired" % (bid, dueReady['slot']))
                return
            # inside the GCD window -> fall through and keep attacking; the buff casts in the next gap

        # --- OFFENSIVE --- (reached whenever no buff is ready to cast right now)
        # Only cast once we're actually ENGAGED (in attack range: the melee ring, or bow range -- _inMelee
        # is set by the same bow-aware hysteresis). Casting a melee skill mid-RUN made the client's own
        # skill move-to-attack fight our navigation and the char froze (the lycan "used one skill then
        # halted"). While still approaching we just keep walking; skills fire the instant we arrive.
        if not getattr(self, '_inMelee', False):
            return
        # ALL offensive skills go through player.ClickSkillSlot -- the legit "pressed the skill key" path
        # that animates AND deals damage. It works for need-target skills (rolling dagger) and self/AoE
        # skills (Dragon Swirl) alike, provided a target is FOCUSED, so we focus one first. This replaces
        # the old eXLib.SendUseSkillPacketBySlot packet path (the use-skill SEND is unreliable on this
        # client -> the reason Dragon Swirl never fired).
        rng = self._attackRange()[1]                   # bow -> fire offensive skills from bow range too
        castTarget = 0
        try:
            tvid = getattr(self, '_huntTarget', 0) or player.GetTargetVID()
            if tvid and not eXLib.IsDead(tvid) and player.GetCharacterDistance(tvid) <= rng:
                castTarget = tvid                      # prefer the mob we're already fighting
        except:
            castTarget = 0
        if not castTarget:
            try:
                nv = self._findNearestMob(mainVID)     # else the nearest in-range mob
                if nv and player.GetCharacterDistance(nv) <= rng:
                    castTarget = nv
            except:
                castTarget = 0
        if not castTarget:
            return                                     # no mob in range -> don't waste skills
        try:
            player.SetTarget(castTarget)               # focus so need-target skills have a target (AoE ignores it)
        except:
            pass
        # DIAG: dump every offensive skill's state (Learned / Toggle-on / on-CoolDown) + whether the char is
        # STILL -> shows exactly why only 1 of N fires (standing skills are ignored while moving; a skill
        # stuck cd=1 never clears; L0/T0 = not learned / toggle off).
        if AH_DEBUG and (now - getattr(self, '_lastSkDbg', 0.0) > 2.0):
            self._lastSkDbg = now
            still = int((now - self._stillSince) >= 0.35)
            rows = []
            for s in self.skillSet:
                if s.get('isBuff'):
                    continue
                tg = s.get('toggle')
                cdv = '?'
                try: cdv = int(bool(player.IsSkillCoolTime(s['slot'])))
                except: pass
                rows.append("id%s(L%s T%s cd%s)" % (s['id'], int(bool(s.get('learned'))),
                            int(bool(tg is not None and tg.isOn)), cdv))
            _dbg("[SK] tgt=%s still=%s melee=%s | %s" % (
                castTarget, still, int(getattr(self, '_inMelee', False)), " ".join(rows)))
        for s in self.skillSet:
            if not s.get('learned') or s.get('isBuff'):
                continue
            tg = s.get('toggle')
            if tg is None or not tg.isOn:
                continue
            slot = s['slot']
            try:
                if player.IsSkillCoolTime(slot):
                    continue
            except:
                continue
            try:
                player.ClickSkillSlot(slot)            # legit animated cast on the focused target
            except:
                continue
            s['lastCast'] = now
            self._lastOffCast = now                   # (kept) buffs wait out this skill's animation
            self._lastSkillCast = now                 # shared GCD stamp so the next buff won't collide
            _dbg("[SK] CAST id=%s slot=%s" % (s['id'], slot))
            break

    def _castKick(self, now):
        # A manual skill cast cancels the native engine's current move/attack and it bricks (won't
        # re-path). So stop the engine right before the cast (nothing to cancel), and let _startNative
        # restart it -> re-focus + re-path fresh -- once the cast animation has finished.
        try:
            ah = self._getAutoHunting()
            if ah is not None:
                ah.SendRequestAutoHuntingOnoff(0)
        except:
            pass
        self._nativeOn = False
        self._castRestartAt = now + 1.6

    def _refreshSkillDurations(self):
        # Skill duration grows as you add points / master it -> refresh the recast defaults live
        # (~2.5s) so they track without reopening the window. Only auto-updates a box the user hasn't
        # hand-edited (its text still equals the last auto value we wrote).
        now = OpenLib.GetTime()
        if now - getattr(self, '_lastDurRefresh', 0.0) < 2.5:
            return
        self._lastDurRefresh = now
        for s in self.skillSet:
            if not s.get('learned'):
                continue
            lvl, grade, lvlArg = self._skillState(s['id'], s['slot'])
            s['level'] = lvl
            s['grade'] = grade
            if lvl <= 0:
                continue
            s['isBuff'] = self._isBuffSkill(s['id'])
            if not s['isBuff']:
                continue
            dur = self._skillDuration(s['id'], lvlArg, lvl, s['slot'])
            if dur <= 0:
                continue
            newText = str(int(round(dur)))   # readout = real duration (recast adds its own +2)
            try:
                cur = s['edit'].GetText()
            except:
                continue
            if cur != newText:
                try:
                    s['edit'].SetText(newText)
                    s['autoText'] = newText
                except:
                    pass

    def _refreshHelperLabels(self):
        if not self.helperState:
            return
        now = OpenLib.GetTime()
        for h in self.helperState:
            entry = h['entry']
            t = entry.get('time', 0)
            try:
                if entry.get('type') == 'cooldown':
                    rem = int(max(0, t - (now - h['lastUse'])))
                    h['label'].SetText("%dm%02ds" % (rem // 60, rem % 60) if rem >= 60 else "%ds" % rem)
                else:
                    h['label'].SetText("/%ds" % t)
            except:
                pass

    # --------------------------------------------------------- window ----
    def switch_state(self):
        if self.Board.IsShow():
            for p in (self.attackPanel, self.focusPanel):   # side windows close with the main one
                try:
                    p.Board.Hide()
                except:
                    pass
            self.Board.Hide()
        else:
            self.resetSkillsUI(force=True)
            self.resetPotionsUI(force=True)
            self.Board.Show()

    def _rebuildWindow(self):
        # /rah-ui in-game command: rebuild the ENTIRE window in place so BuildWindow() LAYOUT edits (new
        # slots/positions/sizes) take effect WITHOUT a client or window restart. /rah alone only rebinds the
        # class -> logic updates but the already-built widgets keep their old geometry. Here we hide + drop
        # every python ref to the old widget tree (so refcount hits 0 and the C++ windows are destroyed, not
        # orphaned on screen), then re-run the exact __init__ UI sequence. Live BOT state is untouched.
        wasShown = False
        try: wasShown = self.Board.IsShow()
        except: pass
        # 1) tear down side panels
        for _attr in ('rangePreview', 'focusPanel', 'attackPanel'):
            p = getattr(self, _attr, None)
            if p is not None:
                try: p.Board.Hide()
                except: pass
                try: p.Hide()
                except: pass
            try: setattr(self, _attr, None)
            except: pass
        # 2) hide the main board (hides all children) + release every old-widget ref so GC destroys them
        try: self._hideAllSkillWidgets()
        except: pass
        try: self.Board.Hide()
        except: pass
        for _attr in ('Board', 'comp', 'saveBtn', 'startBtn', 'endBtn', 'btnAttackOpt', 'btnFocusOpt',
                      '_skillWidgets', 'toggleHolders', '_keep', 'skillSet', 'helperState', 'potionIcons'):
            try: setattr(self, _attr, None)
            except: pass
        # HP/SP + the empty potion inputs are "create once" (guarded by `hasattr(self,'editHP')` in
        # resetPotionsUI so they don't churn on every teleport). They lived on the OLD board we just
        # destroyed -> DELETE the attrs (not None: hasattr() must go False) so they rebuild on the new one.
        # Without this, /rah-ui left editHP/editSP dangling on the dead board -> the inputs vanished.
        for _attr in ('editHP', 'editSP', 'slotHP', 'slotSP', 'emptyPotInputs', '_potionsBuilt'):
            try:
                if hasattr(self, _attr):
                    delattr(self, _attr)
            except: pass
        # 3) re-init the widget-holding lists, then rebuild exactly as __init__ does
        self.skillSet = []
        self.helperState = []
        self.potionIcons = []
        self._keep = []
        self._skillWidgets = []
        self.toggleHolders = []
        self.BuildWindow()
        self.resetSkillsUI(force=True)
        self.resetPotionsUI(force=True)
        self.rangePreview = RangePreviewWindow(self)
        self.focusPanel = FocusPanel(self)
        self.attackPanel = AttackPanel(self)
        if wasShown:
            try: self.Board.Show()
            except: pass
        try: _info("[Auto-Hunt] window rebuilt in place (build %s)" % AH_BUILD)
        except: pass


def switch_state():
    instance.switch_state()


# reload-safe (for the /rah in-game hot-reload): first load -> build the window; on RELOAD the instance
# still exists in this module dict, so just REBIND its class -> the live instance picks up all new methods
# while KEEPING its window + state (no duplicate window). New __init__ attrs won't exist, but the code
# reads them via getattr(...) defaults + StartBot resets, so that's fine. Window-LAYOUT edits (BuildWindow)
# still need a close+reopen or restart. registerPhaseCallback is dict-keyed -> re-running just replaces it.
try:
    instance
    instance.__class__ = AutoHunting
except NameError:
    instance = AutoHunting()
try:
    _dbg("[AH] build %s active" % AH_BUILD)   # proves which code /rah actually loaded
except:
    pass
Hooks.registerPhaseCallback('autoHuntingCallback', __PhaseCallback)
