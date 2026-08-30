import sys
import __builtin__ as buildin

def HasArguments(module, attrlist):
    for attr in attrlist:
        if not buildin.hasattr(module, attr):
            return False
    return True

for modulename, module in iter(sys.modules.items()):
    if HasArguments(module, ['GetPlayTime']): player = module
    if HasArguments(module, ['GetNameByVID']): chr = module
    if HasArguments(module, ['ArrangeShowingChat']): chat = module
    if HasArguments(module, ['SetCameraMaxDistance']): app = module
    if HasArguments(module, ['GetCurrentMapName']): background = module
    if HasArguments(module, ['ScriptWindow']): ui = module

import eXLib, UIComponents, OpenLib, Movement

# Arrow effect (compass mesh) files, by dropdown label.
EFFECT_BY_LABEL = {
    'Small':  "d:/ymir work/effect/etc/compass/appear_small.mse",
    'Medium': "d:/ymir work/effect/etc/compass/appear_middle.mse",
    'Large':  "d:/ymir work/effect/etc/compass/appear_large.mse",
}
EFFECT_LABELS = ['Small', 'Medium', 'Large']
DEFAULT_EFFECT = EFFECT_BY_LABEL['Medium']

# Target kinds. Metin/Ore by instance TYPE (uBot convention); Boss by monster + BOSS_IDS vnum.
TYPE_LABELS = ['Metin', 'Ore', 'Boss']

TICK_SECONDS = 3.0     # re-point the compass / refresh status this often
PROXIMITY = 1000       # a live instance within this of a recorded spot == the same (static) object
STATUS_DEBUG = False   # True -> append instance count / type histogram to the status line (dev diag)

# A recorded target is flagged DEAD only when the player is within APPEAR_DIST of its coords and it
# is NOT in the instance list (close enough it'd be visible if alive). Beyond that range the object
# is just out of sight, so we never flag it -> no false 'dead'. Per type, measured from the distance
# at which objects pop in/out of the instance list (pixel units = ingame*100):
#   metin: visible ~6700, gone ~7900   ore: visible ~9100+   -> use values safely BELOW the visible range
APPEAR_DIST_BY_KIND = {'Metin': 6000, 'Ore': 8000, 'Boss': 6000}
DEFAULT_APPEAR_DIST = 6000

# Two sightings are the SAME recorded object when same name+kind AND within this distance. Static
# objects (metin/ore) don't move, so a small tolerance dedups them; bosses roam, so they're matched
# within their appearance range (there can't be two of the same boss that close) -> only the FIRST
# appearance is kept instead of logging a new row every time the boss drifts.
SAME_OBJECT_DIST = {'Metin': PROXIMITY, 'Ore': PROXIMITY, 'Boss': APPEAR_DIST_BY_KIND['Boss']}
DEFAULT_SAME_OBJECT_DIST = PROXIMITY

# Pickaxable ore deposits are Type=1 NPCs -> client OBJECT type, the SAME type as guild mining
# NPCs, so the only clean separator is the mob vnum. 20047-20058 + 30301-30306 = the standard Metin2 ore sets (regular + beta maps)
# Add your server's custom ore vnums here if it has any.
ORE_VNUMS = set(range(20047, 20059)) | set(range(30301, 30307))

# Row colors. Metin2 SetFontColor uses the comp.RGB scale where a full channel = 255*255.
COL_ALIVE = (0, 255 * 255, 0)                       # bright green
COL_DEAD = (255 * 255, 0, 0)                        # bright red
COL_UNKNOWN = (150 * 255, 150 * 255, 150 * 255)     # gray

_BTN = ('d:/ymir work/ui/public/large_button_01.sub', 'd:/ymir work/ui/public/large_button_02.sub', 'd:/ymir work/ui/public/large_button_03.sub')

# Every target the compass pointed at this session. Kept until the game closes.
# Each entry: {name, x, y, kind, status('alive'|'dead'|'unknown')}.
try:                       # reload-safe (/rah): keep recorded targets + version across a logic reload
    RECORDED
    RECORD_VERSION
except NameError:
    RECORDED = []
    RECORD_VERSION = [0]   # bumped whenever RECORDED or any status changes (drives the live refresh)

def _recordTarget(vid, x, y, kind):
    try:
        name = chr.GetNameByVID(vid)
    except:
        name = ''
    if not name:
        name = '?'
    same2 = SAME_OBJECT_DIST.get(kind, DEFAULT_SAME_OBJECT_DIST) ** 2
    for r in RECORDED:
        if r.get('kind') == kind and r['name'] == name and (r['x'] - x) ** 2 + (r['y'] - y) ** 2 < same2:
            return  # same object already recorded (keep the first appearance; bosses roam within range)
    RECORDED.append({'name': name, 'x': x, 'y': y, 'kind': kind, 'status': 'alive'})
    RECORD_VERSION[0] += 1


class TargetListDialog(ui.ScriptWindow):

    class ListItem(ui.ListBoxEx.Item):
        def __init__(self, rec):
            ui.ListBoxEx.Item.__init__(self)
            self.rec = rec
            st = rec.get('status', 'alive')
            if st == 'dead':
                tag, col = '[DEAD] ', COL_DEAD
            elif st == 'alive':
                tag, col = '[ALIVE] ', COL_ALIVE
            else:
                tag, col = '[?] ', COL_UNKNOWN
            self.textLine = self.__MakeText(tag + "%s  (%.0f, %.0f)" % (rec['name'], rec['x'], rec['y']), col)
        def __del__(self):
            ui.ListBoxEx.Item.__del__(self)
        def GetText(self):
            return self.rec
        def SetSize(self, width, height):
            ui.ListBoxEx.Item.SetSize(self, 6 * len(self.textLine.GetText()) + 4, height)
        def __MakeText(self, s, col):
            t = ui.TextLine()
            t.SetParent(self)
            t.SetPosition(0, 0)
            try:
                t.SetFontColor(col[0], col[1], col[2])
            except:
                pass
            t.SetText(s)
            t.Show()
            return t

    def __init__(self):
        ui.ScriptWindow.__init__(self)
        self.comp = UIComponents.Component()
        self._shownVer = -1
        self.Board = ui.BoardWithTitleBar()
        self.Board.SetTitleName('Compass - Record List')
        self.Board.SetCloseEvent(self.Close)
        self.Board.SetSize(300, 350)
        self.Board.SetCenterPosition()
        self.Board.AddFlag('movable')

        self.bar, self.listBox, self.scroll = self.comp.ListBoxEx(self.Board, 12, 35, 250, 250)
        self.listBox.SetViewItemCount(14)

        self.clearBtn = self.comp.Button(self.Board, 'Clear Selected', 'Remove the selected entry', 15, 300, self.OnClear, *_BTN)
        self.goBtn = self.comp.Button(self.Board, 'Go to Object', 'Pathfind to the selected entry', 160, 300, self.OnGo, *_BTN)

        self.Board.Hide()

    def Refresh(self):
        self.listBox.RemoveAllItems()
        for rec in RECORDED:
            self.listBox.AppendItem(self.ListItem(rec))
        self._shownVer = RECORD_VERSION[0]

    def OpenList(self):
        self.Refresh()
        self.Board.Show()

    def OnClear(self):
        sel = self.listBox.GetSelectedItem()
        if not sel:
            return
        try:
            RECORDED.remove(sel.GetText())
            RECORD_VERSION[0] += 1
        except:
            pass
        self.Refresh()

    def OnGo(self):
        sel = self.listBox.GetSelectedItem()
        if not sel:
            return
        rec = sel.GetText()
        x, y = rec['x'], rec['y']
        # pathfind around walls (same as Move-to-Shop); straight-line fallback if no collision map
        if Movement.GoToPositionAvoidingObjects(x, y) == Movement.NO_PATH_FOUND:
            chr.MoveToDestPosition(player.GetMainCharacterIndex(), x, y)

    def Close(self):
        self.Board.Hide()


try:                       # reload-safe (/rah): rebind the LIVE list window to the new class (no dup window)
    listWindow
    listWindow.__class__ = TargetListDialog
except NameError:
    listWindow = TargetListDialog()


class CompassDialog(ui.ScriptWindow):

    def __init__(self):
        ui.ScriptWindow.__init__(self)
        self.comp = UIComponents.Component()
        self.running = False
        self.lastTick = 0
        self.ticks = 0

        self.Board = ui.BoardWithTitleBar()
        self.Board.SetTitleName('Compass')
        self.Board.SetCloseEvent(self.Close)
        self.Board.SetSize(235, 210)
        self.Board.SetCenterPosition()
        self.Board.AddFlag('movable')

        # Widgets created BOTTOM-TO-TOP so each ComboBox dropdown (opens downward) renders ON TOP
        # of the widgets beneath it (Metin2 draws later-created children last).
        self.lInfo = self.comp.TextLine(self.Board, 'Stopped', 20, 184, self.comp.RGB(255, 255, 0))

        # lInfo must exist before the OnOffButton (it fires funcState once during construction).
        self.playBtn = self.comp.OnOffButton(self.Board, '', 'Start / Stop the compass', 22, 120, funcState=self.OnToggle,
            OffUpVisual=eXLib.PATH + 'OpenBot/Images/start_0.tga', OffOverVisual=eXLib.PATH + 'OpenBot/Images/start_1.tga', OffDownVisual=eXLib.PATH + 'OpenBot/Images/start_2.tga',
            OnUpVisual=eXLib.PATH + 'OpenBot/Images/stop_0.tga', OnOverVisual=eXLib.PATH + 'OpenBot/Images/stop_1.tga', OnDownVisual=eXLib.PATH + 'OpenBot/Images/stop_2.tga')
        self.playBtn.SetOff()
        self.listBtn = self.comp.Button(self.Board, 'Record List', 'Targets recorded this session', 120, 120, self.OnList, *_BTN)

        self.lblEff = self.comp.TextLine(self.Board, 'Arrow:', 20, 80, self.comp.RGB(255, 255, 255))
        self.effCombo = self.comp.ComboBoxFunc(self.Board, EFFECT_LABELS[1], 60, 78, 110, self._onSelect)
        for i, lbl in enumerate(EFFECT_LABELS):
            self.effCombo.InsertItem(i, lbl)

        self.lblType = self.comp.TextLine(self.Board, 'Target:', 20, 48, self.comp.RGB(255, 255, 255))
        self.typeCombo = self.comp.ComboBoxFunc(self.Board, TYPE_LABELS[0], 66, 46, 110, self._onSelect)
        for i, lbl in enumerate(TYPE_LABELS):
            self.typeCombo.InsertItem(i, lbl)

        self.Board.Hide()
        self.Show()   # keep the ScriptWindow shown so OnUpdate ticks

    def _onSelect(self):
        pass

    def OnList(self):
        if listWindow.Board.IsShow():
            listWindow.Board.Hide()
        else:
            listWindow.OpenList()

    def OnToggle(self, state):
        self.running = bool(state)
        try:
            self.Show()   # re-arm OnUpdate in case a world reload (teleport/channel) dropped it from the update loop
        except:
            pass
        if hasattr(self, 'lInfo'):
            self.lInfo.SetText('Running: ' + self._typeLabel() if self.running else 'Stopped')

    def _typeLabel(self):
        try:
            return self.typeCombo.GetCurrentText()
        except:
            return TYPE_LABELS[0]

    def _matchesT(self, kind, vid, t):
        try:
            if kind == 'Metin':
                return t == OpenLib.METIN_TYPE
            if kind == 'Ore':
                if t != OpenLib.OBJECT_TYPE:   # cheap pre-filter (no select) before the vnum check
                    return False
                chr.SelectInstance(vid)
                return chr.GetRace(vid) in ORE_VNUMS
            if kind == 'Boss':
                if t != OpenLib.MONSTER_TYPE:
                    return False
                chr.SelectInstance(vid)
                return chr.GetRace(vid) in OpenLib.BOSS_IDS
        except:
            return False
        return False

    def _snapshot(self):
        snap = []
        try:
            vids = list(eXLib.InstancesList)   # copy keys first (defensive vs mid-iteration changes)
        except:
            return snap
        for vid in vids:
            try:
                if not chr.HasInstance(vid) or eXLib.IsDead(vid):
                    continue
                t = chr.GetInstanceType(vid)
                x, y, z = eXLib.GetPixelPosition(vid)
                snap.append((vid, t, x, y))
            except:
                continue
        return snap

    def _findNearest(self, kind, mx, my, snap):
        best = None
        bestD = 1e18
        for (vid, t, x, y) in snap:
            if not self._matchesT(kind, vid, t):
                continue
            d = (x - mx) * (x - mx) + (y - my) * (y - my)
            if d < bestD:
                bestD = d
                best = (vid, x, y)
        return best

    def _isStillThere(self, rec, snap):
        kind = rec.get('kind', 'Metin')
        rx, ry = rec['x'], rec['y']
        same2 = SAME_OBJECT_DIST.get(kind, DEFAULT_SAME_OBJECT_DIST) ** 2
        for (vid, t, x, y) in snap:
            if (x - rx) * (x - rx) + (y - ry) * (y - ry) >= same2:
                continue
            if self._matchesT(kind, vid, t):
                return True
        return False

    def _updateStatuses(self, mx, my, snap):
        for rec in RECORDED:
            if self._isStillThere(rec, snap):
                new = 'alive'
            else:
                appear = APPEAR_DIST_BY_KIND.get(rec.get('kind', 'Metin'), DEFAULT_APPEAR_DIST)
                d2 = (rec['x'] - mx) * (rec['x'] - mx) + (rec['y'] - my) * (rec['y'] - my)
                if d2 < appear * appear:
                    new = 'dead'           # close enough that it would be visible if alive -> killed
                else:
                    new = rec.get('status', 'alive')   # too far to tell -> keep last (no false flag)
            if rec.get('status') != new:
                rec['status'] = new
                RECORD_VERSION[0] += 1

    def OnUpdate(self):
        try:
            now = app.GetTime()
            if now < self.lastTick:           # a world reload can make the timer look backwards -> resync
                self.lastTick = now
            if now - self.lastTick < TICK_SECONDS:
                return
            self.lastTick = now
            self.ticks += 1

            # WORLD-LOAD GC GUARD (this OnUpdate ticks every frame because the window is Show()n, so it
            # runs THROUGH teleport / channel / character-switch reloads). During a reload the client tears
            # the world down and rebuilds it; touching the instance list, CHURNING the record-list widgets
            # (Refresh -> destroy/create ListBoxEx.Item objects), or spawning the StoneDetect effect THEN can
            # corrupt the Python GC's object list -> freed-object crash on the next collect (the char-switch
            # 'update_refs' crash). Do NONE of that until the map is back AND the player has a real position.
            try:
                if not background.GetCurrentMapName():
                    return
                mVID = player.GetMainCharacterIndex()
                if not mVID:
                    return
                mx, my, mz = eXLib.GetPixelPosition(mVID)
            except:
                return
            if abs(mx) < 1.0 and abs(my) < 1.0:   # world still settling (position not restored) -> wait
                return

            snap = self._snapshot()

            # keep recorded alive/dead flags fresh + live-refresh the list while it's open
            if RECORDED:
                self._updateStatuses(mx, my, snap)
                if listWindow.Board.IsShow() and listWindow._shownVer != RECORD_VERSION[0]:
                    listWindow.Refresh()

            if not self.running:
                return

            kind = self._typeLabel()
            target = self._findNearest(kind, mx, my, snap)
            if target is None:
                msg = '%s: none in range' % kind
                if STATUS_DEBUG:
                    _tc = {}
                    for _e in snap: _tc[_e[1]] = _tc.get(_e[1], 0) + 1
                    msg += ' i=%d types=%s' % (len(snap), _tc)   # dev diag (STATUS_DEBUG off for release)
                self.lInfo.SetText(msg)
                return
            vid, tx, ty = target
            try:
                effectFile = EFFECT_BY_LABEL.get(self.effCombo.GetCurrentText(), DEFAULT_EFFECT)
            except:
                effectFile = DEFAULT_EFFECT
            # eXLib.StoneDetect spawns the compass at the player, rotated to point at (tx,ty).
            eXLib.StoneDetect(mx, my, mz, tx, ty, effectFile, 0.0)
            _recordTarget(vid, tx, ty, kind)
            msg = '%s at (%.0f, %.0f)' % (kind, tx, ty)
            if STATUS_DEBUG: msg += ' i=%d t=%d' % (len(snap), self.ticks)
            self.lInfo.SetText(msg)
        except:
            pass

    def Close(self):
        self.Board.Hide()


try:                       # reload-safe (/rah): rebind the LIVE compass window to the new class
    instance
    instance.__class__ = CompassDialog
except NameError:
    instance = CompassDialog()


def switch_state():
    if instance.Board.IsShow():
        instance.Board.Hide()
    else:
        try:
            instance.Show()   # re-arm the OnUpdate loop in case a teleport dropped it
        except:
            pass
        instance.Board.Show()
