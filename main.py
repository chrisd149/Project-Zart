import direct.directbase.DirectStart
from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from direct.actor.Actor import Actor
from panda3d.ai import *
from direct.gui.DirectGui import *


def addOnscreenText(x, y, txt):
    return OnscreenText(text=txt,
                        style=1,
                        fg=(1, 1, 1, 1),
                        pos=(x, y),
                        align=TextNode.ALeft,
                        scale=.05,
                        wordwrap=15)


def addButtons(x, y, z, txt, command):
    return DirectButton(text=txt,
                        pos=(x, y, z),
                        scale=.05,
                        command=command
                        )


class Scene(DirectObject):
    def __init__(self):

        # onscreentext
        addOnscreenText(-1.75, .9, "Control the helper toon")
        # addOnscreenText(1, .9, "Spam the buttons to make the toon pursure the cog or wander around")

        #
        addButtons(1.5, 0, .5, "Pursure Cog", self.pursure_cog)
        addButtons(1.5, 0, .6, "Wander", self.wander)

        base.cam.setPosHpr((0, -25, 5), (0, -5, 0))

        self.load_models()
        self.cog_ai()

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
        self.toon.setPos(self.toon_start)
        self.toon.loop('Idle')

        # toon models
        self.helper_legs = Actor('phase_3\models\char/tt_a_chr_dgl_shorts_legs_1000.bam')
        self.helper_torso = Actor('phase_3\models\char/tt_a_chr_dgs_shorts_torso_1000.bam')
        self.helper_head = Actor('phase_3\models\char/tt_a_chr_dgm_skirt_head_1000.bam')

        self.helper = Actor({'legs': self.helper_legs, 'torso': self.helper_torso, 'head': self.helper_head},
                            {'legs': {'Static': 'phase_3\models\char/tt_a_chr_dgm_shorts_legs_1000.bam',
                                      'Idle': 'phase_3/models/char/tt_a_chr_dgl_shorts_legs_neutral.bam',
                                      'Walk': 'phase_3.5/models/char/tt_a_chr_dgs_shorts_legs_walk.bam',
                                      'Wave': 'phase_3.5/models/char/tt_a_chr_dgs_shorts_legs_wave.bam',
                                      'Run': 'phase_3/models/char/tt_a_chr_dgs_shorts_legs_run.bam', },

                             'torso': {'Static': 'phase_3\models\char/tt_a_chr_dgm_shorts_torso_1000.bam',
                                       'Idle': 'phase_3/models/char/tt_a_chr_dgs_shorts_torso_neutral.bam',
                                       'Walk': 'phase_3.5/models/char/tt_a_chr_dgm_shorts_torso_walk.bam',
                                       'Wave': 'phase_3.5/models/char/tt_a_chr_dgm_shorts_torso_wave.bam',
                                       'Run': 'phase_3/models/char/tt_a_chr_dgm_shorts_torso_run.bam', },

                             'head': {'Idle': 'phase_3/models/char/tt_a_chr_dgm_skirt_head_neutral.bam',
                                      'Walk': 'phase_3.5/models/char/tt_a_chr_dgm_skirt_head_walk.bam',
                                      'Wave': 'phase_3.5/models/char/tt_a_chr_dgm_skirt_head_wave.bam',
                                      'Run': 'phase_3/models/char/tt_a_chr_dgm_skirt_head_run.bam', }})

        self.helper.attach('torso', 'legs', 'joint_hips')
        self.helper.attach('head', 'torso', 'def_head')
        self.helper.reparentTo(render)
        self.helper.setPos(self.helper_start)
        self.helper.loop('Idle')

        # cog actor
        self.cog = Actor(Actor('phase_3.5\models\char\suitA-mod.bam',
                              {'Walk': 'phase_4\models\char\suitA-walk.bam',
                                  'Stand': 'phase_4\models\char\suitA-neutral.bam'}))

        self.cog.reparentTo(render)
        self.cog.setPosHpr((0, 0, 0),(90, 0, 0))


    def pursure_cog(self):
        # chases cog, prioitizes pursure over wander, (i.e. will put more
        # effort in chasing the cog over wandering around)
        self.AIchar = AICharacter("toon", self.toon, 100, 0.05, 5)
        self.AIworld.addAiChar(self.AIchar)
        self.AIbehaviors = self.AIchar.getAiBehaviors()

        self.AIbehaviors.pursue(self.cog, 1.0)

        self.toon.loop('Run')

    def wander(self):
        # wanders around a point
        self.AIchar = AICharacter("toon", self.toon, 100, 0.05, 5)
        self.AIworld.addAiChar(self.AIchar)
        self.AIbehaviors = self.AIchar.getAiBehaviors()

        self.AIbehaviors.wander(10, 10, 10, 0.75)

        self.toon.loop('Run')

    def cog_ai(self):
        # renders AI world
        self.AIworld = AIWorld(render)

        self.AIchar = AICharacter("cog", self.cog, 100, 0.05, 5)
        self.AIworld.addAiChar(self.AIchar)
        self.AIbehaviors = self.AIchar.getAiBehaviors()

        # evades toon, higher prioity over wander
        self.AIbehaviors.evade(self.toon, 15, 20, 1.0)

        # wanders around a point
        self.AIbehaviors.wander(-25, 25, 0, 0.5)

        # AI World update
        taskMgr.add(self.AIUpdate, "AIUpdate")

    # Updates all AI in self.AIworld
    def AIUpdate(self, task):
        self.AIworld.update()
        return task.cont
    # this causes the AI to get a bit wacky when too many
    # AI updates are made


app = Scene()
base.run()