
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


import eXLib
import OpenLib,FileManager,UIComponents

class BuffDialog(ui.ScriptWindow):

	Cooltime = 0
	sk1 = 0
	sk2 = 0
	sk3 = 0
	
	def __init__(self):
		self.Board = ui.ThinBoard()
		self.Board.SetSize(200, 225)
		self.Board.SetPosition(52, 40)
		self.Board.AddFlag('movable')
		self.Board.Hide()
		
		self.comp = UIComponents.Component()
		self.Header = self.comp.TextLine(self.Board, 'Buffbot', 83, 7, self.comp.RGB(255, 255, 0))
		self.TargetNameLabel = self.comp.TextLine(self.Board, 'Target Name:', 20, 32, self.comp.RGB(255, 255, 255))
		self.Name = self.comp.TextLine(self.Board, '', 100, 32, self.comp.RGB(255, 255, 255))
		self.FollowLabel = self.comp.TextLine(self.Board, 'Follow Target', 69, 110, self.comp.RGB(255, 255, 255))
		self.DelayLabel = self.comp.TextLine(self.Board, 'Delay: 20 Sec.', 73, 155, self.comp.RGB(255, 255, 255))
		
		self.SegenImage = self.comp.ExpandedImage(self.Board, 85, 65, str("d:/ymir work/ui/skill/shaman/gicheon_02.sub"))
		self.HDDImage = self.comp.ExpandedImage(self.Board, 40, 65, str("d:/ymir work/ui/skill/shaman/hosin_02.sub"))
		self.ReflektImage = self.comp.ExpandedImage(self.Board, 130, 65, str("d:/ymir work/ui/skill/shaman/boho_02.sub"))
		self.Close = self.comp.Button(self.Board, '', 'Close', 177, 7, self.Hide_UI, 'd:/ymir work/ui/public/close_button_01.sub', 'd:/ymir work/ui/public/close_button_02.sub', 'd:/ymir work/ui/public/close_button_03.sub')
		self.DelaySlide = self.comp.SliderBar(self.Board, 0.2, self.SlideFunc, 13, 140)
		self.BuffOff = self.comp.HideButton(self.Board, '', '', 84, 180, self.SetBuffStatus, eXLib.PATH + 'OpenBot/Images/start_0.tga', eXLib.PATH + 'OpenBot/Images/start_1.tga', eXLib.PATH + 'OpenBot/Images/start_2.tga')
		self.BuffOn = self.comp.HideButton(self.Board, '', '', 84, 180, self.SetBuffStatus, eXLib.PATH + 'OpenBot/Images/stop_0.tga', eXLib.PATH + 'OpenBot/Images/stop_1.tga', eXLib.PATH + 'OpenBot/Images/stop_2.tga')
		self.SegenOn = self.comp.HideButton(self.Board, '', '', 55, 80, self.BuffSegen, eXLib.PATH + 'OpenBot/Images/on_0.tga', eXLib.PATH + 'OpenBot/Images/on_1.tga', 'OpenBot/mages/on_2.tga')
		self.SegenOff = self.comp.HideButton(self.Board, '', '', 55, 80, self.BuffSegen, eXLib.PATH + 'OpenBot/Images/off_0.tga', eXLib.PATH + 'OpenBot/Images/off_1.tga', eXLib.PATH + 'OpenBot/Images/off_2.tga')
		self.HDDOn = self.comp.HideButton(self.Board, '', '', 100, 80, self.BuffHDD, eXLib.PATH + 'OpenBot/Images/on_0.tga', eXLib.PATH + 'OpenBot/Images/on_1.tga', 'OpenBot/mages/on_2.tga')
		self.HDDOff = self.comp.HideButton(self.Board, '', '', 100, 80, self.BuffHDD, eXLib.PATH + 'OpenBot/Images/off_0.tga', eXLib.PATH + 'OpenBot/Images/off_1.tga', eXLib.PATH + 'OpenBot/Images/off_2.tga')
		self.ReflektOn = self.comp.HideButton(self.Board, '', '', 147, 80, self.BuffReflekt, eXLib.PATH + 'OpenBot/Images/on_0.tga', eXLib.PATH + 'OpenBot/Images/on_1.tga', 'OpenBot/mages/on_2.tga')
		self.ReflektOff = self.comp.HideButton(self.Board, '', '', 147, 80, self.BuffReflekt, eXLib.PATH + 'OpenBot/Images/off_0.tga', eXLib.PATH + 'OpenBot/Images/off_1.tga', eXLib.PATH + 'OpenBot/Images/off_2.tga')
		self.FollowOn = self.comp.HideButton(self.Board, '', '', 135, 110, self.SetFollow, eXLib.PATH + 'OpenBot/Images/on_0.tga', eXLib.PATH + 'OpenBot/Images/on_1.tga', 'OpenBot/mages/on_2.tga')
		self.FollowOff = self.comp.HideButton(self.Board, '', '', 135, 110, self.SetFollow, eXLib.PATH + 'OpenBot/Images/off_0.tga', eXLib.PATH + 'OpenBot/Images/off_1.tga', eXLib.PATH + 'OpenBot/Images/off_2.tga')
		
		self.BuffStatus = int(FileManager.ReadConfig("BuffStatus"))
		self.BuffDelay = int(FileManager.ReadConfig("BuffDelay"))
		self.Segen = int(FileManager.ReadConfig("Segen"))
		self.Reflekt = int(FileManager.ReadConfig("Reflekt"))
		self.HDD = int(FileManager.ReadConfig("HDD"))
		self.Follow = int(FileManager.ReadConfig("Follow"))
		self.TargetVID = int(FileManager.ReadConfig("TargetVID"))
		
		if self.BuffStatus:
			self.BuffOn.Show()
		else:
			self.BuffOff.Show()
		if self.Segen:
			self.SegenOn.Show()
		else:
			self.SegenOff.Show()
		if self.HDD:
			self.HDDOn.Show()
		else:
			self.HDDOff.Show()
		if self.Reflekt:
			self.ReflektOn.Show()
		else:
			self.ReflektOff.Show()
		if self.Follow:
			self.FollowOn.Show()
		else:
			self.FollowOff.Show()
			
		if self.TargetVID != 0:
			self.Name.SetText(chr.GetNameByVID(self.TargetVID))
		else:
			self.Name.SetText("None")
		
		self.DelaySlide.SetSliderPos(float(self.BuffDelay*0.01))
		self.SlideFunc()
		self.Update()
		
	def switch_state(self):
		if self.Board.IsShow():
			self.Hide_UI()
		else:
			self.Board.Show()
	def Hide_UI(self):
		self.Board.Hide()
		FileManager.WriteConfig("BuffStatus", str(self.BuffStatus))
		FileManager.WriteConfig("BuffDelay", str(self.BuffDelay))
		FileManager.WriteConfig("Segen", str(self.Segen))
		FileManager.WriteConfig("Reflekt", str(self.Reflekt))
		FileManager.WriteConfig("HDD", str(self.HDD))
		FileManager.WriteConfig("Follow", str(self.Follow))
		FileManager.WriteConfig("TargetVID", str(self.TargetVID))
		FileManager.Save()
		
		
	def SetBuffStatus(self):
		if self.Segen == 1 or self.HDD == 1 or self.Reflekt == 1:
			if self.BuffStatus:
				self.BuffStatus = 0
				self.BuffOff.Show()	
				self.BuffOn.Hide()	
			else:	
				self.BuffStatus = 1
				self.Cooltime = -1
				self.BuffOff.Hide()	
				self.BuffOn.Show()
		else:
			chat.AppendChat(7, "Turn on a Buffskill or select a target first!")
		
	def BuffSegen(self):
		if self.BuffStatus == 0:
			if self.Segen:
				self.Segen = 0	
				self.SegenOn.Hide()
				self.SegenOff.Show()
			else:	
				self.Segen = 1
				self.SegenOn.Show()
				self.SegenOff.Hide()
		else:
			chat.AppendChat(7, "Stop the Bot to add a skill!")
	
	def BuffHDD(self):
		if self.BuffStatus != 1:
			if self.HDD:
				self.HDD = 0	
				self.HDDOn.Hide()
				self.HDDOff.Show()
			else:	
				self.HDD = 1
				self.HDDOn.Show()
				self.HDDOff.Hide()
		else:
			chat.AppendChat(7, "Stop the Bot to add a skill!")

	def BuffReflekt(self):
		if self.BuffStatus != 1:
			if self.Reflekt:
				self.Reflekt = 0	
				self.ReflektOn.Hide()
				self.ReflektOff.Show()
			else:	
				self.Reflekt = 1
				self.ReflektOn.Show()
				self.ReflektOff.Hide()
		else:
			chat.AppendChat(7, "Stop the Bot to add a skill!")	
	
	def SetFollow(self):
		if self.Follow:
			self.Follow = 0	
			self.FollowOn.Hide()
			self.FollowOff.Show()
			self.FollowTarget_0()
		else:	
			self.Follow = 1
			self.FollowOn.Show()
			self.FollowOff.Hide()
			self.FollowTarget_1()
			
	def SlideFunc(self):
		self.BuffDelay = int((self.DelaySlide.GetSliderPos()*100)+0.001)
		self.DelayLabel.SetText("Delay: "+str(self.BuffDelay)+ " Sec.")	
		

	def Update(self):
		if self.BuffStatus:
			player.SetTarget(int(self.TargetVID))
			if self.Cooltime == 0:
				self.Cooltime = time.clock()
			else:
				Time = time.clock()
				if self.Cooltime == -1:
					TimeToWait = 0
				else:
					TimeToWait = self.Cooltime + self.BuffDelay
				if TimeToWait < Time:
					if self.Segen:
						if player.IsSkillCoolTime(4) == 0:
							player.ClickSkillSlot(4)
						else:
							self.sk1 = 1
					if self.Reflekt:
						if player.IsSkillCoolTime(5) == 0:
							player.ClickSkillSlot(5)
						else:
							self.sk2 = 1
					if self.HDD:
						if player.IsSkillCoolTime(6) == 0:
							player.ClickSkillSlot(6)
						else:
							self.sk3 = 1
					if self.Segen != 1:
						self.sk1 = 1
					if self.Reflekt != 1:
						self.sk2=1
					if self.HDD != 1:
						self.sk3 = 1
					if self.sk1 == 1 and self.sk2 == 1 and self.sk3 == 1:
						self.Cooltime = 0
						self.sk1 = 0
						self.sk2 = 0
						self.sk3 = 0
		else:
			self.TargetVID = player.GetTargetVID()
			self.Name.SetText(chr.GetNameByVID(self.TargetVID))
		self.UpdateBuff = OpenLib.WaitingDialog()
		self.UpdateBuff.Open(0.5)
		self.UpdateBuff.SAFE_SetTimeOverEvent(self.Update)			

	def FollowTarget_1(self):
		x,y = eXLib.GetPixelPosition(TargetVid)[:2]
		chr.MoveToDestPosition(player.GetMainCharacterIndex(),int(x),int(y))
		
		self.UpdateFollow = OpenLib.WaitingDialog()
		self.UpdateFollow.Open(1.0)
		self.UpdateFollow.SAFE_SetTimeOverEvent(self.FollowTarget_1)
		
	def FollowTarget_0(self):
		self.UpdateFollow = OpenLib.WaitingDialog()
		self.UpdateFollow.Close()
		
		
	