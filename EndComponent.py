"""
This purpose of this module is to illustrate a component that has a algorithmic
design variable, i.e. a variable that is algorithmically computed but can be
overridden by the user to a specific value.

This example uses the experimental AlgorithmicVariable module and code from the
BoltedPlatesComponent. Notice the versioning and edit code is mostly cut and
paste with the only differences related to 'other_member' being a
AlgorithmicVariable instead of an int.

The biggest difference between a plugin that has AlgorithmicVariables like
ExampleEndComponent and one that does not, like BoltedPlatesComponent is
that DesignForMember needs to compute the algorithmic values.  In this case,
DesignForMember calls MoveToEnd which is where the algorithmic values are determined.
"""

from BoltedPlates import BoltedPlatesCreate
import Component
import Designable.Existing as Existing
import AlgorithmicVariable as AV
import Designable.Processable as Processable
import Designable.ProcessableComponent as ProcessableComponent
import PluginSetupTools
import Point3D
import componentedit
import component_tools
import copy
import dialog
import dialog.checkbox
import dialog.dimension
import job
import param

Versions = (
        {'width':24., '_other_member':AV.AlgorithmicVariable(0)}
        ,
        )

def LatestVersionNumber():
    return len(Versions) -1

def LatestVersion():
    return Versions[-1]

def CurrentVersionDict(*args, **kwargs):
    d = copy.deepcopy(LatestVersion())
    d.update(width = job.GetRefreshedJobPluginOption(
        ExampleEndComponent
        , EditEndComponentSetup()
        ).width)
    d.update(args, **kwargs)
    return d

def WindowPositionID():
    return '863b13c4-3f19-482c-9efe-6a7f9d2622fb'

def build_ui_in_frame(f):
    AV.IntEntry(f, '_other_member', 'Other member:')
    dialog.dimension.DimensionEntry(f, 'width', 'default', 'Width:').Validate(
        'width > 0.', 'Must be greater than 0')
    dialog.checkbox.Checkbox(f, 'graphical', 'Graphical')
    return f

class MemberEditUI(componentedit.ComponentUIHelper):
    column_foldname = '52e9c595-5dba-4cda-85f7-2418c1963051'

    def __init__(self, obj):
        componentedit.ComponentUIHelper.__init__(self)
        self.plugin = obj
        self.column_title = obj.Description()

    @componentedit.leaf('Settings', foldname='9ef98f66-5e7f-40dd-a20e-f374e619419d')
    def create_ui_leaf(self, f):
        build_ui_in_frame(f)
        return [self.plugin]

class StandAloneMultiEditUI(componentedit.ComponentUIHelper):
    column_foldname = MemberEditUI.column_foldname

    def __init__(self, model, column_title):
        componentedit.ComponentUIHelper.__init__(self)
        self.model = model
        self.column_title = column_title

    @componentedit.leaf('Settings', foldname='9ef98f66-5e7f-40dd-a20e-f374e619419d')
    def create_ui_leaf(self, f):
        build_ui_in_frame(f)
        return self.model

def EditInGadget(model, title):
    controller = componentedit.StandaloneComponentEditController(
            componentedit.StandaloneComponentEditView(
                WindowPositionID()
                , title
                )
            , StandAloneMultiEditUI(model, title)
            )
    controller.CreateUI()
    return controller.Run()

def EditInDialog(model, registered_name):
    if len(model) == 1:
        title = model[0].Description()
    else:
        title = 'Editing %s %ss' % (str(len(model)), registered_name)
    d = build_ui_in_frame(dialog.Dialog(title))
    d.RememberWindowPosition(WindowPositionID())
    d.model = model
    return d.Run()

class ExampleEndComponent(
        componentedit.MemberEditMethods
        , ProcessableComponent.EndComponent
        ):
    """
    Simple end component that algorithmically determines the connecting member
    but allows the user to override the value.
    """
    def __init__(self, *args, **kwargs):
        componentedit.MemberEditMethods.__init__(
                self
                , MemberEditUI
                )
        ProcessableComponent.EndComponent.__init__(
                self
                , **CurrentVersionDict(*args, **kwargs)
                )
        self._version = LatestVersionNumber()

    other_member = property(
            lambda x: x._other_member.Get()
            , lambda x, n: x._other_member.Set(n)
            )

    def MoveToEnd(self, mn, end):
        super(ExampleEndComponent, self).MoveToEnd(mn, end)
        l = ProcessableComponent.NodeMemberNumbers(mn, end)
        #should figure out how to have other_member stay system if it is in nodes
        #rather than just picking the first node...
        self._other_member.SetAlgorithmicValue(l[0] if len(l) else 0)

    def MembersCurrentlyObserved(self):
        return filter(lambda n: n, [self.other_member, self.member_number])

    def MultiEdit(self, others):
        return EditInGadget(
                [self] + others
                , ProcessableComponent.ClassNameDescription(self)
                if len(others) else self.Description()
                )

    def DesignForMember(self, mn):
        self.MoveToEnd(mn, self.end_index)
        modifies = self.MembersCurrentlyObserved()
        other = Existing.MemberOrNone(modifies[0] if len(modifies) else 0, int)
        if other:
            le = self.ref_point_in_global
            re = le + Point3D.Point3D(0,0,12.)
            for p in BoltedPlatesCreate.DesignBoltedPlates(mn, other, le, re, self.width):
                self.RegisterDesignProxy(p)
        return True

DesiredRegisteredName = 'Example end component'

class EditEndComponentSetup(object):
    def __init__(self, width = None):
        self.width = width if width else LatestVersion()['width']
    def __call__(self, *args, **kwargs):
        param.Units('inch')
        d = dialog.Dialog(
                '%s Setup' %
                Component.RegisteredClassDescription(ExampleEndComponent)
                )
        dialog.dimension.DimensionEntry(d, 'width', 'default', 'Width:').Validate(
                'width > 0.', 'Must be greater than 0'
                )
        d.model = [self]
        return d.Run()
    def __eq__(self, other):
        return type(self) == type(other) and self.__dict__ == other.__dict__
    def __ne__(self, other):
        return not self.__eq__(other)

def RegisterEndComponent():
    Component.RegisterComponentType(
            ExampleEndComponent
            , DesiredRegisteredName
            )
    component_tools.RegisterComponentAddCommand(ExampleEndComponent)
    PluginSetupTools.RegisterPluginSetup(
            ExampleEndComponent
            , EditEndComponentSetup()
            )

RegisterEndComponent()

if __name__ == '__main__':
    assert ExampleEndComponent(('width', 12.)).width == 12.
    assert ExampleEndComponent(width = 12.).width == 12.
    c = ExampleEndComponent(
            ('_other_member', AV.AlgorithmicVariable(34))
            , ('x', True)
            , width = 36.
            , s = 'hello'
            )
    assert c._other_member == AV.AlgorithmicVariable(34)
    assert c.other_member == 34
    assert c.x == True
    assert c.width == 36.
    assert c.s == 'hello'
    assert c == Processable._pickle_test(c)
    c.Edit()

