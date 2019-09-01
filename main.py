# Project Zart
# Formerly Panda3D AI Demo

# Project by Christian Diaz @chrisd149

#  ______                       _____     __________
#      //         //\\         ||   \\        ||
#     //         //__\\        ||   //        ||
#    //         //    \\       ||  ||         ||
#   //_____    //      \\      ||   \\        ||
#
# This is a path finding project that uses a toon actor as a
# test actor for a path finding function.


import direct.directbase.DirectStart
from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from direct.actor.Actor import Actor
from panda3d.ai import *
from direct.gui.DirectGui import *
import sys


def addOnscreenText(x, y, txt):
    return OnscreenText(text=txt,
                        style=1,
                        fg=(1, 1, 1, 1),
                        pos=(x, y),
                        align=TextNode.ALeft,
                        scale=.05,
                        wordwrap=12
                        )


def addButtons(x, y, z, txt, command):
    return DirectButton(text=txt,
                        pos=(x, y, z),
                        scale=.05,
                        command=command
                        )


def addEntry(x, y, z, txt, command):
    return DirectEntry(initialText=txt,
                       text_pos=(-.34, 0, 0),
                       pos=(x, y, z),
                       scale=.05,
                       command=command,
                       numLines=1,
                       width=1.75
                       )


class Scene(DirectObject):
    def __init__(self):
        self.log = open('log.txt', "w+")

        # OnscreenText objects
        addOnscreenText(1.2, .9, "Spam the buttons to make the toon pursure the cog or wander around")
        addOnscreenText(-1.8, .95, "Project Zart            Version: 1.0.0 Alpha    "
                                   "     Author: Christian Diaz    Build: Panda3D-1.10.3")
        # inconsistent spacing is to make the text run into the next line
        addOnscreenText(1.2, .2, "Enter the coordinates of your Go To target, and click the ENTER key after typing in"
                                 " your value for each field.")

        # buttons
        addButtons(1.5, 0, .4, "Go To", self.go_to)
        addButtons(1.5, 0, .5, "Exit", self.exit)

        # entries
        self.x_seek_entry = addEntry(1.425, 0, .3, "X", self.X)
        self.y_seek_entry = addEntry(1.525, 0, .3, "Y", self.Y)

        self.load_models()

    def load_models(self):
        # loads .egg environment
        environment = loader.loadModel('meshs/final_blender_plane_col.egg')
        environment.reparentTo(render)
        environment.setHpr(0, -90, 0)

        # toon starting pos
        self.toon_start = Point3(0, -20, 0)

        # toon models
        self.toon_legs = Actor('phase_3\models\char/tt_a_chr_dgs_shorts_legs_1000.bam')
        self.toon_torso = Actor('phase_3\models\char/tt_a_chr_dgm_shorts_torso_1000.bam')
        self.toon_head = Actor('phase_3\models\char/tt_a_chr_dgm_skirt_head_1000.bam')

        self.toon = Actor({'legs': self.toon_legs, 'torso': self.toon_torso, 'head': self.toon_head},
                          {'legs': {'Static': 'phase_3\models\char/tt_a_chr_dgs_shorts_legs_1000.bam',
                                    'Idle': 'phase_3/models/char/tt_a_chr_dgs_shorts_legs_neutral.bam',
                                    'Walk': 'phase_3.5/models/char/tt_a_chr_dgs_shorts_legs_walk.bam',
                                    'Wave': 'phase_3.5/models/char/tt_a_chr_dgs_shorts_legs_wave.bam',
                                    'Run': 'phase_3/models/char/tt_a_chr_dgs_shorts_legs_run.bam', },

                           'torso': {'Static': 'phase_3\models\char/tt_a_chr_dgm_shorts_torso_1000.bam',
                                     'Idle': 'phase_3/models/char/tt_a_chr_dgm_shorts_torso_neutral.bam',
                                     'Walk': 'phase_3.5/models/char/tt_a_chr_dgm_shorts_torso_walk.bam',
                                     'Wave': 'phase_3.5/models/char/tt_a_chr_dgm_shorts_torso_wave.bam',
                                     'Run': 'phase_3/models/char/tt_a_chr_dgm_shorts_torso_run.bam', },

                           'head': {'Idle': 'phase_3/models/char/tt_a_chr_dgm_skirt_head_neutral.bam',
                                    'Walk': 'phase_3.5/models/char/tt_a_chr_dgm_skirt_head_walk.bam',
                                    'Wave': 'phase_3.5/models/char/tt_a_chr_dgm_skirt_head_wave.bam',
                                    'Run': 'phase_3/models/char/tt_a_chr_dgm_skirt_head_run.bam', }})

        self.toon.attach('torso', 'legs', 'joint_hips')
        self.toon.attach('head', 'torso', 'def_head')
        self.toon.reparentTo(render)
        self.toon.setPos(self.toon_start)
        self.toon.loop('Idle')

        # AI world and character creation
        self.AIworld = AIWorld(render)
        self.AIchar = AICharacter("toon", self.toon, 60, 0.1, 5)
        self.AIworld.addAiChar(self.AIchar)
        self.AIbehaviors = self.AIchar.getAiBehaviors()
        # gets all the behaviors for toon ai chars

        base.cam.reparentTo(self.toon)
        base.cam.setPosHpr((0, -25, 5), (0, -10, 0))

    def X(self, textEntered):
        # gets the x entry value and converts it to an interger
        self.get_x = DirectEntry.get(self.x_seek_entry)
        int(self.get_x)

    def Y(self, textEntered):
        # gets the y entry value and converts it to an interger
        self.get_y = DirectEntry.get(self.y_seek_entry)
        int(self.get_y)

    def go_to(self):
        self.go_button = addButtons(1.5, 0, -.1, "GO", self.path_finding)
        self.go_button.setScale(.1)
        self.selected_pos = Point3((float(self.get_x)), (float(self.get_y)), 0)
        # Moves toon to the selected LPoint3f Position, via the A* algorithm

        self.arrow = loader.loadModel('models/arrow.egg')
        self.arrow.reparentTo(render)
        self.arrow.setPosHprScale(self.selected_pos, (0, 0, 0), (2, 2, 2))
        self.AIbehaviors.initPathFind('meshs/navmesh.csv')
        # Loads an arrow at the selected pos

    def path_finding(self):
        self.arrow.remove_node()
        del self.arrow
        # destroys go_button until rendered with go_to button
        self.go_button.destroy()
        del self.go_button  # destroys the go_button

        self.AIbehaviors.pathFindTo(self.selected_pos)

        # adds PathFindTo task to taskMgr
        taskMgr.add(self.AIUpdate, "AIUpdate")
        print('\nGoing to', self.selected_pos)

        self.log.write("\nGoing  to ")
        self.log.write(str(self.selected_pos))

    # Updates all AI in self.AIworld
    def AIUpdate(self, task):
        self.AIworld.update()
        if self.AIbehaviors.behaviorStatus('pathfollow') == 'done':
            self.toon.loop('Idle')
            print('\nCompleted task in', task.time, 'seconds')
            self.log.write('\nCompleted task in')
            self.log.write(str(task.time))
            self.log.write('seconds.')
            return task.done
        elif self.AIbehaviors.behaviorStatus('pathfollow') != 'done':
            return task.cont

    @staticmethod
    def exit():
        sys.exit()


scene = Scene()
base.run()
