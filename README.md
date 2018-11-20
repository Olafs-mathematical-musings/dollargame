# Dollar Game
The dollar game as shown on numberphile (youtube channel)

You need:
- Python (3.5+) (https://www.python.org/downloads/)
- pygame (https://www.pygame.org) - I recommend to install pip for installations
- this repository (dollargame.py, brownpaper.jpg, Kalam.ttf or Kalam.woff2)
- any non standard python modules I forgot to mention

The game and editor should be intuitively usable

## Editor

Colors indicate what you get when you click: What is drawn green will be added to the game graph, what is red will be removed. What is white can be dragged or edited, i.e. the node dollar amount can be decremented with left click, incremented with right click. New nodes are added with an edge to the last node.

To remove a node you need to delete all edges to it. You can create a separation of a graph into two graphs, the editor doesn't prevent that, you can even have a separate single node. In that case create an edge to link it back to the graph. Especially to remove an orphaned node you first need to add an edge to it and then delete that edge again to also delete the node.

The editor computes the genus and dollar sum, as the numberphile video (https://www.youtube.com/watch?v=U33dsEcKgeQ) says, the game is solvable, if the amount of dollars is at least the genus of the graph.

## Game

When you hover a node you see all edges playing a role, left click means donating dollars, right click receiving dollars.
A game ends if all nodes are out of debt.
