# Project Zart
# Formerly Panda3D AI Demo

import direct.directbase.DirectStart
from panda3d.core import *
from direct.showbase import DirectObject
from direct.task import Task
from direct.actor.Actor import Actor
from panda3d.ai import *
from direct.gui.DirectGui import *
from direct.task import Task



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
                        pos=(x, y, z),
                        scale=.05,
                        command=command,
                        numLines=1,
                        width=1
                        )


class Scene(DirectObject.DirectObject):
    def __init__(self):
        taskMgr.popupControls()
        # onscreentext
        # addOnscreenText(-1.75, .9, "Control the helper toon")
        addOnscreenText(1.2, .9, "Spam the buttons to make the toon pursure the cog or wander around")
        addOnscreenText(-1.8, .95, "Project Zart            Version: 1.0.0 Alpha    "
                                   "     Author: Christian Diaz    Build: Panda3D-1.10.3")
        # inconsistent spacing is to make the text run into the next line
        addOnscreenText(1.2, .2, "Enter the coordinates of your Go To target, and click the ENTER key after typing in"
                                 " your value for each field.")

        # buttons
        addButtons(1.5, 0, .4, "Go To", self.go_to)
        self.x_seek_entry = addEntry(1.425, 0, .3, "X", self.X)
        self.y_seek_entry = addEntry(1.525, 0, .3, "Y", self.Y)

        base.cam.setPosHpr((0, -50, 5), (0, -5, 0))

        self.load_models()

    def load_models(self):

        # toon starting pos
        self.toon_start = Point3(0, -25, 0)
        self.helper_start= Point3(5, -35, 0)

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
        #self.toon.setPos(self.toon_start)
        self.toon.loop('Idle')

        """# cog actor
        self.cog = Actor(Actor('phase_3.5\models\char\suitA-mod.bam',
                              {'Walk': 'phase_4\models\char\suitA-walk.bam',
                                  'Stand': 'phase_4\models\char\suitA-neutral.bam'}))

        self.cog.reparentTo(render)
        self.cog.setPosHpr((0, 0, 0),(90, 0, 0))"""

    def X(self, textEntered):
        # gets the x entry value and converts it to an interger
        self.get_x = DirectEntry.get(self.x_seek_entry)
        int(self.get_x)
        print("User picked", self.get_x, "as their x value")

    def Y(self, textEntered):
        # gets the y entry value and converts it to an interger
        self.get_y = DirectEntry.get(self.y_seek_entry)
        int(self.get_y)
        print("User picked", self.get_y, "as their y value")

    def go_to(self):
        self.go_button = addButtons(1.5, 0, -.1, "GO", self.seek)
        self.go_button.setScale(.1)
        self.selected_pos = Point3((float(self.get_x)), (float(self.get_y)), 0)
        # Moves toon to the selected Point3 Position

    def seek(self):
        self.AIworld = AIWorld(render)
        # chases cog, prioritizes pursue over wander, (i.e. will put more
        # effort in chasing the cog over wandering around)
        self.go_button.destroy()
        del self.go_button  # destroys the go_button

        self.AIchar = AICharacter("toon", self.toon, 100, 0.05, 5)
        self.AIworld.addAiChar(self.AIchar)
        self.AIbehaviors = self.AIchar.getAiBehaviors()

        taskMgr.add(self.AIUpdate, "AIUpdate", self.remove_task("AIUpdate"))

    def close_enough(self, task):
        self.AIworld.update()
        str_selected_pos = (str(self.selected_pos))
        self.selected_pos_no_str = ''.join(c for c in str_selected_pos if c not in "L P o i n t 3 f '( ) ")

        current_x = int(self.toon.getX())
        current_y = int(self.toon.getY())

        round_x = round(current_x, 5)
        round_y = round(current_y, 5)

        self.current_pos = (round_x, round_y, 0)

        x_difference = int(self.get_x) - current_x
        y_difference = int(self.get_y) - current_y
        if x_difference and y_difference <= 1:
            print('Done')
            self.AIbehaviors.removeAi('seek')
            return task.done

        else:
            print('Going to selected position,', self.selected_pos)
            self.AIbehaviors.seek(self.selected_pos)


    def AIUpdate(self, task):
        self.AIworld.update()
        str_selected_pos = (str(self.selected_pos))
        self.selected_pos_no_str = ''.join(c for c in str_selected_pos if c not in "L P o i n t 3 f '( ) ")

        current_x = int(self.toon.getX())
        current_y = int(self.toon.getY())

        round_x = round(current_x, 5)
        round_y = round(current_y, 5)

        self.current_pos = (round_x, round_y, 0)

        x_difference = int(self.get_x) - current_x
        y_difference = int(self.get_y) - current_y
        if x_difference and y_difference <= 1:


            print('Done')

        else:
            print(self.current_pos)
            self.AIbehaviors.seek(self.selected_pos)
            return task.cont
            print(self.AIbehaviors.behaviorStatus('seek', self.toon))

    # this causes the AI to get a bit wacky when too many
    # AI updates are made


app = Scene()
base.run()
