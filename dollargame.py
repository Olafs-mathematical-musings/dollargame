"""
The Dollar Game as presented by numberphile (https://www.youtube.com/watch?v=U33dsEcKgeQ)
put into the public domain by Olaf Doschke (olaf@doschke.name - http://www.doschke.name)

You need Python 3 and pygame to run this (tested with python 3.6.5 and pygame 1.9.4)
"""

import sys, os, pickle, operator, math
import pygame as pg
from pygame.locals import *
from random import random

#some global constants
BACKGROUND = "brownpaper.jpg"
SCREENSIZE = (1200,900)
CIRCLESIZE = 50
TITLEFONTSIZE = CIRCLESIZE<<1

BLACK = (0,0,0,255)
DOLLARGREEN = (133,187,101,255)
DOLLARYELLOW = (232,224,201,255)
GRAPHCOLOR = (16,64,128,255)
ADDCOLOR = (16,192,128,255)
REMOVECOLOR = (255,0,0,255)
HIGHLIGHTCOLOR = (255,255,255,255)
TRANSPARENTCOLOR = (255,255,255,0)
TITLEFONT = "Arial Black"
TEXTFONT = "Arial"
NODEFONT = "Kalam.ttf"

# textgradient draws text in colors with black border
def textgradient(text, font, size, colors, bordersize):
   # starting simple, just render the text BLACK
   myfont = pg.font.SysFont(font, size)
   textsize = myfont.render(text, False, BLACK)
   # but only to determine its size.
   (tw,th) = textsize.get_size()

   # Now for the real deal
   textsurface = pg.Surface((int(4+tw), int(4+th)), pg.SRCALPHA)
   textindex = 0
   textxoffset=0
   # render each letter
   for c in text:
      letter = myfont.render(c, True, BLACK)
      (lw,lh) = letter.get_size()
      lettersurface = pg.Surface((int(6+lw), int(6+lh)), pg.SRCALPHA)
 
      # draw text in all positions from (0,0) to (2*bordersize,2*bordersize) for the additional border
      # the core letters in colors given by the colors list parameter are put on top of this
      for xoffset in range(2*bordersize+1):
         for yoffset in range(2*bordersize+1): 
            lettersurface.blit(letter,(xoffset,yoffset))

      # color the letter according to the gradient given in the colors list
      # equally spread form 0% to 100%
      textpercentage = textindex/(len(text)-1) # 0-1 (0%-100%)
      colorindex = int(textpercentage*(len(colors)-1)) # will at maximum be the highest colorindex len(colors)-1
      colorpercentagelo = colorindex/(len(colors)-1)
      colorpercentagehi = (colorindex+1)/(len(colors)-1)
      localcolorpercentage = (textpercentage-colorpercentagelo)/(colorpercentagehi-colorpercentagelo)
      col1 = colors[colorindex]
      try:
         col2 = colors[colorindex+1]
      except:
         # colorindex+1 might be len(colors), one too high
         # in this case the second color becomes the first, the last letter at 100% will get the last color anyway
         col2 = col1

      # interpolate color   
      color = (col2[0]*localcolorpercentage+col1[0]*(1-localcolorpercentage),
               col2[1]*localcolorpercentage+col1[1]*(1-localcolorpercentage),
               col2[2]*localcolorpercentage+col1[2]*(1-localcolorpercentage))

      # here's the letter "put on top of that"
      letter = myfont.render(c, True, color)
      lettersurface.blit(letter,(bordersize,bordersize))
      textsurface.blit(lettersurface,(textxoffset,0))
      textxoffset+=letter.get_width()
      textindex+=1

   return textsurface

# Simple state base object,
# only keeps track of which sate is next and when this state is done
# see Controller event_loop and States subclasses event handling to see how this is supposed to work
class States(object):
    def __init__(self):
        self.done = False
        self.next = None

# Game title screen
class Title(States):
    def __init__(self):
        States.__init__(self)
        self.name='title'
        self.next='editor'
    def startup(self, model):

        # Title screen
        text = textgradient('The Dollar Game', TITLEFONT, TITLEFONTSIZE, [DOLLARGREEN, DOLLARYELLOW, DOLLARGREEN],2)
        (tw,th) = text.get_size()
        (sw,sh) = model.fg.get_size()
        model.fg.blit(text,((sw-tw)/2,(sh-3*th)/2))
        
        yoffset=(sh-th)/2+10
        textfont = pg.font.SysFont(TEXTFONT, int(TITLEFONTSIZE/3))
        text = textfont.render('As seen on numberphile', True, BLACK)
        (tw,th) = text.get_size()
        model.fg.blit(text,((sw-tw)/2,yoffset))

        # displays minimal instructions
        yoffset=yoffset+th+10
        text = textfont.render('Click anywhere to start the editor.', True, BLACK)
        (tw,th) = text.get_size()
        model.fg.blit(text,((sw-tw)/2,yoffset))

        yoffset=yoffset+th+10
        text = textfont.render('Press R to create a random graph.', True, BLACK)
        (tw,th) = text.get_size()
        model.fg.blit(text,((sw-tw)/2,yoffset))

        yoffset=yoffset+th+10
        text = textfont.render('Press any other key to start the game.', True, BLACK)
        (tw,th) = text.get_size()
        model.fg.blit(text,((sw-tw)/2,yoffset))

        model.draw = True        

    def cleanup(self, model):
        model.fg.fill((0,0,0,0))

    def doevent(self, event, model):

        # keyboard
        if event.type == pg.KEYDOWN:
           key = pg.key.get_pressed()
           if key[ord('r')] or key[ord('R')]:
              # R for random game
              model.random = True
           self.done = True

        # and mouse   
        elif event.type == pg.MOUSEBUTTONDOWN:
           self.next = 'editor'
           self.done = True

class Editor(States):
    def __init__(self):
        States.__init__(self)
        self.name='editor'       
        self.next = 'game'
        self.mousemotion = False
    def startup(self, model):
        model.reset()
        # trigger a draw as if a mouse move event occurred
        self.mousemotion = True

       # no game loaded
        if model.random:
           if model.random:
              model.nodes={}
              model.nodeidcounter=0
              model.edges=set()

           nodes = int(random()*12)+4
           (sw,sh) = model.fg.get_size()
           angle = 0 # arrange nodes in circle starting at angle 0
           for n in range(nodes):
               x = int(math.cos(angle)*sw/3+sw/2)
               y = int(math.sin(angle)*sh/3+sh/2)
               angle += 2*math.pi/nodes
               model.nodes[model.nodeidcounter]=[(x,y),0]
               model.nodeidcounter+=1
               if n>0:
                  model.edges.add((n-1,n))
           for n in range(nodes>>1):
               n1 = int(random()*nodes)
               n2 = int(random()*nodes)
               if n1!=n2:
                  model.edges.add((n1,n2))
           genus = len(model.edges)-nodes+1
           dollars = 0
           for node in model.nodes.values():
               amount = int(random()*7)-3
               node[1] = amount
               dollars += node[1]
           model.nodes[0][1] += genus - dollars
           
    def cleanup(self, model):
        model.fg.fill((0,0,0,0))
    def doevent(self, event, model):

        # process keyboard events
        if event.type == pg.KEYDOWN:
           key = pg.key.get_pressed()
           if key[ord('s')] or key[ord('S')]:
              # S for saving this game
              # simple binary aving of the model.nodes dict and model.edges set plus node counter (next node index)
              with open('dollargame.sav','wb') as savegame:
                   pickle.dump(model.nodes, savegame)
                   pickle.dump(model.edges, savegame)
                   pickle.dump(model.nodeidcounter, savegame)
           else:
              # Any other key. swtich to game state
              self.done = True

        # process several mouse events
        elif event.type == pg.MOUSEMOTION or self.mousemotion:
           self.mousemotion = False
           model.draw = True

           # Determine several possible things:
           # 1. A nearest node (means hovered node, actually, if the mouse is within the node circle).
           #    Also, this is potentially the node to drag
           # 2. Dragging the hovered node (determined in step 1)
           # 3. A Narest edge, existing or potential edge. Which case it is will be determined when
           #    drawing the model foreground (fg) surface), because iterating all edges it's easy to see.
           # 4. Possible new node position (then draw node in ADDCOLOR at mouse position)

           model.reset() # resets some settings of the model to determine all these things

           # Some essential information to know mouse state
           (MouseX, MouseY) = pg.mouse.get_pos()
           (leftbutton, middlebutton, rightbutton) = pg.mouse.get_pressed()
           # Mouse motion can happen while a button is pressed,
           # and it might differ from the last mousebutondown event.

           # 1. Dtermine a nearest node
           mindistance = CIRCLESIZE**2
           for i in range(model.nodeidcounter):
               try:
                  # not all indexes might have nodes (as editing can also delete nodes)
                  # therefore just try accessing model.nodes[i]
                  (node, nodevalue) = model.nodes[i]
               except:
                  continue # no node with such an index: continue the loop
               distance = (MouseX-node[0])**2+(MouseY-node[1])**2 # actually square distance,
               
               # but mindistance also is CIRCLESIZE squared (x**2 means pow(x,2) or x^2 in other programming languages).
               if mindistance>distance:
                  mindistance=distance
                  model.nearestnodeindex = i

           # 2. With leftbutton pressed, drag and drop of the nearest node:
           if leftbutton:
              if model.dragnodeindex<0 and model.nearestnodeindex>=0:
                 # drag start
                 model.dragnodeindex = model.nearestnodeindex
              if model.dragnodeindex>=0:
                 # drag - let the node position follow the mouse position.
                 model.nodes[model.dragnodeindex][0] = (MouseX, MouseY)
                 # fast mouse moves meanwhile might have overridden nearestnodeindex! Therefore:
                 model.nearestnodeindex = model.dragnodeindex
                 # dragging means no change of the node dollar amount value:
                 model.addamount = 0 # reset to 0 from MOUSEBUTTONDOWN event before MOUSEBUTTONUP event

           # 3. Determine a nearest edge      
           if model.nearestnodeindex<0:
              # if the mousepointer is in a node, that node has the focus.
              # Therefore only determine nearest edge, if no node has focus
              
              mindistance = CIRCLESIZE/2
              model.nearestedgedistance = mindistance
              # iterate all possible edges between nodes, no matter whether they exist or not.
              # An existing edge will be drawn with REMOVECOLOR to signal it is removable with a click.
              # A non-existing edge will be drawn with ADDECOLOR to signal it as created with a click.
              
              for node1index in range(model.nodeidcounter):
                 for node2index in range(node1index+1,model.nodeidcounter):
                     # compute possible edge line from point EdgeA to point EdgeB
                     try:
                        # not all indexes might have nodes (as editing can also delete nodes)
                        # therefore just try accessing model.nodes[]
                        node1 = model.nodes[node1index][0]
                        node2 = model.nodes[node2index][0]
                        EdgeA, EdgeB = Vec2d(node1), Vec2d(node2)
                     except:
                        # one node doesn't exit, so that's not an edge to care about
                        continue

                     MousePosition = Vec2d(MouseX, MouseY)
                     # vector along edge from point A pointing to paoint B
                     EdgeVector = (EdgeB - EdgeA)
                     # Mousevector realtive to same origin point A
                     RelativeMousePosition = MousePosition-EdgeA
                     # dot products gives projected length (famously 0 for perdicular vectors)
                     EdgePosition = RelativeMousePosition.dot(EdgeVector)/(EdgeVector.get_length()**2)
                     # that should be between 0 and 1
                     if EdgePosition>=0 and EdgePosition <=1:
                        ProjectedEdgePostiion =  EdgeA + EdgePosition * EdgeVector # That's a point on the edge line
                        distance = (MousePosition - ProjectedEdgePostiion).get_length()
                     else:
                        # we need some value to compare mindistance with
                        #setting distance to mindistance means no change of the nearest edge found
                        distance = mindistance
                       
                     if mindistance>distance:
                        # new nearest edge found:
                        mindistance=distance
                        model.nearestedge = (node1index,node2index)
                        
           model.nearestedgedistance = mindistance             
           # 4. new node position
           if model.nearestnodeindex<0 and model.nearestedge is None:
              # making this a condition also means nodes cannot overlap
              # but they might be dragged anwhere later
              model.newnode = (MouseX, MouseY)
                
        elif event.type == pg.MOUSEBUTTONDOWN:

           # mouseclick can potentially start a new drag operation
           model.dragnodeindex = -1
           (leftbutton, middlebutton, rightbutton) = pg.mouse.get_pressed()

           # if a nearestnode is known from üprevious mousemotion events
           if  model.nearestnodeindex>=0:
              # then set addamount
              # these will be added to the neareastnode
              # at mousebutton up,
              # if the adamount isn't reset at mouse motions (drag)
              if leftbutton:
                 model.addamount = -1
              if rightbutton:
                 model.addamount = 1

           # mouseclick off any near edge or node means adding anew node:
           if model.nearestedge is None and model.nearestnodeindex<0 and leftbutton:
              (MouseX,MouseY) = pg.mouse.get_pos()
              model.nodes[model.nodeidcounter]=[(MouseX,MouseY),0]
              model.nearestnodeindex = model.nodeidcounter
              model.nodeidcounter+=1
              model.draw = True # there's something new to draw

              # also add an edg, so the new nodeis connected to the graph
              # connect to the latest nondeleted node:
              model.nearestedge = None
              for i in range(model.nodeidcounter):
                  try:
                     # not every index exists, so firsttest, whether the node dictionary
                     # has an entry at someindex. 
                     testnodeexists = model.nodes[model.nodeidcounter-2-i] # causes exception, if the index does not exist.
                     testnodeexists = model.nodes[model.nodeidcounter-1] # causes exception, if the index does not exist.
                     model.edges.add((model.nodeidcounter-2-i,model.nodeidcounter-1))
                     break
                  except:
                     pass
                  
           # if there is a nearest edge known (see mousmotion event),
           # a click either means
           # removing an existing edge
           # or adding a non existing edge.
           # One of the actions will be possible:
           if not model.nearestedge is None:
              try:
                 model.edges.remove(model.nearestedge)
              except:
                 # removing failes, so we can add it instead
                 model.edges.add(model.nearestedge)

              # in case this is the last edge for a specific node remove it
              # this isn't throughlychecking all nodes
              # standalone nodes arepossible
              try:
                 del model.nodes[model.removenodeindex]
                 model.removenodeindex = -1
              except:
                 pass

              # Something has changes, so draw that...
              model.draw = True
              model.nearestedge = None
              # ...in the same manner as if a mouse move event occurred
              self.mousemotion = True

        elif event.type == pg.MOUSEBUTTONUP:
           # drag operation ends here:
           model.dragnodeindex = -1
           try:
              # potentially the nearestnode might also be deleted, therefore just try
              if model.nearestnodeindex>=0:
                 model.nodes[model.nearestnodeindex][1] += model.addamount
                 model.draw= True
              # if that succeeds the amount should eb reset to 0
              model.addamount = 0
           except:
              pass


class Game(States):
    def __init__(self):
        States.__init__(self)
        self.name = 'game'       
        self.next = 'title'
    def startup(self, model):
        model.reset()

        # draw the screen...
        model.draw = True
        #...in the same manner as if a mouse move event occurred
        self.mousemotion = True
                      
    def cleanup(self, model):
        model.fg.fill((0,0,0,0))
        model.solved = False
        model.random = False
        
    def doevent(self, event, model):
        if event.type == pg.KEYDOWN:
           self.done = True
        elif event.type == pg.MOUSEBUTTONDOWN:
           if model.solved:
              self.done = True
              return
          
           (leftbutton, middlebutton, rightbutton) = pg.mouse.get_pressed()
           if  model.nearestnodeindex>=0:
              if leftbutton:
                 model.addamount = -1
              if rightbutton:
                 model.addamount = 1
           
        elif event.type == pg.MOUSEMOTION or self.mousemotion:
           self.mousemotion = False

           # determine nearest node (means hovered node, actually, if the mouse is within the node circle).
           oldnearestnodeindex = model.nearestnodeindex
           model.reset()
           (MouseX, MouseY) = pg.mouse.get_pos()

           mindistance = CIRCLESIZE**2
           for i in range(model.nodeidcounter):
               try:
                  # not all indexes might have nodes (as editing can also delete nodes)
                  # therefore just try accessing model.nodes[]
                  (node, nodevalue) = model.nodes[i]
               except:
                  continue
               distance = (MouseX-node[0])**2+(MouseY-node[1])**2
               if mindistance>distance:
                  mindistance=distance
                  model.nearestnodeindex = i
                  if model.nearestnodeindex != oldnearestnodeindex:
                     model.addamount = 0
                  model.draw = True

        elif event.type == pg.MOUSEBUTTONUP:
           if model.nearestnodeindex>=0:
              # along each node give or take model.addamount
              for edge in model.edges:
                  othernodeindex = -1
                  if edge[0] == model.nearestnodeindex:
                     othernodeindex = edge[1]
                  if edge[1] == model.nearestnodeindex:
                     othernodeindex = edge[0]
                  if othernodeindex>=0:  
                     model.nodes[model.nearestnodeindex][1] += model.addamount
                     model.nodes[othernodeindex][1] -= model.addamount
                     model.draw = True
           model.addamount = 0
            
class Model:
    def __init__(self):
        self.bg = pg.image.load(BACKGROUND)        
        self.fg = pg.Surface(SCREENSIZE, pg.SRCALPHA)
        self.draw = False
        self.nodes = {}
        self.nodeidcounter=0
        self.edges=set()
        self.removenode = None
        self.dragnodeindex = -1
        self.removenodeindex = -1
        self.addamount = 0
        self.solved = False
        self.random = False
        self.reset()
        
    def reset(self):
        self.nearestnodeindex = -1
        self.nearestedge = None
        self.nearestedgedistance = -1
        self.newnode = None

class View:
    def __init__(self):
        self.screen = pg.display.set_mode(SCREENSIZE)
    def update(self, model, state):
        if model.draw:
           (sw,sh) = model.fg.get_size()

           textfont = pg.font.SysFont(TEXTFONT, int(TITLEFONTSIZE/3))

           if state=='game':
              model.fg.fill((0,0,0,0))

              # check, if all nodes are positive!
              for node in model.nodes.values():
                  if node[1] < 0:
                    break
              else:
                  model.solved = True
                  model.reset()

           
              if model.solved:
                 text = textfont.render('You solved! Press any key or click to continue.', True, BLACK)
              else:
                 text = textfont.render('Press any key to give up.', True, BLACK)
              (tw,th) = text.get_size()
              
              model.fg.blit(text,((sw-tw)/2,20))
           
              for edge in model.edges:
                  node1 = model.nodes[edge[0]]
                  node2 = model.nodes[edge[1]]
                  color = GRAPHCOLOR
               
                  othernodeindex = -1
                  if edge[0] == model.nearestnodeindex:
                     othernodeindex = edge[1]
                  if edge[1] == model.nearestnodeindex:
                     othernodeindex = edge[0]
                  if othernodeindex>=0:
                     color = HIGHLIGHTCOLOR
               
                  pg.draw.line(model.fg, color, node1[0], node2[0],5)
                  
           if state=='editor':
              model.fg.fill((0,0,0,0))           
              
              text = textfont.render('Press S to save the game.', True, BLACK)
              (tw,th) = text.get_size()
              model.fg.blit(text,((sw-tw)/2,20))
           
              text = textfont.render('Press any other key to start the game.', True, BLACK)
              (tw,th) = text.get_size()
              model.fg.blit(text,((sw-tw)/2,30+th))

              text = textfont.render('click to create or delete node or edge, nodes can be dragged.', True, BLACK)
              (tw,th) = text.get_size()
              model.fg.blit(text,(10,sh-th-10))

              #text = textfont.render('nearest node index:'+str(model.nearestnodeindex), True, BLACK)
              #(tw,th) = text.get_size()
              #model.fg.blit(text,(10,sh-th-36))
           
              nearestedgeexists = False
              for edge in model.edges:
                    if not(model.nearestedge is None) and edge == model.nearestedge:
                       pg.draw.line(model.fg, REMOVECOLOR, model.nodes[edge[0]][0],model.nodes[edge[1]][0],5)
                       nearestedgeexists = True
                    else:
                       node1 = model.nodes[edge[0]]
                       node2 = model.nodes[edge[1]]
                       pg.draw.line(model.fg, GRAPHCOLOR, node1[0],node2[0],5)
              if not model.nearestedge is None and not nearestedgeexists:
                 pg.draw.line(model.fg, ADDCOLOR, model.nodes[model.nearestedge[0]][0]
                                                     , model.nodes[model.nearestedge[1]][0],5)

              model.removenodeindex = -1
              if nearestedgeexists:
                 # check whether a node become standalone, if the edge is removed.
                 # if so, mark this nodes with REMOVECOLOR, too.
                 otheredges = [e for e in model.edges if not e==model.nearestedge and (e[0]==model.nearestedge[0] or e[1]==model.nearestedge[0])]
                 if len(otheredges)==0:
                    model.removenodeindex = model.nearestedge[0]
                 
                 otheredges = [e for e in model.edges if not e==model.nearestedge and (e[0]==model.nearestedge[1] or e[1]==model.nearestedge[1])]
                 if len(otheredges)==0:
                    model.removenodeindex = model.nearestedge[1]

              genus = len(model.edges)-len(model.nodes)+1
              nodes = 0
              dollars = 0
              for (node,nodeamount) in model.nodes.values():
                 nodes+=1
                 dollars+=nodeamount
              
              text = textfont.render('Genus:'+str(genus)+' Dollars:'+str(dollars), True, BLACK)
              (tw,th) = text.get_size()
              model.fg.blit(text,(sw-tw-10,sh-th-10))

              latestnode = None
              for latestnodeindex in range(model.nodeidcounter,-1,-1):
                 try:
                    latestnode = model.nodes[latestnodeindex][0]
                    break
                 except:
                    continue
                 

              if model.nearestedge is None and model.nearestnodeindex<0 and not model.newnode is None:
                 if not latestnode is None:
                    pg.draw.line(model.fg, ADDCOLOR, latestnode, model.newnode,5)
                    
                 pg.draw.circle(model.fg, TRANSPARENTCOLOR, model.newnode, CIRCLESIZE)
                 pg.draw.circle(model.fg, ADDCOLOR, model.newnode, CIRCLESIZE, 5)
                 myfont = pg.font.Font(NODEFONT, int(.60*TITLEFONTSIZE))
                 amount = myfont.render(str(0), True, ADDCOLOR)
                 model.fg.blit(amount,(model.newnode[0]-amount.get_width()/2,model.newnode[1]-amount.get_height()/2+5))

           if state!='title':         
              for (node,nodeamount) in model.nodes.values():
                 pg.draw.circle(model.fg, TRANSPARENTCOLOR, node, CIRCLESIZE)
                 if   model.nearestnodeindex>=0 and node == model.nodes[model.nearestnodeindex][0]:
                      color = HIGHLIGHTCOLOR
                 elif model.removenodeindex>=0  and node == model.nodes[model.removenodeindex ][0]:
                      color = REMOVECOLOR
                 else:
                      color = GRAPHCOLOR
                 pg.draw.circle(model.fg, color, node, CIRCLESIZE, 5)
                 myfont = pg.font.Font(NODEFONT, int(.60*TITLEFONTSIZE))
                 amount = myfont.render(str(nodeamount), True, color)
                 model.fg.blit(amount,(node[0]-amount.get_width()/2,node[1]-amount.get_height()/2+5))


           if model.draw:
              self.screen.blit(model.bg,(0,0))
              self.screen.blit(model.fg,(0,0))
              pg.display.update()

              model.draw = False
        
class Controller:
    def __init__(self):
        pg.init()
        pg.font.init()
        pg.display.set_caption("Dollar Game")
        pg.mouse.set_visible(1)
        self.done = False
        self.model = Model()
        self.view = View()

        try:
           with open('dollargame.sav','rb') as savegame:
                self.model.nodes = pickle.load(savegame)
                self.model.edges = pickle.load(savegame)
                self.model.nodeidcounter = pickle.load(savegame)
        except:
           pass
        
    def setup_states(self, state_dict, start_state):
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]
        self.state.startup(self.model)
    def flip_state(self):
        self.state.done = False
        self.state_name = self.state.next
        self.state.cleanup(self.model)
        self.state = self.state_dict[self.state_name]
        self.state.startup(self.model)
    def update(self):
        if self.state.done:
           self.flip_state()
        self.view.update(self.model, self.state_name)
    def event_loop(self):
        pg.time.delay(10)
        for event in pg.event.get():
            if event.type == pg.QUIT:
               self.done = True
            self.state.doevent(event, self.model)

    def main_event_loop(self):
        while not self.done:
            self.event_loop()
            self.update()

def main():
    app = Controller()
    state_dict = {
        'title' : Title(),
        'editor': Editor(),
        'game'  : Game()
    }
    app.setup_states(state_dict, 'title')
    app.main_event_loop()

    pg.quit()
    sys.exit()

###### END of main game code


# auto id dictionary (autoiddict) is a dictionary with an id counter
# for automatic key generation (quite like a database table autonumber for primarykeys)
# This is handy, if you reference dictionary values by keys in other lists or sets or dictionaries
# and want the same id number used as key to always reference the same value

class autoiddict(dict):
    def __init__(self):
        dict.__init__(self)
        self.idcounter = 0

    def __missing(self,key):
        return None

    def add(self, value):
        key = self.idcounter
        self[key] = value
        self.idcounter+=1
        return key

    def __setitem__(self, key, value):
        if key is None:
           self.add(value)
        else:
           dict.__setitem__(self, key, value)

    def __iter__(self):
        return iter(self.items())

class Vec2d(object):
    """2d vector class, supports vector and scalar operators,
       and also provides a bunch of high level functions
       """
    __slots__ = ['x', 'y']

    def __init__(self, x_or_pair, y = None):
        if y == None:
            self.x = x_or_pair[0]
            self.y = x_or_pair[1]
        else:
            self.x = x_or_pair
            self.y = y

    def __len__(self):
        return 2

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise IndexError("Invalid subscript "+str(key)+" to Vec2d")

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        else:
            raise IndexError("Invalid subscript "+str(key)+" to Vec2d")

    # String representaion (for debugging)
    def __repr__(self):
        return 'Vec2d(%s, %s)' % (self.x, self.y)

    # Comparison
    def __eq__(self, other):
        if hasattr(other, "__getitem__") and len(other) == 2:
            return self.x == other[0] and self.y == other[1]
        else:
            return False

    def __ne__(self, other):
        if hasattr(other, "__getitem__") and len(other) == 2:
            return self.x != other[0] or self.y != other[1]
        else:
            return True

    def __nonzero__(self):
        return bool(self.x or self.y)

    # Generic operator handlers
    def _o2(self, other, f):
        "Any two-operator operation where the left operand is a Vec2d"
        if isinstance(other, Vec2d):
            return Vec2d(f(self.x, other.x),
                         f(self.y, other.y))
        elif (hasattr(other, "__getitem__")):
            return Vec2d(f(self.x, other[0]),
                         f(self.y, other[1]))
        else:
            return Vec2d(f(self.x, other),
                         f(self.y, other))

    def _r_o2(self, other, f):
        "Any two-operator operation where the right operand is a Vec2d"
        if (hasattr(other, "__getitem__")):
            return Vec2d(f(other[0], self.x),
                         f(other[1], self.y))
        else:
            return Vec2d(f(other, self.x),
                         f(other, self.y))

    def _io(self, other, f):
        "inplace operator"
        if (hasattr(other, "__getitem__")):
            self.x = f(self.x, other[0])
            self.y = f(self.y, other[1])
        else:
            self.x = f(self.x, other)
            self.y = f(self.y, other)
        return self

    # Addition
    def __add__(self, other):
        if isinstance(other, Vec2d):
            return Vec2d(self.x + other.x, self.y + other.y)
        elif hasattr(other, "__getitem__"):
            return Vec2d(self.x + other[0], self.y + other[1])
        else:
            return Vec2d(self.x + other, self.y + other)
    __radd__ = __add__

    def __iadd__(self, other):
        if isinstance(other, Vec2d):
            self.x += other.x
            self.y += other.y
        elif hasattr(other, "__getitem__"):
            self.x += other[0]
            self.y += other[1]
        else:
            self.x += other
            self.y += other
        return self

    # Subtraction
    def __sub__(self, other):
        if isinstance(other, Vec2d):
            return Vec2d(self.x - other.x, self.y - other.y)
        elif (hasattr(other, "__getitem__")):
            return Vec2d(self.x - other[0], self.y - other[1])
        else:
            return Vec2d(self.x - other, self.y - other)
    def __rsub__(self, other):
        if isinstance(other, Vec2d):
            return Vec2d(other.x - self.x, other.y - self.y)
        if (hasattr(other, "__getitem__")):
            return Vec2d(other[0] - self.x, other[1] - self.y)
        else:
            return Vec2d(other - self.x, other - self.y)
    def __isub__(self, other):
        if isinstance(other, Vec2d):
            self.x -= other.x
            self.y -= other.y
        elif (hasattr(other, "__getitem__")):
            self.x -= other[0]
            self.y -= other[1]
        else:
            self.x -= other
            self.y -= other
        return self

    # Multiplication
    def __mul__(self, other):
        if isinstance(other, Vec2d):
            return Vec2d(self.x*other.x, self.y*other.y)
        if (hasattr(other, "__getitem__")):
            return Vec2d(self.x*other[0], self.y*other[1])
        else:
            return Vec2d(self.x*other, self.y*other)
    __rmul__ = __mul__

    def __imul__(self, other):
        if isinstance(other, Vec2d):
            self.x *= other.x
            self.y *= other.y
        elif (hasattr(other, "__getitem__")):
            self.x *= other[0]
            self.y *= other[1]
        else:
            self.x *= other
            self.y *= other
        return self

    # Division
    def __div__(self, other):
        return self._o2(other, operator.div)
    def __rdiv__(self, other):
        return self._r_o2(other, operator.div)
    def __idiv__(self, other):
        return self._io(other, operator.div)

    def __floordiv__(self, other):
        return self._o2(other, operator.floordiv)
    def __rfloordiv__(self, other):
        return self._r_o2(other, operator.floordiv)
    def __ifloordiv__(self, other):
        return self._io(other, operator.floordiv)

    def __truediv__(self, other):
        return self._o2(other, operator.truediv)
    def __rtruediv__(self, other):
        return self._r_o2(other, operator.truediv)
    def __itruediv__(self, other):
        return self._io(other, operator.floordiv)

    # Modulo
    def __mod__(self, other):
        return self._o2(other, operator.mod)
    def __rmod__(self, other):
        return self._r_o2(other, operator.mod)

    def __divmod__(self, other):
        return self._o2(other, operator.divmod)
    def __rdivmod__(self, other):
        return self._r_o2(other, operator.divmod)

    # Exponentation
    def __pow__(self, other):
        return self._o2(other, operator.pow)
    def __rpow__(self, other):
        return self._r_o2(other, operator.pow)

    # Bitwise operators
    def __lshift__(self, other):
        return self._o2(other, operator.lshift)
    def __rlshift__(self, other):
        return self._r_o2(other, operator.lshift)

    def __rshift__(self, other):
        return self._o2(other, operator.rshift)
    def __rrshift__(self, other):
        return self._r_o2(other, operator.rshift)

    def __and__(self, other):
        return self._o2(other, operator.and_)
    __rand__ = __and__

    def __or__(self, other):
        return self._o2(other, operator.or_)
    __ror__ = __or__

    def __xor__(self, other):
        return self._o2(other, operator.xor)
    __rxor__ = __xor__

    # Unary operations
    def __neg__(self):
        return Vec2d(operator.neg(self.x), operator.neg(self.y))

    def __pos__(self):
        return Vec2d(operator.pos(self.x), operator.pos(self.y))

    def __abs__(self):
        return Vec2d(abs(self.x), abs(self.y))

    def __invert__(self):
        return Vec2d(-self.x, -self.y)

    # vectory functions
    def get_length_sqrd(self):
        return self.x**2 + self.y**2

    def get_length(self):
        return math.sqrt(self.x**2 + self.y**2)
    def __setlength(self, value):
        length = self.get_length()
        self.x *= value/length
        self.y *= value/length
    length = property(get_length, __setlength, None, "gets or sets the magnitude of the vector")

    def rotate(self, angle_degrees):
        radians = math.radians(angle_degrees)
        cos = math.cos(radians)
        sin = math.sin(radians)
        x = self.x*cos - self.y*sin
        y = self.x*sin + self.y*cos
        self.x = x
        self.y = y

    def rotated(self, angle_degrees):
        radians = math.radians(angle_degrees)
        cos = math.cos(radians)
        sin = math.sin(radians)
        x = self.x*cos - self.y*sin
        y = self.x*sin + self.y*cos
        return Vec2d(x, y)

    def get_angle(self):
        if (self.get_length_sqrd() == 0):
            return 0
        return math.degrees(math.atan2(self.y, self.x))
    def __setangle(self, angle_degrees):
        self.x = self.length
        self.y = 0
        self.rotate(angle_degrees)
    angle = property(get_angle, __setangle, None, "gets or sets the angle of a vector")

    def get_angle_between(self, other):
        cross = self.x*other[1] - self.y*other[0]
        dot = self.x*other[0] + self.y*other[1]
        return math.degrees(math.atan2(cross, dot))

    def normalized(self):
        length = self.length
        if length != 0:
            return self/length
        return Vec2d(self)

    def normalize_return_length(self):
        length = self.length
        if length != 0:
            self.x /= length
            self.y /= length
        return length

    def perpendicular(self):
        return Vec2d(-self.y, self.x)

    def perpendicular_normal(self):
        length = self.length
        if length != 0:
            return Vec2d(-self.y/length, self.x/length)
        return Vec2d(self)

    def dot(self, other):
        return float(self.x*other[0] + self.y*other[1])

    def get_distance(self, other):
        return math.sqrt((self.x - other[0])**2 + (self.y - other[1])**2)

    def get_dist_sqrd(self, other):
        return (self.x - other[0])**2 + (self.y - other[1])**2

    def projection(self, other):
        other_length_sqrd = other[0]*other[0] + other[1]*other[1]
        projected_length_times_other_length = self.dot(other)
        return other*(projected_length_times_other_length/other_length_sqrd)

    def cross(self, other):
        return self.x*other[1] - self.y*other[0]

    def interpolate_to(self, other, range):
        return Vec2d(self.x + (other[0] - self.x)*range, self.y + (other[1] - self.y)*range)

    def convert_to_basis(self, x_vector, y_vector):
        return Vec2d(self.dot(x_vector)/x_vector.get_length_sqrd(), self.dot(y_vector)/y_vector.get_length_sqrd())

    def __getstate__(self):
        return [self.x, self.y]

    def __setstate__(self, dict):
        self.x, self.y = dict


if __name__ == '__main__':
    main()
