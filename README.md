# Dollar Game
The dollar game as shown on numberphile (youtube channel)

You need:
-poython (3.5+) (https://www.python.org/downloads/)
-pygame (https://www.pygame.org) - I recommend to install pip for installations
-this repository (dollargame.py, brownpaper.jpg, Kalam.ttf or Kalam.woff2)
-any non standardd python modules I forgot to mention

The game and editor should be intuitively usable

##Editor

Colors indicate what you get when you click: What is drawn green will be added to the game graph, what is red will be removed. What is white can be dragged or edited, i.e. the node dollar amount can be decremented with left click, incremented with right click. New nodes are added with an edge to the last node.

To remove a node you need to delete all edges to it. You can create a separation of a graph into two graphs, the Editor doesn't prevent that, you can even have a separate single node. In that case create an edge to link the grpahs back into one. Especially to remove an orphaned node first add an edge to it and then delete that adge again.

The editor computes the genus and dollar sum, as the numberphile video says, the game is solvable, if the amount of dollars is at least the genus of the graph.

##Game

When you hover a node you see all edges playing a role, left cleck means giving dollors, right click taking dollars.
A game ends if all nodes are non negative.
