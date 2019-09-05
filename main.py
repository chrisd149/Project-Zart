# Project Zart
# Formerly Panda3D AI Demo

# Project by Christian Diaz @chrisd149

#  ______                       _____     __________
#      //         //\\         ||   ))        ||
#     //         //__\\        ||   //        ||
#    //         //----\\       ||  ||         ||
#   //_____    //      \\      ||   \\        ||
#
# This is a path finding project that uses a toon actor as a
# test actor for a path finding function.

# Inspired by Baritone Project, a path finding plugin for
# Minecraft


import direct.directbase.DirectStart
from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from direct.actor.Actor import Actor
from panda3d.ai import *
from direct.gui.DirectGui import *
import sys
from direct.interval.IntervalGlobal import *
import time

start = time.time()


def addOnscreenText(x, y, txt):
    return OnscreenText(text=txt,
                        style=1,
                        fg=(0, 0, 0, 1),
                        pos=(x, y),
                        align=TextNode.ALeft,
                        scale=.05,
                        wordwrap=12
                        )


def addButtons(x, y, z, txt, command):
    return DirectButton(text=txt,
                        pos=(x, y, z),
                        scale=.05,
                        command=command,
                        enableEdit=1
                        )


def addEntry(x, y, z, txt, command):
    return DirectEntry(initialText=txt,
                       text_pos=(-.34, 0, 0),
                       pos=(x, y, z),
                       scale=.05,
                       numLines=1,
                       command=command,
                       width=1.75
                       )


def addFrame(a, b, c, d, x, y, z):
    return DirectFrame(frameSize=(a, b, c, d),
                       frameColor=(255, 255, 0, .1),
                       pos=(x, y, z))


class Scene(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        self.log = open('log.txt', "w+")
        self.taskMgr = taskMgr

        # OnscreenText objects
        addOnscreenText(-1.8, .95, "Project Zart            Version: 1.2.0 Alpha    "
                                   "     Author: Christian Diaz    Build: Panda3D-1.10.3")
        # inconsistent spacing is to make the text run into the next line
        self.initial_text = addOnscreenText(1.2, .4, "Enter the coordinates of your Go To target, and click the ENTER "
                                                     "key after typing in your value for each field.")
        addFrame(-.5, .5, .5, -.5, 1.5, 0, .5)

        # buttons
        self.go_to_button = addButtons(1.5, 0, .7, "Go To", self.go_to)
        addButtons(1.5, 0, .8, "Exit", self.exit)
        self.obstacle_button = addButtons(-1.6, 0, .7, "Add Obstacle", self.obstacle)

        # entries
        self.x_seek_entry = addEntry(1.425, 0, .6, "X", self.X)
        self.y_seek_entry = addEntry(1.525, 0, .6, "Y", self.Y)

        self.load_models()

    def load_models(self):
        # loads .egg environment
        environment = loader.loadModel('meshs/final_blender_plane_col.egg')
        environment.reparentTo(render)
        environment.setHpr(0, -90, 0)
        self.base = base

        # toon starting pos
        self.toon_start = Point3(0, 0, 0)

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
        self.AIchar = AICharacter("toon", self.toon, 50, 0.05, 10)
        self.AIworld.addAiChar(self.AIchar)
        self.AIbehaviors = self.AIchar.getAiBehaviors()


        # cog actor
        self.cog = Actor(Actor('phase_3.5\models\char\suitA-mod.bam',
                               {'Walk': 'phase_4\models\char\suitA-walk.bam',
                                'Stand': 'phase_4\models\char\suitA-neutral.bam'}))
        self.cog.reparentTo(render)
        self.cog.setPosHpr((0, 0, 0), (90, 0, 0))
        self.cog.setPos(30, -52.5, 0)

        move1 = self.cog.posInterval(10, Point3(-30, -52.5, 0))
        move2 = self.cog.posInterval(2.5, Point3(-30, -60, 0))
        move3 = self.cog.posInterval(10, Point3(30, -60, 0))
        move4 = self.cog.posInterval(2.5, Point3(30, -52.5, 0))

        pace = Sequence(
            move1,
            move2,
            move3,
            move4
        )

        pace.loop()

        self.AIbehaviors.evade(self.cog, 5, 5, .25)

        self.base.cam.setPosHpr((0, -25, 5), (0, -10, 0))

    def obstacle(self):
        self.cube = loader.loadModel('models/cube.egg')
        self.cube.reparentTo(render)
        self.cube.setPosHprScale((-5, 30, 1), (90, 0, 0), (1, 2, 1))
        self.cube.setColor(0, 255, 255)

        self.AIworld.addObstacle(self.cube)
        self.AIbehaviors.obstacleAvoidance(5)
        move_1 = self.cube.posInterval(5, Point3(7.5,  30, 1))
        move_2 = self.cube.posInterval(5, Point3(-5,  30, 1))

        move = Sequence(
            move_1,
            move_2
        )

        move.loop()

        self.obstacle_button.destroy()

    def X(self, textEntered):
        # gets the x entry value and converts it to an integer
        self.get_x = DirectEntry.get(self.x_seek_entry)

    def Y(self, textEntered):
        # gets the y entry value and converts it to an integer
        self.get_y = DirectEntry.get(self.y_seek_entry)

    def go_to(self):
        global taskAccumulator
        self.go_button = addButtons(1.5, 0, -.1, "GO", self.path_finding)
        self.go_button.setScale(.1)
        self.selected_pos = Vec3((float(self.get_x)), (float(self.get_y)), 0)
        self.arrow = loader.loadModel('models/arrow.egg')
        self.arrow.reparentTo(render)
        self.arrow.setPosHprScale((float(self.get_x), float(self.get_y), 2.5), (0, 0, 0), (2, 2, 2))

        # gets all the behaviors for toon ai chars
        self.taskMgr.add(self.AIUpdate, "AIUpdate")

        self.cancel_button = addButtons(1.5, 0, -.2, "Cancel", self.cancel_path_finding)
        self.cancel_button.setScale(.1)
        self.cancel_button['text_fg'] = (255, 0, 0, 1)
        self.initial_text.destroy()
        self.go_text = addOnscreenText(1.25, .3, "Select GO to go to selected position, or CANCEL to cancel input")

        # adds PathFindTo task to taskMgr
        self.AIbehaviors.initPathFind('meshs/navmesh.csv')

    def path_finding(self):
        global taskAccumulator
        self.go_button.destroy()  # destroys go_button until rendered with go_to button
        del self.go_button  # destroys the go_button
        self.cancel_button.destroy()
        del self.cancel_button
        self.go_text.destroy()
        self.pause_text = addOnscreenText(1.25, .3, "Select PAUSE to stop AI")

        self.pause_button = addButtons(1.5, 0, .1, "Pause", self.pause_ai)
        self.pause_button.setScale(.1)
        self.pause_button.setColor(255, 0, 0)

        self.AIbehaviors.pathFindTo(self.selected_pos)
        # Moves toon to the selected LPoint3f Position, via the A* algorithm

        print('\nGoing to', self.selected_pos)
        self.log.write("\nGoing  to ")
        self.log.write(str(self.selected_pos))
        self.arrow.setColor(255, 0, 0, 0)
        taskAccumulator = 1

    def cancel_path_finding(self):
        self.go_button.destroy()
        self.arrow.remove_node()
        self.cancel_button.destroy()
        del self.cancel_button
        self.taskMgr.remove("AIUpdate")

    def pause_ai(self):
        self.pause_button.destroy()
        del self.pause_button
        self.arrow.remove_node()
        self.AIbehaviors.pauseAi('toon')
        self.taskMgr.remove("AIUpdate")
        print('TASK STOPPED BY USER')
        self.log.write('\nTASK STOPPED BY USER AT')
        self.log.write(str(self.toon.getPos()))
        self.pause_text.destroy()
        del self.pause_text
        self.initial_text = addOnscreenText(1.2, .4, "Enter the coordinates of your Go To target, and click the "
                                                     "ENTER key after typing in your value for each field.")

    def AIUpdate(self, task):
        self.AIworld.update()
        get_toon_pos_x = str(self.toon.getX())
        get_toon_pos_y = str(self.toon.getY())
        toon_pos_x = round(float(get_toon_pos_x), -1)
        toon_pos_y = round(float(get_toon_pos_y), -1)
        # rounds toon's current X and Y values into a float

        x_difference = float(self.get_x) - toon_pos_x
        y_difference = float(self.get_y) - toon_pos_y
        # finds distance between X and Y values and selected pos

        # The getX and getY functions spit out a long float, so they
        # have to be rounded to match selected pos values.

        if 0 <= x_difference < 1:
            toon_pos_x = toon_pos_x - x_difference
            # Subtracts X difference from toon's X pos value
        if 0 >= x_difference > -1:
            toon_pos_x = toon_pos_x + x_difference
            # Adds X difference from toon's X pos value
        if 0 <= y_difference < 1:
            toon_pos_y = toon_pos_y - y_difference
            # Subtracts Y difference from toon's Y pos value
        if 0 >= y_difference > -1:
            toon_pos_y = toon_pos_y + y_difference
            # Adds Y difference to toon's X pos value
        # Checks if the toon's current X or Y difference from the
        # corresponding input X/Y are within a range between 0 and
        # 1.  This makes the toon_pos_x and toon_pos_y round almost
        # exactly to selected pos when they are greater/less than zero,
        # and less/greater than 1 or -1.

        toon_pos = Vec3(float(toon_pos_x), float(toon_pos_y), 0)
        # organizes toon's current pos to Vec3 format

        # Checks if selected pos and toon pos are the same Vec3 value, and
        # if the path find task is done, or at destination.
        if self.selected_pos == toon_pos and self.AIbehaviors.behaviorStatus('pathfollow') == 'done':
            self.toon.loop('Idle')
            self.arrow.remove_node()
            self.pause_button.destroy()
            del self.pause_button
            self.pause_text.destroy()
            del self.pause_text
            self.initial_text = addOnscreenText(1.2, .4, "Enter the coordinates of your Go To target, and click the "
                                                         "ENTER key after typing in your value for each field.")
            # sets initial text in right side of screen
            self.log.write('\nCompleted task in')
            self.log.write(str(task.time))
            self.log.write('seconds.')
            print('Arrived at destination', toon_pos, 'in ', str(task.time), 'seconds')
            return Task.done

        # Prints error message if only path follow check comes back positive.
        # This is due to position calculator not working 100% accurately.
        elif self.AIbehaviors.behaviorStatus('pathfollow') == 'done':
            self.arrow.remove_node()
            self.pause_button.destroy()
            del self.pause_button
            self.pause_text.destroy()
            del self.pause_text
            self.initial_text = addOnscreenText(1.2, .4, "Enter the coordinates of your Go To target, and click the "
                                                         "ENTER key after typing in your value for each field.")
            print("Error: Missed Target very closely, assuming task done")
            print(toon_pos)

        # Continues path finding task if task isn't done.
        if self.AIbehaviors.behaviorStatus('pathfollow') != 'done':
            return Task.cont

    def exit(self):
        print('Program Ended by User')
        print('Toon Pos:', self.toon.getPos())
        print('Cog Pos:', self.cog.getPos())
        self.log.write('Program Ended by User')
        self.log.write('\nToon Pos: ')
        self.log.write(str(self.toon.getPos()))
        self.log.write('\nCog Pos: ')
        self.log.write(str(self.cog.getPos()))
        sys.exit()


scene = Scene()
base.run()
