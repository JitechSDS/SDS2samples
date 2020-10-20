# startup code begin
import os
import Drawing
import GroupMember as GM #thanks to BV
from model import member as modelMem
from param import *
from math import *
Units("feet")
saved_sds2_version = '2017.21'
saved_python_version = (2, 7, 2, 'final', 0)
try:
    from shape import Shape
    from point import Point, PointLocate
    from member import Member, MemberLocate
    from mtrl_list import MtrlLocate, HoleLocate
    from cons_line import ConsLine
    from cons_circle import ConsCircle
    from rnd_plate import RndPlate
    from rect_plate import RectPlate
    from bnt_plate import BntPlate
    from rolled_section import RolledSection
    from weld_add import Weld
    from flat_bar import FlatBar
    from hole_add import Hole
    from bolt_add import Bolt
    from roll_plate import RollPl
    from sqr_bar import SqrBar
    from rnd_bar import RndBar
    from shr_stud import ShrStud
    from grate import Grate
    from grate_trd import GrateTrd
    from deck import Deck
    from mtrl_fit import MtrlFit
    from version import CurrentVersion, VersionCompare
    curr_version = CurrentVersion()
except ImportError:
    curr_version = 'None' 
    def VersionCompare( v1, v2 ):
        return -1
if VersionCompare( curr_version, '6.311' ) >= 0:
    from job import Job
    from fab import Fabricator
if VersionCompare( curr_version, '6.312' ) >= 0:
    from plate_layout import PlateLayout
if VersionCompare( curr_version, '6.314' ) >= 0:
    from plate_layout import BntPlateLayout
if VersionCompare( curr_version, '6.4' ) >= 0:
    from mtrl_cut import MtrlCut
if VersionCompare( curr_version, '7.006' ) >= 0:
    from member import MemberAllocated
if VersionCompare( curr_version, '7.009' ) >= 0:
    from job import JobName
    from fab import FabricatorName
if VersionCompare( curr_version, '7.1' ) >= 0:
    from job import ProcessJob
    from job import ProcessOneMem
    from view import View
    from clevis import Clevis
    from turnbuckle import Turnbuckle
    from member import MultiMemberLocate
    from mtrl_list import MtrlByGuid
if VersionCompare( curr_version, '7.101' ) >= 0:
    from member import MemberProperties
    from member import MemberPropertySet
if VersionCompare( curr_version, '7.109' ) >= 0:
    from assembly import Assembly
    from assembly import AssemblyList
if VersionCompare( curr_version, '7.110' ) >= 0:
    from member import GroupMemberCreate
if VersionCompare( curr_version, '7.113' ) >= 0:
    from member import MarkMemberForProcess
if VersionCompare( curr_version, '7.132' ) >= 0:
    from mtrl_list import MtrlProperties
    from mtrl_list import MtrlPropertySet
    from job import JobProperties
    from job import JobPropertySet
# startup code end

path2save = 'C:\Users\$USERNAME\Desktop'
name1 = 'GatherToLoad'
name2 = 'GatherForTransmittal'
#fullname1 = os.path.join(path2save,name1+".sel")
#fullname2 = os.path.join(path2save,name2+".sel")
fullname1 = os.path.join(os.path.expandvars(path2save),name1+".sel")
fullname2 = os.path.join(os.path.expandvars(path2save),name2+".sel")

subs = []
dict_keys = []
dict_list_gfl = []
dict_list_gtr = []
load_only = []
lded_gather = Drawing.GetAllGatherSheetNames()

mem_list = MultiMemberLocate("Members")

for mem in mem_list:
    if mem.type == 'Misc':
        m = modelMem(mem.member_number)#if misc group_num not avaliable in member.Members convert to model and store group_number
        group_number = m.group_num
    else:
        group_number = mem.group_num
    if group_number == 0:                #thanks to BV
        #print("no group mrmber")
        for i in range(mem.mtrl_quantity):
            mtrl = mem.material(i)
            if mtrl.main_mtrl == 'No':
                if mtrl.piecemark.startswith('hss') or mtrl.piecemark.startswith('rb') or mtrl.piecemark.startswith('m'):
                    continue
                else:
                    if mtrl.piecemark not in subs:
                        subs.append(mtrl.piecemark)
                    else:
                        continue
            else:
                continue
    else:
        #print("group member")
        for g in range(mem.mtrl_quantity):
            mtrlg = mem.material(g)
            if mtrlg.piecemark.startswith('hss') or mtrlg.piecemark.startswith('rb') or mtrlg.piecemark.startswith('m'):
                    continue
            else:
                if mtrlg.piecemark not in subs:
                    subs.append(mtrlg.piecemark)
                else:
                    continue
            
for j in subs:
    if j in lded_gather:
        continue
    else:
        load_only.append(j)

for k in load_only:
    my_dict = dict(text=k,)
    dict_list_gfl.append(my_dict)

for m in subs:
    my_dict2 = dict(text=m,)
    dict_list_gtr.append(my_dict2)

dict_sel = dict(selection=dict_list_gfl)
dict_sel2 = dict(selection=dict_list_gtr)

GTL = str(dict_sel)
GTL = GTL.replace('\'', '\"')#replaces '' with "" before writing to file
GTT = str(dict_sel2)
GTT = GTT.replace('\'', '\"')

with open(fullname1, "w") as file1:
    file1.write(GTL)

with open(fullname2, "w") as file2:
    file2.write(GTT)

ClearSelection()

