
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
# modules = sys.modules
	
# for modulename in modules:
# for modulename in sys.modules:


for modulename, module in iter(sys.modules.items()):
	# module = sys.modules[modulename]
    if HasArguments(module, ['clock']):time = module
    if HasArguments(module, ['GetPlayTime']):player = module
    if HasArguments(module, ['GetNameByVID']):chr = module
    if HasArguments(module, ['DirectEnter']):net = module
    if HasArguments(module, ['SetCameraMaxDistance']):app = module
    if HasArguments(module, ['mouseController']):mouseModule = module
    if HasArguments(module, ['ArrangeShowingChat']):chat = module
    if HasArguments(module, ['ClearSlot']):wndMgr = module
    if HasArguments(module, ['GetCurrentMapName']):background = module
    if HasArguments(module, ['SetEmpireNameMode']):chrmgr = module
    if HasArguments(module, ['GetItemName', 'SelectItem']):item = module
    if HasArguments(module, ['ArrangeTextTail', 'RegisterChatTail']):textTail = module
    if HasArguments(module, ['ItemToolTip']):uiToolTip = module
    if HasArguments(module, ['GetGradeByVID']):nonplayer = module
    if HasArguments(module, ['OpenQuestWindow', 'GameWindow']):game = module
    if HasArguments(module, ['IsSoftwareCursor']):systemSetting = module
    if HasArguments(module, ['SelectAnswer']):event = module
    if HasArguments(module, ['ENVIRONMENT_NIGHT']):constInfo = module
    if HasArguments(module, ['GenerateColor']):grp = module
    if HasArguments(module, ['GenerateFromHandle']):grpImage = module
    if HasArguments(module, ['LogBox']):dbg = module
    if HasArguments(module, ['EnableCaptureInput', 'GetReading']):ime = module
    if HasArguments(module, ['GetSkillCoolTime', 'GetSkillLevelUpPoint']):skill = module
    if HasArguments(module, ['Exist', 'Get']):pack = module
    if HasArguments(module, ['SetGeneralMotions']):playerSettingModule = module
    if HasArguments(module, ['PlaySound']):snd = module
    if HasArguments(module, ['IsPrivateShop']):shop = module
    if HasArguments(module, ['APP_TITLE']):locale = module
    if HasArguments(module, ['APP_TITLE']):localeinfo = module
    if HasArguments(module, ['CharacterWindow']):uiCharacter = module
    if HasArguments(module, ['IsAtlas']):miniMap = module
    if HasArguments(module, ['InputDialog']):uiCommon = module
    if HasArguments(module, ['factorial']):math = module
    if HasArguments(module, ['BigBoard']):uiTip = module
    if HasArguments(module, ['AtlasWindow']):uiMiniMap = module
    if HasArguments(module, ['MARKADDR_DICT']):serverInfo = module
    if HasArguments(module, ['ScriptWindow']):ui = module
    if HasArguments(module, ['SAFEBOX_PAGE_SIZE']):safebox = module
    if HasArguments(module, ['ItemToolTip']):uiToolTip = module
    if HasArguments(module, ['Interface']):interfacemodule = module
    if HasArguments(module, ['CreateEffect']):effect = module
    if HasArguments(module, ['Clear']):quest = module
    if HasArguments(module, ['AUTH_ADD_MEMBER']):guild = module
    if HasArguments(module, ['GetExceptionString']):exception = module
    if HasArguments(module, ['O_APPEND']):os = module
    if HasArguments(module, ['WRAPPER_ASSIGNMENTS']):functools = module

import eXLib,OpenLib,Movement
import UIComponents

BOARD_SIZE_X = 300
BOARD_SIZE_Y = 450
SB_LAYOUT_VER = 3   # SearchBot (release) window layout version -> switch_state rebuilds an older live window

DEBUG = False       # release: keep False. True surfaces developer diagnostics (tooltip/scan/save exceptions) in chat.

def _dbg(msg):
	if DEBUG:
		try: chat.AppendChat(3, msg)
		except: pass

def formatYang(amount):
	# Compact notation: k = thousand, kk = million; capped at kk so prices read like
	# in-shop (e.g. 500,000,000 -> "500kk", 100,000 -> "100k", 1,000 -> "1k").
	num = 0
	val = float(amount)
	while val >= 1000 and num < 2:
		val = val/1000.0
		num += 1
	s = "{0:0.1f}".format(val)
	if s.endswith(".0"):
		s = s[:-2]
	return s + ("K"*num)   # UPPERCASE K/KK (e.g. "100KK")

def convertPrice(yang,won=0):
	# Show the shop's real Won + Yang split (1 Won = 100KK). An item can be both, e.g. won=99 + yang=... ->
	# "99 Won 100KK" (a space before "Won"); won=0 + yang=500,000,000 -> "500KK" (no space, just yang).
	parts = []
	if won > 0:
		parts.append("{0} Won".format(int(won)))
	if yang > 0 or won == 0:
		parts.append(formatYang(yang))
	return " ".join(parts)

def fmtThousands(n):
	# '.' thousands separator for numbers >= 10000 (1344 -> "1344", 10999 -> "10.999", 100426 -> "100.426")
	n = int(n)
	if n < 10000:
		return str(n)
	s, out = str(n), ''
	while len(s) > 3:
		out = '.' + s[-3:] + out; s = s[:-3]
	return s + out

def nameMatch(query, itemName):
	# Case- AND space-insensitive subsequence match: every char of `query` must appear in the item name
	# (both lowercased, spaces removed) in order, gaps allowed -> matches across words. So "fragmentdee"
	# hits "Fragment de Energie" and "rubinmit" hits "Rubin Dragon Mitic". `query` is pre-normalized by caller.
	if not query:
		return True
	text = itemName.lower().replace(" ", "")
	i, n = 0, len(query)
	for ch in text:
		if ch == query[i]:
			i += 1
			if i == n:
				return True
	return False


# ===================== PATHFINDER: full-map checkpoint sweep (trading glass) =====================
# Read the current map's collision .dat (1 cell = 100 world units) and lay a serpentine grid of checkpoints
# over the walkable area, ~SWEEP_STEP cells apart (< the shop reveal disc R=55 cells -> overlap), each
# snapped to the nearest walkable cell. Output = world-coord (x,y) list ordered boustrophedon for the sweep
# engine to walk. Validated offline on metin2_map_privateshop (512x512 -> 48 checkpoints).
SWEEP_STEP     = 50     # checkpoint spacing in cells (~5000 world; R=5500)
SWEEP_SNAP_MAX = 30     # cells to search outward when a grid point lands on blocked terrain
SWEEP_SETTLE   = 0.3    # MIN sec at a checkpoint before trusting the shop snapshot (was 1.0; adaptive DRAIN
                        # snapshots from tick 1 and scans as soon as the count is stable + this min elapsed)
SWEEP_ARRIVE   = 350    # world units: close enough to a checkpoint
SWEEP_TICK     = 0.1    # OnUpdate cadence WHILE sweeping (was TIME_WAIT=0.25): polls shop open/close ~2.5x
                        # faster so we detect IsOpen/closed sooner -> much less dead time per shop roundtrip

def _loadCollisionGrid(mapName):
	try:
		f = open(eXLib.PATH + 'OpenBot/Maps/' + mapName + '.dat', 'rb')
		data = f.read().replace('\r\n', '\n').split('\n')
		f.close()
	except:
		return 0, 0, None
	if not data or len(data[0].split()) < 2:
		return 0, 0, None
	hdr = data[0].split()
	maxX, maxY = int(hdr[0]), int(hdr[1])
	return maxX, maxY, data[1:1 + maxY]

def _cellWalkable(rows, x, y, maxX, maxY):
	if x < 0 or y < 0 or x >= maxX or y >= maxY:
		return False
	r = rows[y]
	return x < len(r) and r[x] == '1'

def _snapWalkable(rows, cx, cy, maxX, maxY, maxR):
	if _cellWalkable(rows, cx, cy, maxX, maxY):
		return (cx, cy)
	for rad in range(1, maxR + 1):
		for dx in range(-rad, rad + 1):
			for dy in (-rad, rad):
				if _cellWalkable(rows, cx + dx, cy + dy, maxX, maxY):
					return (cx + dx, cy + dy)
		for dy in range(-rad + 1, rad):
			for dx in (-rad, rad):
				if _cellWalkable(rows, cx + dx, cy + dy, maxX, maxY):
					return (cx + dx, cy + dy)
	return None

def generateCheckpoints(mapName, step=SWEEP_STEP):
	maxX, maxY, rows = _loadCollisionGrid(mapName)
	if not rows:
		return []
	pts, seen, rowIdx = [], set(), 0
	for gy in range(step // 2, maxY, step):
		xs = list(range(step // 2, maxX, step))
		if rowIdx % 2 == 1:
			xs.reverse()
		for gx in xs:
			snapped = _snapWalkable(rows, gx, gy, maxX, maxY, SWEEP_SNAP_MAX)
			if snapped is not None:
				key = (snapped[0] // 4, snapped[1] // 4)
				if key not in seen:
					seen.add(key)
					pts.append((snapped[0] * 100, snapped[1] * 100))
		rowIdx += 1
	return pts

# sweep engine states
SW_IDLE, SW_WALK, SW_DRAIN, SW_SCAN, SW_DONE = range(5)


def relativeEndY(Y_value):
	return BOARD_SIZE_Y - abs(Y_value)

def relativeEndX(X_value):
	return BOARD_SIZE_X - abs(X_value)

def relativeCenterY(Y_value):
	return BOARD_SIZE_Y/2 + Y_value

def relativeCenterX(X_value):
	return BOARD_SIZE_X/2 + X_value

#Called when new shop appears
def shopCallback(vid):
	if(searchDialog.State != 0):	
		searchDialog.PlayersVids.append(vid)

class SearchDialog(ui.ScriptWindow):

	SLOT_COUNT = 40
	STATE_OPEN_SHOP = 1
	STATE_WAIT_SHOP_OPEN = 2
	STATE_WAIT_SHOP_CLOSE = 3
	Items = []
	ATTEMPTS_WAIT = 2
	numAttempts = 0
	TIME_WAIT = 0.25
 
	lastTime = 0
 
 
	class ListItem(ui.ListBoxEx.Item):
		def __init__(self, item):
			ui.ListBoxEx.Item.__init__(self)
			self.canLoad=0
			self.item=item
			self.textLine=self.__CreateTextLine(item.GetDisplay())          

		def __del__(self):
			ui.ListBoxEx.Item.__del__(self)

		def GetText(self):
			return self.item

		def SetSize(self, width, height):
			ui.ListBoxEx.Item.SetSize(self, 6*len(self.textLine.GetText()) + 4, height)

		def __CreateTextLine(self, fileName):
			textLine=ui.TextLine()
			textLine.SetParent(self)
			textLine.SetPosition(0, 0)
			textLine.SetText(fileName)
			textLine.Show()
			return textLine	

	class Item:
		def __init__(self, itemName, shopVID, count, price, slot, won = 0, posX = 0, posY = 0, ownerName = '',
		             itype = 0, isub = 0, level = 0, cmask = 0, vnum = 0, sockets = None, attrs = None):
			self.name = itemName
			self.shop = shopVID
			self.count = count
			self.yang = price                                 # raw yang the shop set for this slot
			self.won = won                                    # raw won (cheque) the shop set for this slot
			self.price = (price + won*100000000)/max(1, self.count)  # per-unit total yang, used only for sorting
			self.slot = slot
			self.shop_x = posX
			self.shop_y = posY
			self.ownerName = ownerName    # snapshotted at scan time -> name stays correct off-map (fixes the
			self.shopKey = None           # lazy-name bug); coords key set by ScanShop for dedup
			# GF-filter metadata captured from the item proto at scan time (item.SelectItem + getters):
			self.itype = itype            # EItemType (1=weapon 2=armor 3=use 28=costume ...)
			self.isub = isub              # subtype within the type (weapon: 0=sword.., armor: 0=body..)
			self.level = level            # required level (LIMIT_LEVEL); 0 = none
			self.cmask = cmask            # class-usable bitmask: 1=warrior 2=ninja 4=sura 8=shaman 16=lycan
			self.vnum = vnum              # item proto vnum (encodes +N refine) -> drives the hover tooltip
			self.sockets = sockets if sockets is not None else [0, 0, 0]   # metin/DS sockets
			self.attrs = attrs if attrs is not None else []                # [(type, value), ...] bonus attributes
		def GetDisplay(self):
			owner = self.ownerName
			if not owner:
				try: owner = chr.GetNameByVID(self.shop) or ''
				except: owner = ''
			# An OFFLINE private-shop owner has no client-side name (only a real server-based trading glass
			# can resolve it from the server), so GetNameByVID returns '' -> show "Offline" instead of blank.
			if not owner:
				owner = 'Offline'
			return " {:20}  {:12}  {:>4}  {:>11}".format(self.name[:20], owner[:12], self.count, convertPrice(self.yang,self.won))
		def getStringFormat(self):
			return "Slot: " + str(self.slot) + "  Name: " + str(self.name) + "  Price: " + str(self.price) + " yang  Count: " + str(self.count) + " Shop VID: " + str(self.shop)
	
	def __init__(self):
		self.closeAttempt = 0
		ui.ScriptWindow.__init__(self)
		eXLib.RegisterNewShopCallback(shopCallback)   # global callback: register ONCE (not in BuildWindow)

		# State init MUST precede BuildWindow: the SearchButton (OnOffButton) fires its funcState callback
		# (EnableButtonClicked -> Start/StopSweep) ONCE during construction, and those touch these attrs. On a
		# COLD client start this crashed the whole module import ('swScannedVids' missing) -- /rah never hit it
		# because the singleton already had the attrs set.
		self.PlayersVids = []
		self.Items = []
		self.State = 0
		self.PlayerIndex = 0
		# sweep engine state
		self.sweeping = False
		self.swState = SW_IDLE
		self.checkpoints = []
		self.swScannedVids = set()
		self.swScanQueue = []
		self.swScanSub = 0
		self.swScanTries = 0
		self.swCpIdx = 0

		self.BuildWindow()

		# GF-style paginated search window (additive; reads this dialog's swept .Items). Built once here;
		# /rah rebinds its class, /rah-ui rebuilds it via the cascade in _rebuildWindow.
		self.glass = TradingGlass(self)

	# All window/widget construction lives here so /rah-ui can tear it down + rebuild in place (new layout,
	# new buttons) WITHOUT a client restart. Keep global/state setup (RegisterNewShopCallback, self.Items,
	# sweep state) in __init__ so a rebuild never double-registers callbacks or wipes accumulated finds.
	def BuildWindow(self):
		# RELEASE layout: a small StoneCompass-sized window. Green start/stop button drives the map Scan; a
		# status label; and the Trading Glass button. (The old in-window item list / search / shop buttons are
		# gone -- searching + buying live in the Trading Glass window now.)
		self.Board = ui.BoardWithTitleBar()
		self.Board.SetTitleName('SearchBot')
		self.Board.SetCloseEvent(self.CloseWindow)
		self.Board.SetSize(340, 152)
		self.Board.SetCenterPosition()
		self.Board.AddFlag("movable")
		self.comp = UIComponents.Component()

		# lSweep must exist before the OnOffButton (its funcState can fire once during construction). Yellow,
		# wide enough for the full "Scan: Checkpoints N/48  Shops: N  Items: N" line.
		self.lSweep = self.comp.TextLine(self.Board, 'Scan: Idle', 12, 96, self.comp.RGB(255, 255, 0))
		self.SearchButton = self.comp.OnOffButton(self.Board, '', 'Start / Stop the map scan', 152, 40,
			funcState=self.EnableButtonClicked,
			OffUpVisual=eXLib.PATH + 'OpenBot/Images/start_0.tga', OffOverVisual=eXLib.PATH + 'OpenBot/Images/start_1.tga', OffDownVisual=eXLib.PATH + 'OpenBot/Images/start_2.tga',
			OnUpVisual=eXLib.PATH + 'OpenBot/Images/stop_0.tga', OnOverVisual=eXLib.PATH + 'OpenBot/Images/stop_1.tga', OnDownVisual=eXLib.PATH + 'OpenBot/Images/stop_2.tga')
		self.SearchButton.SetOff()
		_TGBTN = ('d:/ymir work/ui/public/large_button_01.sub','d:/ymir work/ui/public/large_button_02.sub','d:/ymir work/ui/public/large_button_03.sub')
		self.GlassBtn = self.comp.Button(self.Board, 'Trading Glass', 'Open the trading glass search', 120, 118, self.OpenGlass, *_TGBTN)
		self._sbVer = SB_LAYOUT_VER

	def _rebuildWindow(self):
		# /rah-ui: rebuild the window in place so BuildWindow LAYOUT/button edits show without a client
		# restart. Mirrors EnergyBot._rebuildWindow: remember visibility, hide, drop every widget ref so the
		# old board+children are released, rebuild, then restore visibility. State (self.Items, sweep) is kept.
		wasShown = False
		try: wasShown = self.Board.IsShow()
		except: pass
		try: self.Board.Hide()
		except: pass
		for a in ('Board', 'comp', 'SearchButton', 'GlassBtn', 'lSweep'):
			try: setattr(self, a, None)
			except: pass
		self.BuildWindow()
		# cascade: rebuild the child Trading Glass window too (keeps the two windows in sync on /rah-ui)
		try: self.glass._rebuildWindow()
		except: pass
		if wasShown:
			try: self.Board.Show()
			except: pass

	def OpenGlass(self):
		# lazy-create so it works on the LIVE instance after /rah too (that instance predates TradingGlass and
		# __init__ isn't re-run on reload). Also self-heal an OLDER-layout glass (pre-GF-panel: no cClass combo)
		# by rebuilding it in place, so the filter dropdowns appear without a restart.
		try:
			if not getattr(self, 'glass', None):
				self.glass = TradingGlass(self)
			elif getattr(self.glass, '_layoutVer', 0) != TG_LAYOUT_VER:
				# live window predates the current layout (e.g. old portrait MVP) -> rebuild it in place;
				# fall back to a fresh window if the rebuild itself fails.
				try: self.glass._rebuildWindow()
				except: self.glass = TradingGlass(self)
			self.glass.switch_state()
		except Exception as e:
			_dbg("[SearchBot] Trading Glass error: %s" % e)

	def EnableButtonClicked(self,val):
		# green start/stop button now drives the map Scan (the full-map sweep), not the old manual scanner
		if val:
			self.StartSweep()
		else:
			self.StopSweep()


	def StartSearch(self):
		self.numShopsSearched = 0
		self.State = 1
		self.PlayersVids = []
		# Do NOT reset self.Items here: we accumulate finds across areas so shops scanned
		# earlier stay in the list after we move out of their instance range.
		self.PlayerIndex = 0
		self.ScanPlayers()
		self.State = self.STATE_OPEN_SHOP

	def UpdateLabelText(self):
		pass   # release: the old manual-scan labels were removed; the scan status uses lSweep (UpdateSweepLabel)


	def MoveSelectedShop(self):
		itemList = self.ListBoxItems.GetSelectedItem()
		if itemList:
			item = itemList.GetText()
			# Prefer the position captured at search time; fall back to a live lookup
			# (owner may still be in sight) and bail out if neither yields a real
			# position, so we never walk to the map origin (the old top-left bug).
			x, y = getattr(item, 'shop_x', 0), getattr(item, 'shop_y', 0)
			if abs(x) < 1.0 and abs(y) < 1.0:
				x, y, z = eXLib.GetPixelPosition(item.shop)
			if abs(x) < 1.0 and abs(y) < 1.0:
				chat.AppendChat(3, "[SearchBot] Shop owner out of sight - re-run the search to refresh its position.")
				return
			# Route around walls with A* pathfinding (same pipeline EnergyBot uses);
			# fall back to a straight-line click-move only if the map has no collision
			# data / the target is unreachable (FindPath returns no path).
			if Movement.GoToPositionAvoidingObjects(x, y) == Movement.NO_PATH_FOUND:
				chr.MoveToDestPosition(player.GetMainCharacterIndex(), x, y)
	
	def OpenSelectedShop(self):
		itemList = self.ListBoxItems.GetSelectedItem()
		if itemList:
			item = itemList.GetText()
			net.SendOnClickPacket(item.shop)
		
		
	def StopSearch(self):
		self.State = 0

	# ============================= TRADING GLASS full-map sweep =============================
	def StartSweep(self):
		mapName = background.GetCurrentMapName()
		self.checkpoints = generateCheckpoints(mapName)
		if not self.checkpoints:
			chat.AppendChat(3, "[Scan] no collision map for '%s' (need OpenBot/Maps/%s.dat)" % (mapName, mapName))
			try: self.SearchButton.SetOff()
			except: pass
			return
		self.numShopsSearched = 0
		self.Items = []           # CLEAR the list each scan -> a clean re-scan (no old no-vnum items mixed in);
		self.swScannedVids = set()  # reset scanned VIDs so this session's shops are rescanned, not skipped
		self.swScanQueue = []
		self.swScanSub = 0
		self.swScanTries = 0
		self.swCpIdx = 0
		self.State = 0            # disable the old manual scanner
		self.swState = SW_WALK
		self.sweeping = True
		chat.AppendChat(3, "[Scan] START '%s': %d checkpoints" % (mapName, len(self.checkpoints)))
		self.UpdateSweepLabel()

	def StopSweep(self):
		self.sweeping = False
		self.swState = SW_IDLE
		try: Movement.StopMovement()
		except: pass
		# StopMovement only stops issuing NEW moves; the last MoveToDestPosition is still running server-side,
		# so the char keeps walking to the next path point after Stop. Send a move to the CURRENT position to
		# cancel the in-flight move -> character halts immediately (same trick as EnergyBot._stopBot).
		try:
			mx, my, mz = player.GetMainCharacterPosition()
			chr.MoveToDestPosition(player.GetMainCharacterIndex(), int(mx), int(my))
		except: pass
		try:
			if shop.IsOpen(): net.SendShopEndPacket()
		except: pass
		self.UpdateSweepLabel()
		chat.AppendChat(3, "[Scan] STOPPED (%d shops, %d items)" % (len(self.swScannedVids), len(self.Items)))

	def _sweepDone(self):
		self.sweeping = False
		self.swState = SW_DONE
		try: Movement.StopMovement()
		except: pass
		try: self.SearchButton.SetOff()   # reset the green start/stop button when the scan finishes
		except: pass
		self.UpdateSweepLabel()
		chat.AppendChat(3, "[Scan] DONE: %d shops scanned, %d items indexed" % (len(self.swScannedVids), len(self.Items)))
		self.SaveScan()   # persist to disk so a restart/crash doesn't cost a full re-scan

	# ---- disk persistence: one tab-separated file per map under OpenBot/Data/ (no json dependency) ----
	def _scanPath(self, mapName):
		return eXLib.PATH + 'OpenBot/Data/tradingglass_' + (mapName or 'unknown') + '.txt'

	def SaveScan(self):
		try:
			d = eXLib.PATH + 'OpenBot/Data/'
			try: os.makedirs(d)
			except: pass
			mapName = background.GetCurrentMapName() or 'unknown'
			try: ts = int(time.time())
			except: ts = 0
			f = open(self._scanPath(mapName), 'w')
			f.write("#\t%s\t%d\t%d\n" % (mapName, ts, len(self.Items)))
			for it in self.Items:
				_sk = ','.join(str(s) for s in (getattr(it, 'sockets', None) or []))
				_at = ';'.join('%d,%d' % (t, v) for (t, v) in (getattr(it, 'attrs', None) or []))
				f.write("%s\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%s\t%d\t%d\t%d\t%d\t%d\t%s\t%s\n" % (
					(it.name or '').replace('\t', ' ').replace('\n', ' '), it.shop, it.count, it.yang, it.won,
					it.slot, int(it.shop_x), int(it.shop_y), (it.ownerName or '').replace('\t', ' '),
					getattr(it, 'itype', 0), getattr(it, 'isub', 0), getattr(it, 'level', 0), getattr(it, 'cmask', 0),
					getattr(it, 'vnum', 0), _sk, _at))
			f.close()
			chat.AppendChat(3, "[Scan] saved %d items -> OpenBot/Data/tradingglass_%s.txt" % (len(self.Items), mapName))
		except Exception as e:
			_dbg("[Scan] save error: %s" % e)

	def LoadScan(self, mapName=None):
		try:
			if not mapName:
				mapName = background.GetCurrentMapName() or 'unknown'
			f = open(self._scanPath(mapName), 'r')
			data = f.read(); f.close()
			ts, loaded = 0, []
			for ln in data.split('\n'):
				if not ln:
					continue
				if ln[0] == '#':
					pp = ln.split('\t')
					if len(pp) >= 3:
						try: ts = int(pp[2])
						except: ts = 0
					continue
				p = ln.split('\t')
				if len(p) < 9:
					continue
				try:
					_it = int(p[9])  if len(p) > 9  else 0   # backward-compat: shorter old saves default new fields
					_is = int(p[10]) if len(p) > 10 else 0
					_lv = int(p[11]) if len(p) > 11 else 0
					_cm = int(p[12]) if len(p) > 12 else 0
					_vn = int(p[13]) if len(p) > 13 else 0
					_sk = [int(s) for s in p[14].split(',') if s != ''] if len(p) > 14 and p[14] else [0, 0, 0]
					_at = []
					if len(p) > 15 and p[15]:
						for _pair in p[15].split(';'):
							_tv = _pair.split(',')
							if len(_tv) == 2:
								_at.append((int(_tv[0]), int(_tv[1])))
					it = SearchDialog.Item(p[0], int(p[1]), int(p[2]), int(p[3]), int(p[5]), int(p[4]), int(p[6]), int(p[7]), p[8], _it, _is, _lv, _cm, _vn, _sk, _at)
					it.shopKey = (int(round(it.shop_x / 100.0)), int(round(it.shop_y / 100.0)))
					loaded.append(it)
				except:
					pass
			self.Items = loaded
			age = ''
			try:
				if ts:
					secs = int(time.time()) - ts
					age = (' (%dm ago)' % (secs // 60)) if secs < 3600 else (' (%dh ago)' % (secs // 3600))
			except:
				pass
			chat.AppendChat(3, "[Glass] loaded %d saved items for %s%s" % (len(loaded), mapName, age))
			return True
		except Exception as e:
			_dbg("[Glass] no saved scan for '%s' (%s)" % (mapName, e))
			return False

	def UpdateSweepLabel(self):
		try:
			self.lSweep.SetText("Scan: Checkpoints %d/%d  Shops: %s  Items: %s" %
				(self.swCpIdx, len(self.checkpoints), fmtThousands(len(self.swScannedVids)), fmtThousands(len(self.Items))))
		except:
			pass

	def _inRangeShopVids(self):
		vids = []
		try:
			for x in eXLib.InstancesList:
				if not chr.HasInstance(x):
					continue
				chr.SelectInstance(x)
				r = chr.GetRace(x)
				if r >= OpenLib.MIN_RACE_SHOP and r <= OpenLib.MAX_RACE_SHOP:
					vids.append(x)
		except:
			pass
		return vids

	def _sweepTick(self):
		if self.swState == SW_WALK:
			if self.swCpIdx >= len(self.checkpoints):
				self._sweepDone(); return
			cp = self.checkpoints[self.swCpIdx]
			if OpenLib.isPlayerCloseToPosition(cp[0], cp[1], SWEEP_ARRIVE):
				Movement.StopMovement()
				self.swState = SW_DRAIN
				self.swDrainStart = app.GetTime()
				self.swLastCount = -1
				self.swStable = 0
			else:
				Movement.GoToPositionAvoidingObjects(cp[0], cp[1])

		elif self.swState == SW_DRAIN:
			# Adaptive: the server streams spawn packets in AFTER we stop, so snapshot the in-range shop
			# count EVERY tick from arrival and scan as soon as it is STABLE across 2 snapshots AND a short
			# min-settle has elapsed -- instead of always burning the full second. If shops loaded fast we
			# start scanning at ~SWEEP_SETTLE; if they trickle in we keep waiting until stable (no misses).
			vids = self._inRangeShopVids()
			if len(vids) == self.swLastCount:
				self.swStable += 1
			else:
				self.swStable = 0
				self.swLastCount = len(vids)
			_drainDt = app.GetTime() - self.swDrainStart   # <0 means clock reset (world reload) -> treat as elapsed
			if self.swStable >= 2 and (_drainDt < 0 or _drainDt >= SWEEP_SETTLE):
				self.swScanQueue = [v for v in vids if v not in self.swScannedVids]
				self.swState = SW_SCAN

		elif self.swState == SW_SCAN:
			if not self.swScanQueue:
				self.swCpIdx += 1
				self.swState = SW_WALK
				self.UpdateSweepLabel()
				return
			vid = self.swScanQueue[0]
			if self.swScanSub == 0:                       # open the shop
				if not chr.HasInstance(vid):
					self.swScanQueue.pop(0); return       # despawned -> skip
				net.SendOnClickPacket(vid)
				self.swScanSub = 1; self.swScanTries = 0
			elif self.swScanSub == 1:                     # wait open -> scan -> CLOSE (close-before-open)
				if shop.IsOpen():
					self.ScanShop(vid)
					self.swScannedVids.add(vid)
					net.SendShopEndPacket()
					self.swScanSub = 2
				else:
					self.swScanTries += 1
					if self.swScanTries > 5:              # never opened -> give up on this shop
						self.swScanQueue.pop(0); self.swScanSub = 0
			elif self.swScanSub == 2:                     # wait closed -> next shop
				if not shop.IsOpen():
					self.swScanQueue.pop(0); self.swScanSub = 0
			self.UpdateSweepLabel()

	def CloseWindow(self):
		self.Board.Hide()
		self.Board.Destroy()


	def UpdateItemList(self):
		value = (self.ItemEditBoxValue.GetText() or "").strip().lower()
		self.ListBoxItems.RemoveAllItems()
		lst = []
		for item in self.Items:
			if value in item.name.lower():
				lst.append(item)
		lst.sort(key=lambda x: x.price)
		for item in lst:
			self.ListBoxItems.AppendItem(self.ListItem(item))
  
	def ScanPlayers(self):
		for x in eXLib.InstancesList:
			test = chr.HasInstance(x)
			chr.SelectInstance(x)
			if test != 0 and chr.GetRace(x) >= OpenLib.MIN_RACE_SHOP and chr.GetRace(x) <= OpenLib.MAX_RACE_SHOP:
				self.PlayersVids.append(x)
		self.UpdateLabelText()
		return True

	def BuySelectedItem(self):
		itemList = self.ListBoxItems.GetSelectedItem()
		if itemList:
			item = itemList.GetText()
			self.BuyItemDirectly(item)

	def BuyItemDirectly(self,item):
		vid = item.shop
		slot = item.slot
		x,y,z = player.GetMainCharacterPosition()
		dst_x,dst_y,dst_z = eXLib.GetPixelPosition(vid)
		if(dst_x + dst_y < 0.000001):
			return
		Movement.TeleportStraightLine(x,y,dst_x,dst_y)
		net.SendOnClickPacket(vid)
		net.SendShopBuyPacket(slot)
		Movement.TeleportStraightLine(dst_x,dst_y,x,y)
		net.SendShopEndPacket()

	def OpenShop(self,vid):
		if self.IsShopOpen() == False and chr.HasInstance(vid):
			net.SendOnClickPacket(vid)

	def IsShopOpen(self):
		return shop.IsOpen()
    
	def CloseShop(self):
		if self.IsShopOpen() == True:
			net.SendShopEndPacket()

	def ScanShop(self,vid):
		self.numShopsSearched+=1
		chr.SelectInstance(vid)
		# Capture the shop owner's position now, while the shop is open and the instance
		# is guaranteed loaded. Re-reading it later (owner out of sight) returns (0,0,0)
		# and would send the character walking to the map origin (top-left).
		shop_x, shop_y, shop_z = eXLib.GetPixelPosition(vid)
		# NaN/inf guard (26.1.11): GetPixelPosition can hand back NaN for a shop owner in some states, and
		# int(round(NaN / 100.0)) below raises "cannot convert float NaN to integer", aborting the whole
		# scan. We're standing right at the shop, so fall back to the player's position for a valid coord.
		if not (shop_x == shop_x and shop_y == shop_y and abs(shop_x) < 1e12 and abs(shop_y) < 1e12):
			try:
				_mv = player.GetMainCharacterIndex()
				shop_x, shop_y, shop_z = eXLib.GetPixelPosition(_mv)
			except:
				pass
			if not (shop_x == shop_x and shop_y == shop_y and abs(shop_x) < 1e12 and abs(shop_y) < 1e12):
				shop_x, shop_y, shop_z = 0.0, 0.0, 0.0   # last-resort: never let a NaN reach int(round())
		try: ownerName = chr.GetNameByVID(vid) or ''   # snapshot NOW (correct off-map / after despawn)
		except: ownerName = ''
		# Dedup by stable COORDS key (VIDs recycle across map reloads): a re-scan of the SAME shop
		# location refreshes it, while keeping items from shops scanned elsewhere.
		key = (int(round(shop_x / 100.0)), int(round(shop_y / 100.0)))
		self.Items = [it for it in self.Items if getattr(it, 'shopKey', None) != key]
		for x in range(0,self.SLOT_COUNT*shop.GetTabCount()):
			id = shop.GetItemID(x)
			if id != 0:
				price = shop.GetItemPrice(x)
				name = item.GetItemNameByVnum(id)
				if id == 50300:
					sk = shop.GetItemMetinSocket(x,0)
					skill_name = str(skill.GetSkillName(sk))
					name = str(skill_name) + " " + name
				count = shop.GetItemCount(x)
				itype, isub, level, cmask = self._itemMeta(id)
				try: sockets = [shop.GetItemMetinSocket(x, si) for si in range(3)]
				except: sockets = [0, 0, 0]
				attrs = []
				try:
					for ai in range(7):                    # ITEM_ATTRIBUTE_SLOT_MAX_NUM; GetItemAttribute -> (type, value)
						attrs.append(shop.GetItemAttribute(x, ai))
				except: pass
				it = self.Item(name,vid,count,price,x,shop.GetItemCheque(x),shop_x,shop_y,ownerName,itype,isub,level,cmask,id,sockets,attrs)
				it.shopKey = key
				self.Items.append(it)
		self.UpdateLabelText()
		return key

	def _itemMeta(self, vnum):
		# Read GF-filter metadata from the item proto (verified against client-source PythonItemModule.cpp):
		# item.SelectItem loads the proto; GetItemType/SubType + GetLimit(LIMIT_LEVEL=1) + IsAntiFlag give
		# type / subtype / required-level / class-usability. Guarded -- a bad vnum just yields zeros.
		itype = isub = level = cmask = 0
		try:
			item.SelectItem(vnum)
			itype = item.GetItemType()
			isub = item.GetItemSubType()
			for _li in range(2):                 # ITEM_LIMIT_MAX_NUM = 2
				_lt, _lv = item.GetLimit(_li)
				if _lt == 1:                     # LIMIT_LEVEL
					level = _lv; break
			if not item.IsAntiFlag(4):      cmask |= 1   # ITEM_ANTIFLAG_WARRIOR  (1<<2)
			if not item.IsAntiFlag(8):      cmask |= 2   # ITEM_ANTIFLAG_ASSASSIN (1<<3) -> ninja
			if not item.IsAntiFlag(16):     cmask |= 4   # ITEM_ANTIFLAG_SURA     (1<<4)
			if not item.IsAntiFlag(32):     cmask |= 8   # ITEM_ANTIFLAG_SHAMAN   (1<<5)
			# NOTE: this server has NO anti-Lycan/Wolfman flag (verified: antiflags stop at SAFEBOX 1<<17), so
			# Lycan usability is DERIVED at filter time from the base 4 bits (DoSearch), not captured here.
		except:
			pass
		return itype, isub, level, cmask
        
	def OnUpdate(self):
		currTime = app.GetTime()
		# Clock-reset-safe throttle: a channel switch / world reload makes app.GetTime() jump BACKWARD while
		# self.lastTime still holds the old (larger) value, so currTime-lastTime goes NEGATIVE and the old
		# check ( < TIME_WAIT ) stayed true forever -> OnUpdate bailed every frame and the sweep never ticked
		# after a channel switch. Only throttle on a small POSITIVE delta; a negative delta = clock reset ->
		# fall through and let the branch below resync self.lastTime = currTime.
		_wait = SWEEP_TICK if getattr(self, 'sweeping', False) else self.TIME_WAIT
		_dt = currTime - self.lastTime
		if 0 <= _dt < _wait:
			return
		# GC-safe world-load guard: this window is always shown, so OnUpdate ticks THROUGH teleports.
		# Never touch the instance list / open shops / churn the list during a reload (freed-object crash).
		try:
			if not background.GetCurrentMapName():
				return
			if not player.GetMainCharacterIndex():
				return
		except:
			return

		if getattr(self, 'sweeping', False):
			self.lastTime = currTime
			try:
				self._sweepTick()
			except Exception as _e:
				# Surface a real tick failure and STOP -- never silently freeze the sweep (a silent
				# except:pass here is what hid the channel-switch clock bug). One message, not a spam loop.
				try: chat.AppendChat(3, "[Scan] tick error, stopping: %s" % _e)
				except: pass
				try: self.StopSweep()
				except: self.sweeping = False
			return

		if self.State == 0:
			return

		self.lastTime = currTime
       
		if self.State == self.STATE_OPEN_SHOP and len(self.PlayersVids)>0:
			self.PlayerVID = self.PlayersVids.pop()
			self.OpenShop(self.PlayerVID)
			self.State = self.STATE_WAIT_SHOP_OPEN
			return
        
		elif self.State == self.STATE_WAIT_SHOP_OPEN:
			if self.numAttempts > self.ATTEMPTS_WAIT:
				self.numAttempts = 0
				self.State = self.STATE_WAIT_SHOP_CLOSE
				return
			if self.IsShopOpen() == True:
				self.State = self.STATE_WAIT_SHOP_CLOSE
				self.ScanShop(self.PlayerVID)
				self.CloseShop()
				self.numAttempts = 0
			else:
				self.OpenShop(self.PlayerVID)
				self.numAttempts += 1 
			return
        
		elif self.State == self.STATE_WAIT_SHOP_CLOSE:
			if self.IsShopOpen() == False:
				self.numAttempts = 0
				self.State = self.STATE_OPEN_SHOP
				return
			else:
				if(self.closeAttempt>3):
					self.closeAttempt = 0
					self.CloseShop()
					return
				self.closeAttempt += 1 
				return
        

# ================= TRADING GLASS: GF-style search window over the swept item list =================
# Additive window (the debug SearchBot stays untouched). Reads the shared swept list (owner.Items) and shows
# it GF-style: a filter panel (Name, Class/Category/Subtype dropdowns, Level + Price ranges) over a PAGINATED
# result grid -- only ONE page of rows is appended to the listbox, so filtering 38k+ items renders instantly.
# Filters use metadata captured at scan time (item type/subtype/required-level/class-usability).
TG_W, TG_H = 590, 370          # EXACT GF trading-glass dimensions (uiPrivateShopSearch BoardWithTitleBar 590x370)
TG_ROWS = 10                   # visible result rows
TG_LAYOUT_VER = 19             # bump on ANY layout change -> OpenGlass rebuilds a live window that predates it
SHOP_MAX_YANG = 301999999999   # max a private shop total can reach: 1,999,999,999 Yang + 3000 Won (3000*1e8 + 1,999,999,999)
TG_TIP_DELAY  = 0.15           # hover-intent: seconds the cursor must rest on a row before its tooltip is built
TG_PS = "d:/ymir work/ui/privatesearch/"   # GF trading-glass image dir (present in the live GF client)
TG_ROW_X, TG_ROW_Y0, TG_ROW_STEP = 138, 60, 22   # result-row geometry (2px lower, inset 2px each side)
TG_ROW_W, TG_ROW_H = 432, 20
TG_ROW_COLS = (92, 232, 307, 384)   # cell CENTER x-offsets (Name column widened; all cells center-aligned)
try:
	TG_ROW_BASE     = grp.GenerateColor(1.0, 0.90, 0.50, 0.10)   # faint yellow on EVERY row (GF default look)
	TG_OVER_COLOR   = grp.GenerateColor(1.0, 0.88, 0.45, 0.22)   # hovered row
	TG_SELECT_COLOR = grp.GenerateColor(1.0, 0.80, 0.32, 0.38)   # gold = selected/focused row (lighter than before)
	TG_ROW_BORDER   = grp.GenerateColor(0.35, 0.30, 0.20, 0.5)   # row separator line
except:
	TG_ROW_BASE = 0x1AFFE680; TG_OVER_COLOR = 0x38FFE173; TG_SELECT_COLOR = 0x60FFCC52; TG_ROW_BORDER = 0x804D3F33
TG_LIST_BG     = 0xA01C1814     # dark (but not black) table background behind the rows
TG_LIST_BORDER = 0xFF5A4A32     # table frame border

# ComboBox label -> filter value (first entry is the placeholder = no filter). Enum values are verified from
# client-source ItemData.h (EItemType / EWeaponSubTypes / EArmorSubTypes / EItemAntiFlag).
TG_CLASS = [('Class', None), ('Warrior', 1), ('Ninja', 2), ('Sura', 4), ('Shaman', 8), ('Lycan', 16)]
TG_CAT = [('Category', None), ('Weapon', (1,)), ('Armor', (2,)), ('Costume', (28,)),
          ('Accessory', (33, 34)), ('Use/Potion', (3,)), ('Material', (5,)),
          ('Skillbook', (17,)), ('Alchemy', (29, 30))]
# Subtype dropdown lists ALL subtypes at once (lax filtering, not scoped to Category). Each maps to (type, subtype).
TG_SUB = [('Subtype', None),
          ('Sword', (1, 0)), ('Dagger', (1, 1)), ('Bow', (1, 2)), ('Two-Handed', (1, 3)),
          ('Bell', (1, 4)), ('Fan', (1, 5)), ('Claw', (1, 8)),   # Claw = Lycan weapon (WEAPON_CLAW subtype 8; MOUNT_SPEAR reserves 7)
          ('Body', (2, 0)), ('Helmet', (2, 1)), ('Shield', (2, 2)), ('Bracelet', (2, 3)),
          ('Boots', (2, 4)), ('Necklace', (2, 5)), ('Earring', (2, 6))]
TG_CLASS_MAP = dict(TG_CLASS)
TG_CAT_MAP = dict(TG_CAT)
TG_SUB_MAP = dict(TG_SUB)


def refineFromName(name):
	# Refine (+N) isn't exposed by the shop module, but the private-shop item NAME carries it ("Long Sword+9",
	# "Skeleton Helmet +9"). Parse the trailing +N so the "Item Lvl" filter works -- and works on ALREADY-swept
	# items too (no re-sweep needed, since we always have the name). Returns 0 when there's no +N.
	try:
		i = name.rfind('+')
		if i < 0:
			return 0
		j = i + 1
		while j < len(name) and name[j] == ' ':
			j += 1
		num = ''
		while j < len(name) and name[j].isdigit():
			num += name[j]; j += 1
		return int(num) if num else 0
	except:
		return 0


class TGRowButton(ui.Window):
	# GF result row (ui.Window + grp): 4 CENTER-aligned cells, golden highlight on hover/select via OnRender,
	# and on hover it asks the parent glass to show the ONE shared ItemToolTip for this row's item (the same
	# standard inventory tooltip, which colors requirements against the current char -> green/red).
	def __init__(self):
		ui.Window.__init__(self, "UI")
		self.item = None
		self.onSelect = None
		self.glass = None
		self.isOver = False
		self.selected = False
		self._overSince = 0.0   # hover-intent timer: tooltip builds only after the cursor rests on the row
		self._tipShown = False
		self.cells = []
		for i in range(4):
			t = ui.TextLine()
			t.SetParent(self)
			t.SetPosition(TG_ROW_COLS[i], 4)
			t.SetHorizontalAlignCenter()      # value grows left+right from the column center (like the GF headers)
			t.SetOutline()
			t.Show()
			self.cells.append(t)
	def __del__(self):
		ui.Window.__del__(self)
	def Setup(self, it, onSelect, glass):
		self.item = it
		self.onSelect = onSelect
		self.glass = glass
		self.selected = False
		owner = it.ownerName or ''
		if not owner or owner == 'None':
			try: owner = chr.GetNameByVID(it.shop) or ''
			except: owner = ''
		if not owner or owner == 'None':
			owner = 'Offline'                     # offline owner -> no client-side name (never show "None")
		vals = (str(it.name)[:30], owner[:16], str(it.count), convertPrice(it.yang, it.won))
		for i in range(4):
			self.cells[i].SetText(vals[i])
	def OnMouseOverIn(self):
		# start the hover-intent timer only -- DON'T build the (heavy) tooltip yet; OnUpdate builds it once the
		# cursor has rested TG_TIP_DELAY on this row, so flying past many rows costs nothing.
		self.isOver = True
		self._overSince = app.GetTime()
		self._tipShown = False
	def OnMouseOverOut(self):
		self.isOver = False
		if getattr(self, '_tipShown', False) and self.glass:
			try: self.glass._hideItemTooltip()
			except: pass
		self._tipShown = False
	def OnUpdate(self):                 # backup hover detection if OnMouseOverIn/Out don't fire for a child Window
		if not self.IsShow():
			return
		inside = self.IsIn()
		if inside and not self.isOver:
			self.OnMouseOverIn()
		elif (not inside) and self.isOver:
			self.OnMouseOverOut()
		elif inside and self.isOver and not getattr(self, '_tipShown', False):
			dt = app.GetTime() - getattr(self, '_overSince', 0.0)
			if dt < 0:                  # clock reset (world reload) -> restart the timer
				self._overSince = app.GetTime()
			elif dt >= TG_TIP_DELAY:
				self._tipShown = True
				if self.glass:
					try: self.glass._showItemTooltip(self.item)
					except: pass
	def OnMouseLeftButtonUp(self):
		if self.onSelect:
			try: self.onSelect(self)
			except: pass
	def OnRender(self):
		x, y = self.GetGlobalPosition()
		w, h = TG_ROW_W, TG_ROW_H
		if self.selected:  grp.SetColor(TG_SELECT_COLOR)   # gold
		elif self.isOver:  grp.SetColor(TG_OVER_COLOR)     # hover
		else:              grp.SetColor(TG_ROW_BASE)       # faint yellow on every row (GF default)
		grp.RenderBar(x, y, w, h)
		grp.SetColor(TG_ROW_BORDER)
		grp.RenderLine(x, y + h - 1, w, 0)


class TGButton(ui.Window):
	# A button whose visual is a ExpandedImageBox scaled on X -> lets Save/Go/Buy reuse the 122x22 GF findbutton
	# at 61x22 (half width, IDENTICAL height to Search). ui.Button can't scale; ExpandedImageBox.SetScale can.
	def __init__(self):
		ui.Window.__init__(self, "UI")
		self.callback = None
		self.visuals = {}
		self.lbl = None
	def __del__(self):
		ui.Window.__del__(self)
	def Build(self, board, text, x, y, w, h, callback, subUp, subOver, subDown, scaleX):
		self.SetParent(board); self.SetPosition(x, y); self.SetSize(w, h)
		self.callback = callback
		self.visuals = {}
		for st, sub in (('up', subUp), ('over', subOver), ('down', subDown)):
			im = ui.ExpandedImageBox(); im.SetParent(self); im.SetPosition(0, 0)
			try: im.AddFlag("not_pick")           # let the click pass THROUGH the image to this button window
			except: pass
			try: im.LoadImage(sub)
			except: pass
			try: im.SetScale(scaleX, 1.0)
			except: pass
			im.Show(); self.visuals[st] = im
		self.visuals['over'].Hide(); self.visuals['down'].Hide()
		if text:
			t = ui.TextLine(); t.SetParent(self); t.SetPosition(w // 2, h // 2)
			t.SetHorizontalAlignCenter(); t.SetVerticalAlignCenter()
			t.SetText(text); t.Show()             # default white font, NO outline -> identical to Search's label
			try: t.AddFlag("not_pick")
			except: pass
			self.lbl = t
		self.Show()
	def _state(self, st):
		for k, im in self.visuals.items():
			(im.Show() if k == st else im.Hide())
	def OnMouseOverIn(self):  self._state('over')
	def OnMouseOverOut(self): self._state('up')
	def OnMouseLeftButtonDown(self): self._state('down')
	def OnMouseLeftButtonUp(self):
		self._state('over')
		if self.callback:
			try: self.callback()
			except: pass


class TradingGlass(ui.ScriptWindow):
	def __init__(self, owner):
		ui.ScriptWindow.__init__(self)
		self.owner = owner        # SearchDialog: source of the shared swept .Items
		self.results = []
		self.page = 0
		self.BuildWindow()

	def _img(self, path, x, y):
		im = ui.ImageBox()
		im.SetParent(self.Board)
		im.SetPosition(x, y)
		try: im.LoadImage(path)
		except: pass
		im.Show()
		return im

	def _eimg(self, sub, x, y):
		try: return self.comp.ExpandedImage(self.Board, x, y, TG_PS + sub)
		except: return None

	def _borderbox(self, x, y, w, h, color, thick=1):
		# a thin rectangular border made of 4 ui.Bars (top/bottom/left/right)
		bars = []
		for bx, by, bw, bh in ((x, y, w, thick), (x, y + h - thick, w, thick), (x, y, thick, h), (x + w - thick, y, thick, h)):
			b = ui.Bar(); b.SetParent(self.Board); b.SetPosition(bx, by); b.SetSize(bw, bh); b.SetColor(color); b.Show()
			bars.append(b)
		return bars

	def _tilde(self, x, y):
		t = ui.TextLine(); t.SetParent(self.Board); t.SetPosition(x, y); t.SetText('~'); t.SetOutline(); t.Show()
		return t

	def _flabel(self, y, text):
		# GF left-filter label: the leftNameImg gradient strip with centered label text
		img = self._img(TG_PS + "private_leftNameImg.sub", 10, y)
		txt = ui.TextLine(); txt.SetParent(img); txt.SetPosition(60, 5)
		txt.SetHorizontalAlignCenter(); txt.SetText(text); txt.SetOutline(); txt.Show()
		return img, txt

	def _slot(self, sub, x, y, editw, default, maxlen, number=True):
		# GF input slot image with a bare EditLine on it (number-mode for the range fields, text for name)
		img = self._img(TG_PS + sub, x, y)
		if number:
			ed = self.comp.OnlyEditLine(img, editw, 15, 4, 2, default, maxlen)
		else:
			ed = ui.EditLine(); ed.SetParent(img); ed.SetPosition(4, 2); ed.SetSize(editw, 15)
			ed.SetMax(maxlen); ed.SetText(default); ed.Show()
		return img, ed

	def BuildWindow(self):
		self.comp = UIComponents.Component()
		self.Board = ui.BoardWithTitleBar()
		self.Board.SetTitleName('Trading Glass')
		self.Board.SetSize(TG_W, TG_H)
		self.Board.SetCenterPosition()
		self.Board.AddFlag('movable')
		self.Board.SetCloseEvent(self.switch_state)
		_FIND = (TG_PS + "private_findbuttonImg01.sub", TG_PS + "private_findbuttonImg02.sub", TG_PS + "private_findbuttonImg03.sub")

		# --- result table: dark bg + framed border + GF corner pieces. (GF's 9-slice .tga edges need SetScale
		# to stretch, unreliable in uBot's toolkit -> a solid dark bg + thin border give the framed-dark-list
		# look reliably; the GF corner .subs still frame the corners.) ---
		# list container: 2px lower + 2px inset each side; bottom aligned with the Name-input bottom (~313).
		# GF corner images removed per request -> just a dark bg + thin border.
		self.listBg = ui.Bar()
		self.listBg.SetParent(self.Board); self.listBg.SetPosition(135, 57); self.listBg.SetSize(438, 256)
		self.listBg.SetColor(TG_LIST_BG); self.listBg.Show()
		self._border = self._borderbox(135, 56, 438, 258, TG_LIST_BORDER)
		self._frame = []
		self.toolTip = uiToolTip.ItemToolTip()   # ONE shared standard tooltip (like inventory), shown on row hover

		# --- result header (gray gradient tab_menu) + column titles CENTERED over each column ---
		self.hdrImg = self._img("d:/ymir work/ui/tab_menu_01.tga", 135, 39)
		self.headers = []
		for text, cx in (('Name', 94), ('Seller', 236), ('Count', 309), ('Price', 386)):
			t = ui.TextLine(); t.SetParent(self.hdrImg); t.SetPosition(cx, 4)
			t.SetHorizontalAlignCenter(); t.SetText(text); t.SetOutline(); t.Show()
			self.headers.append(t)

		# --- pagination arrows (GF images: first/prev ... next/last) + page number ---
		self.bFirst = self.comp.Button(self.Board, '', '', 210, 291, self.FirstPage, TG_PS+"private_first_prev_btn_01.sub", TG_PS+"private_first_prev_btn_02.sub", TG_PS+"private_first_prev_btn_01.sub")
		self.bPrev  = self.comp.Button(self.Board, '', '', 240, 291, self.Prev,      TG_PS+"private_prev_btn_01.sub",       TG_PS+"private_prev_btn_02.sub",       TG_PS+"private_prev_btn_01.sub")
		self.bNext  = self.comp.Button(self.Board, '', '', 453, 291, self.Next,      TG_PS+"private_next_btn_01.sub",       TG_PS+"private_next_btn_02.sub",       TG_PS+"private_next_btn_01.sub")
		self.bLast  = self.comp.Button(self.Board, '', '', 483, 291, self.LastPage,  TG_PS+"private_last_next_btn_01.sub",  TG_PS+"private_last_next_btn_00.sub",  TG_PS+"private_last_next_btn_01.sub")
		self.lPage  = self.comp.TextLine(self.Board, '1 / 1', 351, 296, self.comp.RGB(255, 255, 255))   # white, vertically centered on the arrows
		try: self.lPage.SetHorizontalAlignCenter(); self.lPage.SetVerticalAlignCenter()
		except: pass

		# --- result rows: fixed pool reused across pages (children of Board -> get OnUpdate/mouse events) ---
		self.rows = []
		for i in range(TG_ROWS):
			rb = TGRowButton()
			rb.SetParent(self.Board)
			rb.SetPosition(TG_ROW_X, TG_ROW_Y0 + TG_ROW_STEP * i)
			rb.SetSize(TG_ROW_W, TG_ROW_H)
			rb.Hide()
			self.rows.append(rb)

		# --- LEFT filter panel (exact GF positions) ---
		self.jobImg,   self.jobLbl   = self._flabel(35,  'Classes')
		self.typeImg,  self.typeLbl  = self._flabel(75,  'Items')
		self.lvlImg,   self.lvlLbl   = self._flabel(135, 'Level')
		self.refImg,   self.refLbl   = self._flabel(175, 'Item Level')
		self.priceImg, self.priceLbl = self._flabel(215, 'Price (Won)')
		self.nameImg,  self.nameLbl  = self._flabel(275, 'Name')
		self.lvlTilde = self._tilde(65, 158); self.refTilde = self._tilde(65, 200)
		self.minLvlImg, self.fLMin = self._slot("private_leftSlotHalfImg.sub", 12, 155, 36, "0",   3)
		self.maxLvlImg, self.fLMax = self._slot("private_leftSlotHalfImg.sub", 90, 155, 36, "120", 3)
		self.minRefImg, self.fRMin = self._slot("private_leftSlotHalfImg.sub", 12, 195, 36, "0",  3)
		self.maxRefImg, self.fRMax = self._slot("private_leftSlotHalfImg.sub", 90, 195, 36, "15", 3)   # +N goes to 15
		# Price filter is in WON (1 Won = 100,000,000 Yang = 100 KK). Default range 0..3000 = the full span a private
		# shop can hold (max 3,000 Won). Ex: max=1 shows items worth 100 KK and under. DoSearch converts Won->Yang.
		self.minPImg,   self.fPMin = self._slot("private_leftSlotImg.sub",     12, 235, 115, "0",    4)
		self.maxPImg,   self.fPMax = self._slot("private_leftSlotImg.sub",     12, 255, 135, "3000", 4)
		self.nameSlotImg, self.fName = self._slot("private_leftSlotImg.sub",   12, 295, 136, "", 20, False)

		# --- buttons: Search = 122x22 GF findbutton. Save/Go/Buy = the SAME findbutton scaled to 61x22 (half
		# width, IDENTICAL height) via TGButton. Save left edge = list-left (136); Buy right edge = list-right (574). ---
		self.bSearch = self.comp.Button(self.Board, 'Search', '', 10, 337, self.DoSearch, *_FIND)
		self.bSave = TGButton(); self.bSave.Build(self.Board, 'Save', 134, 337, 61, 22, self.DoSave, _FIND[0], _FIND[1], _FIND[2], 0.5)   # left edge = list-left
		self.bGo   = TGButton(); self.bGo.Build(self.Board,   'Go',   514, 337, 61, 22, self.Go,     _FIND[0], _FIND[1], _FIND[2], 0.5)   # right edge = list-right (Buy removed)
		# "N Items" -- centered on the list box (x=357) and vertically with the Save/Go button row
		self.lCount = self.comp.TextLine(self.Board, '', 357, 348, self.comp.RGB(255, 255, 255))
		try: self.lCount.SetHorizontalAlignCenter(); self.lCount.SetVerticalAlignCenter()
		except: pass

		# --- combos LAST so their dropdowns overlay controls below (SubCategory, Category, Class bottom-to-top) ---
		self.cSub = self.comp.ComboBoxFunc(self.Board, TG_SUB[0][0], 10, 117, 120, self._onFilter)
		for i in range(len(TG_SUB)): self.cSub.InsertItem(i, TG_SUB[i][0])   # ALL subtypes at once (lax, not category-scoped)
		self.cCat = self.comp.ComboBoxFunc(self.Board, TG_CAT[0][0], 10, 97, 120, self._onFilter)
		for i in range(len(TG_CAT)): self.cCat.InsertItem(i, TG_CAT[i][0])
		self.cClass = self.comp.ComboBoxFunc(self.Board, TG_CLASS[0][0], 10, 57, 120, self._onFilter)
		for i in range(len(TG_CLASS)): self.cClass.InsertItem(i, TG_CLASS[i][0])

		self.selectedItem = None
		self._layoutVer = TG_LAYOUT_VER   # stamp so OpenGlass knows this window matches the current layout
		self.Board.Hide()

	def switch_state(self):
		if self.Board.IsShow():
			self.Board.Hide()
		else:
			# after a restart the in-memory list is empty -> auto-load this map's saved scan so results are ready
			try:
				if not self.owner.Items:
					self.owner.LoadScan()
			except: pass
			self.Board.Show()
			self.DoSearch()

	def DoSave(self):
		try: self.owner.SaveScan()
		except Exception as e:
			_dbg("[TradingGlass] save error: %s" % e)

	def _num(self, editline):
		try:
			t = (editline.GetText() or "").strip().replace(',', '')
			return long(t) if t else None
		except:
			return None

	def _onFilter(self):
		# a dropdown selection changed -> re-filter. Guard against firing before the grid exists.
		if getattr(self, 'rows', None) is None:
			return
		self.DoSearch()

	def _combo(self, combo):
		try: return combo.GetCurrentText()
		except: return ''

	def DoSearch(self):
		try: src = list(self.owner.Items)
		except: src = []
		# Name match: case/space-insensitive subsequence (see nameMatch) -> matches across words in the item name.
		name = (self.fName.GetText() or "").lower().replace(" ", "")
		# Price fields are in WON -> convert to Yang (1 Won = 100,000,000 Yang) for the total comparison below.
		pmin = self._num(self.fPMin); pmax = self._num(self.fPMax)
		if pmin is not None: pmin = min(pmin * 100000000, SHOP_MAX_YANG)
		if pmax is not None:
			# 3000 Won = the shop cap -> treat as unlimited (incl. the up-to-1,999,999,999 Yang remainder above 3000*1e8)
			pmax = SHOP_MAX_YANG if pmax >= 3000 else pmax * 100000000
		lmin = self._num(self.fLMin); lmax = self._num(self.fLMax)
		rmin = self._num(self.fRMin); rmax = self._num(self.fRMax)   # Item Lvl = refine (+N), parsed from name
		classbit = TG_CLASS_MAP.get(self._combo(self.cClass), None)   # 1/2/4/8/16 or None
		cattypes = TG_CAT_MAP.get(self._combo(self.cCat), None)       # tuple of EItemType or None
		sub = TG_SUB_MAP.get(self._combo(self.cSub), None)            # (type, subtype) or None -- independent of Category
		out = []
		for it in src:
			if name and not nameMatch(name, it.name):
				continue
			total = it.yang + it.won * 100000000
			if pmin is not None and total < pmin:
				continue
			if pmax is not None and total > pmax:
				continue
			if classbit:
				_base = getattr(it, 'cmask', 0) & 15
				if classbit == 16:   # Lycan: no anti-Lycan flag -> usable if shared (all classes) or class-exclusive
					if _base not in (0, 15):
						continue
				elif not (_base & classbit):
					continue
			if sub is not None:   # subtype implies its type -> most specific, takes precedence over category
				if getattr(it, 'itype', 0) != sub[0] or getattr(it, 'isub', 0) != sub[1]:
					continue
			elif cattypes is not None:
				if getattr(it, 'itype', 0) not in cattypes:
					continue
			lvl = getattr(it, 'level', 0)
			if lmin is not None and lvl < lmin:
				continue
			if lmax is not None and lvl > lmax:
				continue
			if rmin is not None or rmax is not None:
				rf = refineFromName(it.name)
				if rmin is not None and rf < rmin:
					continue
				if rmax is not None and rf > rmax:
					continue
			out.append(it)
		out.sort(key=lambda x: x.yang + x.won * 100000000)
		self.results = out
		self.page = 0
		self.Render()

	def _pages(self):
		n = len(self.results)
		return (n + TG_ROWS - 1) // TG_ROWS if n else 1

	def Render(self):
		self.selectedItem = None
		start = self.page * TG_ROWS
		page_items = self.results[start:start + TG_ROWS]
		for i in range(TG_ROWS):
			rb = self.rows[i]
			if i < len(page_items):
				rb.Setup(page_items[i], self._selectRow, self)
				rb.Show()
			else:
				rb.item = None
				rb.selected = False
				rb.Hide()
		self._hideItemTooltip()
		self.lPage.SetText("%d / %d" % (self.page + 1, self._pages()))
		self.lCount.SetText("%s Items" % fmtThousands(len(self.results)))

	def _showItemTooltip(self, it):
		# populate + show the ONE shared tooltip for the hovered row's item (standard inventory tooltip -> the
		# translucent window with green/red requirement coloring). Needs vnum (re-sweep to populate).
		tt = getattr(self, 'toolTip', None)
		if tt is None or not (it and getattr(it, 'vnum', 0)):
			if tt is not None:
				try: tt.Hide()
				except: pass
			return
		# AddItemData indexes metinSlot[0..METIN_MAX) + attrSlot[0..ATTR_MAX); the live client uses more slots
		# than the 3/7 we captured -> pad BOTH to safe lengths (client reads only what it needs; extra 0s are
		# skipped). metinSlot MUST be an indexable list, attrSlot a list of (type,value) tuples.
		# type-aware padding: gear (weapon/armor/costume/DS/ring/belt) iterates more socket/attr slots (needs
		# padding), but pet-boxes/pets regressed when over-padded -> pad heavily only for gear, keep others at 3/7.
		_heavy = getattr(it, 'itype', 0) in (1, 2, 28, 33, 34)   # DS (29/30) kept at 3/7 so its bonuses render
		_sn, _an = (8, 16) if _heavy else (3, 7)
		sockets = list(it.sockets or [])
		while len(sockets) < _sn: sockets.append(0)
		attrs = list(it.attrs or [])
		while len(attrs) < _an:   attrs.append((0, 0))
		try:
			tt.ClearToolTip()
			tt.AddItemData(int(it.vnum), sockets, attrs)
			# DS/alchemy stones: the default AddItemData renders grade/step but NOT the instance bonuses. The
			# client has a dedicated renderer __AppendDragonSoulAttributeInformation(attrSlot, dsType, grade) that
			# the live shop path uses. grade decodes from the vnum (server DragonSoul.cpp: (vnum/1000)%10; the
			# 100k digit-pair FEDCBA = FE type, D grade, C step, B strength). dsType = the DS subtype (proto slot).
			if getattr(it, 'itype', 0) in (29, 30):
				try:
					_v = int(it.vnum); _grade = (_v / 1000) % 10; _dsType = getattr(it, 'isub', 0)
					tt._ItemToolTip__AppendDragonSoulAttributeInformation(attrs, _dsType, _grade)
					# This newer ItemToolTip sizes width via _tooltip_data_width/_max_tooltip_width (NOT the old
					# toolTipWidth, which is absent -> the log showed ttw=0). Our manual DS append never updates those,
					# so long bonus names overflow. Measure the widest appended line, raise the width vars, and let the
					# client's own OptimizeTooltipWindowSize recompute+resize (falls back to ResizeToolTip).
					try:
						_mw = 0
						for _ch in getattr(tt, 'childrenList', []):
							try:    _w = _ch.GetTextSize()[0]
							except:
								try: _w = _ch.GetWidth()
								except: _w = 0
							if _w > _mw: _mw = _w
						_need = _mw + 24   # left+right padding
						for _a in ('_tooltip_data_width', '_max_tooltip_width', 'toolTipWidth'):
							try:
								if getattr(tt, _a, 0) < _need: setattr(tt, _a, _need)
							except: pass
						_dbg("[ds-width] max_child=%d need=%d tdw=%r mtw=%r" % (_mw, _need, getattr(tt, '_tooltip_data_width', 'NA'), getattr(tt, '_max_tooltip_width', 'NA')))
					except: pass
					try: tt.OptimizeTooltipWindowSize()
					except: tt.ResizeToolTip()
				except Exception as _d:
					_dbg("[ds-append] err: %s" % _d)
			tt.SetTop(); tt.Show()
		except Exception as _e:
			_dbg("[Glass] tip err vnum=%s: %s" % (getattr(it, 'vnum', '?'), _e))

	def _hideItemTooltip(self):
		tt = getattr(self, 'toolTip', None)
		if tt is not None:
			try: tt.Hide()
			except: pass

	def _selectRow(self, rb):
		for r in self.rows:
			r.selected = (r is rb)
		self.selectedItem = rb.item

	def _selected(self):
		return getattr(self, 'selectedItem', None)

	def Prev(self):
		if self.page > 0:
			self.page -= 1; self.Render()

	def Next(self):
		if self.page < self._pages() - 1:
			self.page += 1; self.Render()

	def FirstPage(self):
		if self.page != 0:
			self.page = 0; self.Render()

	def LastPage(self):
		lp = self._pages() - 1
		if self.page != lp:
			self.page = lp; self.Render()

	def Buy(self):
		it = self._selected()
		if it is not None:
			try: self.owner.BuyItemDirectly(it)
			except Exception as e:
				_dbg("[TradingGlass] buy error: %s" % e)

	def Go(self):
		it = self._selected()
		if it is None:
			return
		x, y = getattr(it, 'shop_x', 0), getattr(it, 'shop_y', 0)
		if abs(x) < 1.0 and abs(y) < 1.0:
			try: x, y, z = eXLib.GetPixelPosition(it.shop)
			except: pass
		if abs(x) < 1.0 and abs(y) < 1.0:
			chat.AppendChat(3, "[TradingGlass] shop position unknown - re-run the sweep.")
			return
		if Movement.GoToPositionAvoidingObjects(x, y) == Movement.NO_PATH_FOUND:
			chr.MoveToDestPosition(player.GetMainCharacterIndex(), x, y)

	def _rebuildWindow(self):
		wasShown = False
		try: wasShown = self.Board.IsShow()
		except: pass
		try: self.Board.Hide()
		except: pass
		for a in ('Board', 'comp', 'toolTip', 'listBg', '_border', '_frame', 'hdrImg', 'headers', 'bFirst', 'bPrev', 'bNext', 'bLast',
		          'lPage', 'rows', 'jobImg', 'jobLbl', 'typeImg', 'typeLbl', 'lvlImg', 'lvlLbl',
		          'refImg', 'refLbl', 'priceImg', 'priceLbl', 'nameImg', 'nameLbl', 'lvlTilde', 'refTilde',
		          'minLvlImg', 'fLMin', 'maxLvlImg', 'fLMax', 'minRefImg', 'fRMin', 'maxRefImg', 'fRMax',
		          'minPImg', 'fPMin', 'maxPImg', 'fPMax', 'nameSlotImg', 'fName',
		          'bSearch', 'bSave', 'bGo', 'lCount', 'cSub', 'cCat', 'cClass'):
			try: setattr(self, a, None)
			except: pass
		self.BuildWindow()
		if wasShown:
			self.Board.Show(); self.DoSearch()


def switch_state():
	if searchDialog.Board.IsShow():
		searchDialog.Board.Hide()
	else:
		# self-heal: rebuild the SearchBot window if it predates the current release layout (e.g. the old big
		# debug window) so the small window appears without a client restart / needing /rah-ui.
		if getattr(searchDialog, '_sbVer', 0) != SB_LAYOUT_VER:
			try: searchDialog._rebuildWindow()
			except: pass
		searchDialog.Board.Show()

# reload-safe (for /rah): on RELOAD keep the live singleton + its window/state, just rebind the class so
# it runs new logic (no duplicate window, no double RegisterNewShopCallback). First load builds + shows it.
# Also rebind the child TradingGlass window's class so /rah hot-reloads its logic too. /rah-ui rebuilds both
# windows in place (SearchDialog._rebuildWindow cascades to glass._rebuildWindow).
try:
	searchDialog
	searchDialog.__class__ = SearchDialog
	try: searchDialog.glass.__class__ = TradingGlass
	except: pass
except NameError:
	searchDialog = SearchDialog()
	searchDialog.Show()

# alias so init.py's generic /rah-ui rebuild loop (which looks up module.instance) finds this singleton
instance = searchDialog

