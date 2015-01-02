import os
import pygame
import time
import random
import socket
import fcntl
import struct
import fnmatch
from pygame.locals import *
os.environ["SDL_FBDEV"] = "/dev/fb1"
if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'
global ethdisp


class Icon:

    def __init__(self, name):
      self.name = name
      try:
        self.bitmap = pygame.image.load(iconPath + '/' + name + '.png')
      except:
        pass

class Button:

    def __init__(self, rect, **kwargs):
        self.rect     = rect # Bounds
        self.color    = None # Background fill color, if any
        self.iconBg   = None # Background Icon (atop color fill)
        self.iconFg   = None # Foreground Icon (atop background)
        self.bg       = None # Background Icon name
        self.fg       = None # Foreground Icon name
        self.callback = None # Callback function
        self.value    = None # Value passed to callback
        for key, value in kwargs.iteritems():
            if   key == 'color': self.color    = value
            elif key == 'bg'   : self.bg       = value
            elif key == 'fg'   : self.fg       = value
            elif key == 'cb'   : self.callback = value
            elif key == 'value': self.value    = value

    def selected(self, pos):
        x1 = self.rect[0]
        y1 = self.rect[1]
        x2 = x1 + self.rect[2] - 1
        y2 = y1 + self.rect[3] - 1
        if ((pos[0] >= x1) and (pos[0] <= x2) and
            (pos[1] >= y1) and (pos[1] <= y2)):
            if self.callback:
                if self.value is None: self.callback()
                else:                  self.callback(self.value)
            return True
        return False

    def draw(self, screen):
        if self.color:
            screen.fill(self.color, self.rect)
        if self.iconBg:
            screen.blit(self.iconBg.bitmap,
              (self.rect[0]+(self.rect[2]-self.iconBg.bitmap.get_width())/2,
               self.rect[1]+(self.rect[3]-self.iconBg.bitmap.get_height())/2))
        if self.iconFg:
            screen.blit(self.iconFg.bitmap,
              (self.rect[0]+(self.rect[2]-self.iconFg.bitmap.get_width())/2,
               self.rect[1]+(self.rect[3]-self.iconFg.bitmap.get_height())/2))

    def setBg(self, name):
        if name is None:
            self.iconBg = None
        else:
            for i in icons:
                if name == i.name:
                    self.iconBg = i
                break

# Global stuff -------------------------------------------------------------

screenMode      =  3      # Current screen mode; default = viewfinder
iconPath        = 'icons' # Subdirectory containing UI bitmaps (PNG format)

icons = [] # This list gets populated at startup

buttons = [
    # Screen mode 0 is photo playback
  [Button((  0,188,320, 52), bg='done'),# , cb=doneCallback),
   Button((  0,  0, 80, 52), bg='prev'),# , cb=imageCallback, value=-1),
   Button((240,  0, 80, 52), bg='next'),# , cb=imageCallback, value= 1),
   Button(( 88, 70,157,102)), # 'Working' label (when enabled)
   Button((148,129, 22, 22)), # Spinner (when enabled)
   Button((121,  0, 78, 52), bg='trash',)],# cb=imageCallback, value= 0)],

  # Screen mode 1 is delete confirmation
  [Button((  0,35,320, 33), bg='delete'),
   Button(( 32,86,120,100), bg='yn', fg='yes'),
    #cb=deleteCallback, value=True),
   Button((168,86,120,100), bg='yn', fg='no')],
    #cb=deleteCallback, value=False)],

  # Screen mode 2 is 'No Images'
  [Button((0,  0,320,240)), #cb=doneCallback), # Full screen = button
   Button((0,188,320, 52), bg='done'),       # Fake 'Done' button
   Button((0, 53,320, 80), bg='empty')],     # 'Empty' message
# Screen mode 3 is viewfinder / snapshot
  [Button((  0,188,156, 52), bg='gear',),# cb=viewCallback, value=0),
   Button((164,188,156, 52), bg='play',),# cb=viewCallback, value=1),
   Button((  0,  0,320,240)           ,),# cb=viewCallback, value=2),
   Button(( 88, 51,157,102)),  # 'Working' label (when enabled)
   Button((148, 110,22, 22))], # Spinner (when enabled)
]
ifname=0

class IPdisplay:
    def get_ip_address(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])
        font            = pygame.font.Font(None, 30)
        try:
            eth = get_ip_address('eth0')
        except IOError:
            eth = ('0.0.0.0')
        try:
            wl = get_ip_address('wlan0')
        except IOError: 
            wl = ("0.0.0.0")
        if eth == ("0.0.0.0"):
            ethdisp = font.render(ethip, 1, (255,0,0))
        else:
            ethdisp = font.render(ethip, 1, (0, 255, 0))
        screen.blit( ethdisp, (0,0) )
        ethrect = ethdisp.get_rect()
        if wl == ("0.0.0.0"):
            wldisp = font.render(wlip, 1, (255, 0, 0))
        else:
            wldisp = font.render(wlip, 1, (0, 255, 0))
        screen.blit(wldisp, (0,1*font.get_linesize()) )
        wlrect = wldisp.get_rect()

        #pygame.init()
        #size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        #screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        #pygame.mouse.set_visible(0)

        #black = (0, 0, 0)
        #screen.fill(black)
        #screen.blit(ethdisp,(0,0))
        #screen.blit(wldisp, (0,1*font.get_linesize()) )
        #pygame.display.flip()



os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV'      , '/dev/fb1')
os.putenv('SDL_MOUSEDRV'   , 'TSLIB')
os.putenv('SDL_MOUSEDEV'   , '/dev/input/touchscreen')

pygame.init()
#scope = IPdisplay()
#scope.getips()
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)

# Load all icons at startup.
for file in os.listdir(iconPath):
  if fnmatch.fnmatch(file, '*.png'):
    icons.append(Icon(file.split('.')[0]))

# Assign Icons to Buttons, now that they're loaded
for s in buttons:        # For each screenful of buttons...
  for b in s:            #  For each button on screen...
    for i in icons:      #   For each icon...
      if b.bg == i.name: #    Compare names; match?
        b.iconBg = i     #     Assign Icon to Button
        b.bg     = None  #     Name no longer used; allow garbage collection
      if b.fg == i.name:
        b.iconFg = i
        b.fg     = None





while (True): # your main loop
  # get all events
  ev = pygame.event.get()
  screen.blit(ethdisp,(0,0))
  screen.blit(wldisp, (0,1*font.get_linesize()) )

  # proceed events
  for event in ev:

    # handle MOUSEBUTTONUP
    if event.type == pygame.MOUSEBUTTONUP:
        pos = pygame.mouse.get_pos()
        key = pygame.mouse.get_pressed()
#        print pos
#        print key
        scope = IPdisplay()
        scope.__init__()
    if event.type == pygame.KEYUP:
            if event.key == K_ESCAPE:
                print "Escape Pressed"
                pygame.quit()
            else:
                print (event.key)
                print "you go nowhere, looping"

    for i,b in enumerate(buttons[screenMode]):
        b.draw(screen)
    pygame.display.update()
