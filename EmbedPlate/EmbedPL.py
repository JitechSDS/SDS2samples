###########################################################################
## EmbedPL.py Version 4.14
## Tested in SDS/2 Version 7.233
## Copyright (c) 2011 BV Detailing & Design, Inc.
## All rights reserved.
## Author: Bruce Vaughan
##
## Redistribution and use, with or without modification, are permitted
## provided that the following conditions are met:
##
##  * Redistributions of code must retain the above copyright notice, this
##    list of conditions and the following disclaimer.
##  * This software is NOT FOR SALE.
##  * This software is provided on an as-is basis. The author(s) and/or
##    owner(s) are not obligated to provide technical support or
##    assistance.
##  * This software does not include a warranty or guarantee of any kind.
##  * Any replication or modification to this software must have the
##    consent of its author(s) and/or owner(s).
##
## THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND COPYRIGHT HOLDER "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
## IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR OR COPYRIGHT
## HOLDER BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY HOWEVER CAUSED
## AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
## TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
## USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#############################################################################
"""
***************************************************************************
* IMPORTANT NOTES (version 4.14):                                         *
*    Recommended grades for DBAs and weldable rebar:                      *
*    Imperial: A496 (DBA), A706 (welded rebar)                            *
*    Metric: A496M (DBA), A706M (welded rebar)                            *
*    Metric, Canadian material: 400R, 300W, 400W, 500W                    *
*                                                                         *
*    This version will not work in SDS/2 versions prior to 7.204.         *
*                                                                         *
*    **Bent DBAs added to this custom member will rotate differently      *
*    depending on the current model orientation. It is important          *
*    to maintain a consistent model orientation when adding or editing    *
*    EmbedPL custom members.**                                            *
*    **ABOVE LIMITATION WAS OVERCOME IN SDS/2 VERSION 7.228               *
*                                                                         *
*    Bent DBAs with different input rotations will have the same          *
*    piecemark. This is accomplished by rotating the DBA into position.   *
*                                                                         *
*    A bent DBA rotation of 0 will orient the hook parallel to the member *
*    'X' axis when the view is normal to the NS Face of main material.    *
*                                                                         *
*    Members created with _version 0 will be updated to _version 1        *
*    when edited!!!                                                       *
*                                                                         *
*    Change member elevation and user material moves with the member.     *
*    Change member slope and user material will NOT rotate with the       *
*    member.                                                              *
*                                                                         *
*    Reset button only works on SDS/2 widgets and has no effect on        *
*    custom Tkinter widgets.                                              *
***************************************************************************
    
Originally developed in SDS2 7.021 1/29/06 (R1)

For comments, suggestions or questions post to SDS/2 Detailing Forum.

Version History:
1.02 (1/31/06):
    Incorporate mem.main_mtrl() to determine global points;
    mem.plan_rotation and mem.translate still broken
    
1.03 (2/3/06):
    Add path for defaults file. Go to "Variables" to modify system path.
    
1.04 (7/28/06):
    Add code to adjust plate and stud rotations for SDS/2 Versions 7.023
    and higher.

1.05 (9/12/06):
    Add material usage description to plate and stud material.

1.06 (10/22/06):
    Enable sequence for members ***SEQUENCE DOES NOT WORK***
    Add option to print documentation only
    
1.07 (3/15/07):
    Read/save default files - subdirectory 'SDS/2 root data'/macro/Defaults
    Image files - subdirectory 'SDS/2 root data'/macro/Images
    
1.08 (3/16/07):
    Corrected image path
    
1.09 (3/17/07):
    Import modules, update code
    
2.00 (12/7/07):
    Incorporate Job().sequences()
    Add ClearSelection()
    
2.01 (12/12/07):
    Fixed a few things
    
2.02 (2/29/08):
    Fixed name conflict plate_thick --> plate_thk
    
2.03 (3/4/08):
    Update embed plate member object to avoid TypeError in 7.116
    Get WP from mem.main_mtrl().pt1 to correct stud pattern misplacement in
    some plan rotations.

3.00 (11/18/09):
    Update to custom member EmbedPL.

3.01 (11/24/09):
    Implement StateAccessor
    Create class for dialog box

3.02 (11/27/09):
    Add some rules in dialog box
    Get stud and plate data from XML document
    
3.03 (11/29/09):
    Update to custom member _version = 1
    Add option for beam bearing plates
    Add option to add 'Anchor bolt' holes
    Add option to add DBAs straight, square hook, J Hook

3.04 (11/30/09):
    Rename to EmbedPL
    Change _version to 0

3.05 (12/17/09):
    Assign Point3D objects on edited member
    self.leftWP, self.rightWP, self.ctrPT

3.06 (12/18/09):
    Save doalog box window sizes and positions in XML data file
    Enable modification of XML data file data

3.07 (12/19/09):
    Rename variables no_cols, no_rows, x_spa, z_spa
    to studCols, studRows, studXSpa, studZSpa.
    The variable names are not pickled, only the type and value.
    Therefore, the variable names can be modified as long as the
    number and type of variables pickled remains constant.

3.08 (12/28/09):
    varKeys = self.model.plateinfo[optionList[0]] ----->
        varKeys = self.model.plateinfo[optionList[0]].keys()
    Omit width and height specifications for PlateEditDlg widget.

3.09 (12/31/09):
    Translate on self.rp1 to calculate points for studs and DBAs.
    Use Transform3D to set rotations for studs and straight DBAs.

3.10 (1/5/10):
    Add option to optionDialog "Edit setup data" which bypasses
    adding the member. The main dialog box will have only the
    "Setup" tab.

3.11 (1/13/10):
    Option "Preselected member" - if Beam or Joist member is
    preselected, bypass option dialog.

3.12 (1/19/10):
    Evaluate selected points by comparing to None instead of True or False.
    Point(0,0,0) evaluates False, and will fail the member add.

3.13 (1/21/10):
    Set member orientation with SetColumnOrientation()
    Rotate plate material: self.plate.rotate(mem, (360,0,0))
    Rotate bent DBAs: rb1.Rotate(rb1.Member, (0, 90, self.dbaZRot))

3.14 (2/3/10):
    Modify dialog box Setup tab to use Pack geometry manager.
    Add option to swap ends
    Configure all dialog box frames consistently
    Use EmbedPLDialog.MemberAttrController to set sequence, description,
    and is existing.

3.15 (2/6/10):
    if None not in [leftWP, rightWP]: will cause UnboundLocalError if
    leftWP not selected. Initialize end points:
        leftWP, rightWP = None, None

3.16 (2/15/10):
    Increment dbaZRot by 180 degrees for each subsequent row.

4.00 (3/4/10):
    Enable color selection dialog by context menu for color selection Entry
    fields. Increment _version to 1. Allow for studs and DBAs to be combined
    in a variable pattern. Add option to rotate every other row of bent DBAs
    180 degrees to entered rotation.
    
    Create new tab for studs and DBAs in a combined pattern with variable
    spacing. Tab name is currently 'Mixed'. Spacing format:
        '6' - denotes evenly spaced at 6
        '6,2,2,6' - denotes spacing between 5 columns
        
    Mixed stud and DBA pattern is entered into a table.
    
    Display an interactive 'Anchor Pattern' that adjusts to table entries.
    The pattern is read from the data (XML) file if option 'XML Data' is
    chosen.
    Example: 'DDD,S-S,S-S,DDD'
        This pattern denotes 3 columns and 4 rows. The top and bottom
        rows are fully populated with DBAs and the middle rows are studs
        with the middle column omitted.
    
    Display a table to fill with 'D', 'S', 'H', or '-' which indicates
    DBA, stud, hole, or empty at that location.
    
    Add minimum plate dimension label for 'Studs, DBAs, Holes' option.

    Add ability to read default data from XML file for joists by joist
    series ("G", "LH", "K").
    
    Options are:
        'Studs, DBAs, Holes', 'Studs and DBAs', 'Anchor Holes', 'Plain'
        
    New variables:
        anchorType
        anchorCols
        anchorRows
        anchorColSpa
        anchorRowSpa
        anchorPatt
        rotateAltDBAs
        member_version
        
4.01 (3/9/10):
    Improve functionality of label that displays minimum plate dimensions
    to accomodate Stud, DBA and Hole patterns. Calculation is made based
    on value of self.anchorType.

4.02 (3/10/10):
    User added material will now change elevation with Embed PL member if
    member elevation is changed in the member edit screen.
    Move minimum plate dimensions label to mainFrame.
    Change " " to "0" for anchorPatt. Options are now "D", "S", "0"

4.03 (3/17/10):
    Add code to assign grade of stud material to
    Job().steel_grades("Shear Stud").keys()[0]
    SDS/2 7.208 does not allow assignment of grade to stud material
    Grade of stud has no variable available for serialization in this
    version (1).

4.04 (5/29/10):
    Change option name "Mixed Studs and DBAs" to "Mixed Anchors"
    Added support for holes mixed with studs and DBAs
    Increase number of rows to 12 for "Anchor Holes" option

4.05 (7/27/10):
    Modify description to #8thsRebar and material usage to REBAR
    if the material grade is A706.
    Add condition at Edit() return - If model complete, return False

4.06 (10/5/2010):
    Add button on member screen to set all anchor columns and rows to zero.
    Switch "Mixed" and "Holes" tab locations.
    On Setup tab, replace plate information edit with "Plate Table" and
    stud information with "Stud Table". Import TableDlg for Plate and Stud
    Tables.
    Add context menu item Add Dialog to elevation, X rotation, vertical
    slope, and plan rotation widgets for member edit. Entry fields lose
    ability to accept focus (PR 19727). As a workaround, pick another
    window or focus on a Combobox and the abilty to accept focus is
    regained.

4.07 (10/25/2010):
    Save member description in defaults file.

4.08 (10/28/2010):
    Enable smooth dowels in lieu of DBAs.
    Material descriptions are set for A496 and A706.
    Material usage is set to 'Smooth Dowel' for grades other than A496
    and A706.

4.09 (11/23/2010):
    Enable resizing of Setup table columns.
    Add Mixed Table and Joist Table edit to Setup tab

4.10 (12/12/2010):
    Improve Dialog box method validate_spacing() to allow trailing commas.
    A trailing comma ensures Entry value will be returned as a string.

4.12 (12/20/2010):
    Set attribute WorkpointSlopeDistance for bent round bars. Add code to
    work in SDS/2 version 7.226.

4.11 (12/30/2010):
    Enable up to 11 anchor hole columns.

4.13 (01/16/11):
    Add code to display whether piecemark is user or system in dialog box

4.14 (03/01/11):
    Add/modify code to enable metric units.
    The parsing of "Mixed Anchors" spacings was improved.
    Spacings can now be entered like this: "1-2 1/4,6in,350,600mm".
    Enable named colors - requires OptionDlg version 3.05.
    Remove references to self.AnchorDataDict, keep self.AnchorDataDict1
    Set geometry of color dialog to follow main dialog.
    Add named colors cascade menu to color widget context menus.
    Set bg and fg to material color and reverse color in material color
    widgets.
    Validate color values using function isValidColTup in 'Always' rule.
    Allow for imperial/metric DBA/rebar sizes as a function of grade:
        Imperial grades - All except 400R, 300W, 400W, 500W and grades
                          ending in 'M' (ex. A496M, A706M)
        Metric grades #1 - Grades ending in 'M' (ex. A496M, A706M)
        Metric Grades #2 - 400R, 300E, 400W, 500W

        Warning:
            Do not use Canadian grades in imperial units (400R, 300W,
            400W, 500W)!!
        
          Canadian Sizes (400R, 300W, 400W, 500W)
        ###########################################
        Metric Bar Size     Nominal Dia (mm)
            10M                 11.3
            15M                 16.0
            20M                 19.5
            25M                 25.2
            30M                 29.9
            35M                 35.7
            45M                 43.7
            55M                 56.4

                    US Sizes
        ############################################
        Imperial    Soft Metric     Nominal Dia (mm)
        #3  3/8         10M         0.375 (9.525)
        #4  1/2         13M         0.500 (12.7)
        #5  5/8         16M         0.625 (15.875)
        #6  3/4         19M         0.750 (19.05)
        #7  7/8         22M         0.875 (22.225)
        #8  1in         25M         1.000 (25.4)
        #9  1 1/8       29M         1.128 (28.65)
        #10  1 1/4      32M         1.270 (32.26)
        #11  1 3/8      36M         1.410 (35.81)
        #12  1 1/2      40M         1.500 (38.1)
        #14  1 3/4      43M         1.693 (43)
        #18  2 1/4      57M         2.257 (57.33)
          
        Sizes are NOT converted to nominal diameters
"""
# startup code begin
import os
from math import *

from dialog import Dialog, ResponseNotOK
from dialog.frame import Frame
from dialog.combobox import Combobox
from dialog.dimension import DimensionEntry, DimensionStyled, IsValidDimension

import model as SDSmodel
import Transform3D

from MemberBase import *
from Point3D import *
from StateAccessor import StateAccessor
from Layout3D import Layout3D

from param import *
from shape import Shape
from point import Point, PointLocate
from member import Member, MemberLocate, MembersSelected
from hole_add import Hole
from shr_stud import ShrStud
from job import Job, ProcessJob, ProcessOneMem
from fab import Fabricator
from rect_plate import RectPlate
from rnd_bar import RndBar
from view import View

from macrolib.FileDefaults import import_data, export_data
from macrolib.MemSelection import mem_select
from macrolib.P3D import *
from macrolib.highlight_points import add_cc, remove_cc
from macrolib.ExceptWarn import formatExceptionInfo
from macrolib.OptionDlg import OptionDlg, MultiOptionDlg
from macrolib.OptionDlg import Warning as Warn, ColorSelect, validColTup

import EmbedPLDialog
import EmbedPL_XMLParser

Units("feet")
# startup code end

code_version = '4.14'
epsilon = 0.00001

#### Initialize Variables #################################################
''' These variables are set to instance variables in class EmbedPL'''
# defaults file path
default_file_path = os.path.join(os.path.dirname(__file__), "Defaults")
# defaults file name
def_file = "EmbedPL.txt"
script_name = "EmbedPL_v%s.py" % (code_version)

image_path = os.path.join(os.path.dirname( __file__), "Images")
image_name1 = os.path.join(image_path, "Embed_Plate2.gif")
image_name2 = os.path.join(image_path, "Embed_Plate1.gif")
image_name3 = os.path.join(image_path, "Embed_Plate3.jpg")
image_name4 = os.path.join(image_path, "Embed_Plate4.gif")
image_name5 = os.path.join(image_path, "Plan_small.jpg")

# Items in stud_diaList must have matching entry in XML data file
stud_diaList = ("1/4", "3/8",  "1/2",  "5/8",  "3/4",  "7/8",  "1in",
                       "10mm", "13mm", "16mm", "19mm", "22mm", "25mm")

# All grades except 400R, 300W, 400W, 500W and grades ending with an 'M'
# (A706M, A496M)
dba_diaList = ("3/8",  "1/2",  "5/8",  "3/4",  "7/8",  "1in", "1 1/8",
               "1 1/4", "1 3/8", "1 1/2", "1 3/4", "2 1/4")
# Grades A706M, A496M or any grade ending with an 'M'
dba_diaListM1 = ("10mm", "13mm", "16mm", "19mm", "22mm", "25mm",
                 "29mm", "32mm", "36mm", "40mm", "43mm", "57mm")
# Grade 400R, 300W, 400W, 500W
dba_diaListM2 = ("10", "15", "20", "25", "30", "35", "45", "55")

finishList = ("None", "Red Oxide", "Yellow Zinc", "Gray Oxide",
              "Sandblasted", "Blued Steel", "Galvanized")

dbaTypeList = ['Straight', 'Square Hook', 'J Hook']
dbaGradeList = Job().steel_grades("Plate").keys()

holeTypeList = ("Standard Round", "Short Slot", "Oversized round",
                "Long Slot", "Anchor Bolt Hole", "Cope Hole",
                "Erection Pin Hole", "Plug Weld Hole")

boltTypeList = Job().bolt_sched()

setupDataFile = os.path.join(os.path.dirname(__file__), "EmbedPLData.xml")

memDescription = "EMBED PLATE"

dbaDescrDict = {"A706": ("Rebar", '"#%sREBAR" % (int(dim(diam)*8))',
                         '"REBAR%smm" % DimensionStyled()(diam)'),
                "A706M": ("Rebar", '"#%sREBAR" % (int(round(dim(diam), 0)*8))',
                          '"REBAR%sM" % DimensionStyled()(diam)'),
                "400R": ("Rebar", '"#%sREBAR" % (int(round(dim(diam), 0)*8))',
                          '"REBAR%sM" % DimensionStyled()(diam)'),
                "300W": ("Rebar", '"#%sREBAR" % (int(round(dim(diam), 0)*8))',
                          '"REBAR%sM" % DimensionStyled()(diam)'),
                "400W": ("Rebar", '"#%sREBAR" % (int(round(dim(diam), 0)*8))',
                          '"REBAR%sM" % DimensionStyled()(diam)'),
                "500W": ("Rebar", '"#%sREBAR" % (int(round(dim(diam), 0)*8))',
                          '"REBAR%sM" % DimensionStyled()(diam)'),
                "A496": ("DBA", '"DBA%s" % (diam)',
                         '"DBA%sM" % DimensionStyled()(diam)'),
                "A496M": ("DBA", '"DBA%s" % (diam)',
                          '"DBA%sM" % DimensionStyled()(diam)'),
                "A36": ("Smooth Dowel", 'None', 'None'),
                "A572-50": ("Smooth Dowel", 'None', 'None')}

###########################################################################

def pt3DToPoint(point):
    ''' Convert a Point3D or Pt3D to a Point object'''
    return Point(point.x, point.y, point.z)

# List of variables to save to disk
varSaveList = ['axis_rotation',
               'nailer_holes',
               'embed_plan_rotation',
               'embed_vertical_offset',
               'nailer_edge_dist',
               'nailer_hole_size',
               'option',
               'plate_color',
               'plate_finish',
               'plate_depth',
               'plate_grade',
               'plate_length',
               'plate_seq',
               'plate_thk',
               'stud_finish',
               'stud_color',
               'stud_diam',
               'stud_length',
               'which_end',
               'x_off',
               'z_off',
               'brgPl_dist',
               'studCols',
               'studRows',
               'studXSpa',
               'studZSpa',
               'dbaCols',
               'dbaRows',
               'dbaXSpa',
               'dbaZSpa',
               'dbaType',
               'dbaDiam',
               'dbaLength',
               'dbaHook',
               'dbaGrade',
               'dbaZRot',
               'holeCols',
               'holeRows',
               'holeXSpa',
               'holeZSpa',
               'boltSize',
               'holeSize',
               'boltType',
               'holeType',
               'slotLength',
               'slotRot',
               'anchorType',
               'anchorCols',
               'anchorRows',
               'anchorColSpa',
               'anchorRowSpa',
               'anchorPatt',
               'rotateAltDBAs',
               'memDescription']
#'member_version',

class EmbedPL(StateAccessor, MemberBase):
    '''
NOTE: See version notes for latest information and capabilities.
Add embedded plates with studs for beam connections to concrete foundation
or shear walls, for beam and joist bearing plates, or for Misc Rectangular
Plate members. The location can be set by selecting a beam or joist member
or by picking the member end points. 

Suggested model orientation is plan view for selecting point locations or
any orientation when selecting or preselecting a member. The user enters
the embedded plate plan rotation when selecting a member for reference or
selecting a reference point. For a plan rotation of 0.0 degrees, the
member line will be from left to right, the plate thickness will be below
the member line, and the studs will be pointing toward the bottom of the
screen. For a plan rotation of 180.0 degrees, the member line will be
from right to left, the plate thickness will be above the member line,
and the studs will be pointing toward the top of the screen. User can
enter an X axis rotation. The studs point UP with an axis rotation of
-90 and down with an axis rotation of 90.

Studs will be applied to the plate material NS face.

Nailer holes can be added in opposite corners or all corners [0,2,4].

Default embedded plate sizes and member piece marks can determined by
option 'XML Data' (dictionary EmbedPL.xmlDoc.plateinfo is accessed, default
values are based on member nominal depth) or option 'Last values used'.
This is only valid if a reference member is selected. The reference member
can be a Joist or Beam.

The center point on the length of the custom member is calculated and
kept.

Custom member data is serialized to disk. The file extension of the
data file is 'extra'. Each custom member file will have a companion
'extra' file.

Defaults data is also saved to disk. The defaults are saved in
directory plugins/EmbedPL/Defaults. Images are stored in directory
plugins/EmbedPL/Images. The defaults file can be edited to change
default values.

You can enter a Embed PL using these options:
Preselected member for reference
Select a member for reference
Select a member for reference, set location as a bearing plate
Select a center WP
Select the two end points

You can do these things with an existing Embed PL:
Copy
Stretch member ends (edit to update)
Move (process or edit to update)
Change elevation
Change slope
Change plan rotation
Change the length (the center point is maintained)

Default Infomation
    Initial screen options:
        Preselected member -
            Accept a preselected Beam or Joist member to determine
            reference point locating the member center point in plan.
        Select member -
            Select a Beam or Joist member to determine reference point
            locating the member center point in plan.
        Select member, bearing plate -
            Select a Beam or Joist member to determine reference point
            locating the member center point in plan. Set variables for
            member to act as a bearing plate
        Select Embed PL end points -
            Pick member line end points
        Select reference point -
            Pick a reference point locating the member center point in plan
        Exit
    
    Vertical embedded plate offset: self.embed_vertical_offset
    Which end of memRef ["Left End", "Right End"]: self.which_end
    Member sequence - must be a string: self.plate_seq
    Distance from end of Beam/Joist member to EmbedPL member line

    Stud Information
        Stud diameter ("1/4", "3/8", "1/2", "5/8", "3/4", "7/8", "1"):
            self.stud_diam
        self.stud_length
        self.stud_finish
        self.stud_color
        self.studCols
        self.studRows
        Stud spacing along custom member X-axis: self.studXSpa
        Stud spacing along custom member Y-axis: self.studZSpa

    DBA Information
        Type ['Straight', 'Square Hook', 'J Hook']:
            self.dbaType
        DBA diameter ("1/4", "3/8", "1/2", "5/8", "3/4", "7/8", "1"):
            self.dbaDiam
        self.dbaLength
        self.dbaHook
        self.dbaGrade
        self.dbaZRot for hooked DBAs
        self.dbaCols
        self.dbaRows
        self.dbaXSpa
        self.dbaZSpa
        self.stud_finish - Common with studs
        self.stud_color - Common with studs

    Hole Information
        holeCols
        holeRows
        holeXSpa
        holeZSpa
        boltSize
        holeSize - Enter 0 for SDS/2 to calculate hole size
        boltType - Job().bolt_sched()
        holeType - ("Standard Round", "Short Slot", "Oversized Round",
                    "Long Slot", "Anchor Bolt Hole")
        slotLength - Enter 0 for SDS/2 to calculate long slot length
        slotRot
        
    Stud/DBA/Hole pattern offsets
        Pattern offset X direction: self.x_off
        Pattern offset Y direction: self.z_off
        
    Plate Information
        self.plate_length
        self.plate_depth
        self.plate_thk
        self.plate_finish
        self.plate_color
    Nailer Holes: (0, 2, 4)
        0 = none,
        2 = opposite corners,
        4 = each corner (integer)
        self.nailer_holes (0,2,4)
        Nailer hole edge distance: self.nailer_edge_dist
        Nailer hole size: self.nailer_hole_size

    Custom Member Plan Rotation: self.embed_plan_rotation
    Custom Member X Axis Rotation: self.axis_rotation
    Main Material Grade: self.plate_grade
        Job().steel_grades("Plate").keys()

    Access dictionary self.xmlDoc.plateinfo for self.studCols,
    self.studRows, self.plate_length, self.plate_depth,
    self.plate_thk, self.studXSpa, self.studZSpa, and
    self.mark_prefix as a function of self.memRef.nom_depth
        self.func_data_or_last = func_data_or_last

    Custom member piecemark prefix: self.mark_prefix
    '''
    xmlDoc = EmbedPL_XMLParser.XMLParser(setupDataFile,
                                         'EmbedPLData',
                                         'setupinfo')
    mark_prefix = xmlDoc.setupinfo['mark_prefix']
    _version = 1
    _arguments = {}
    _arguments[0] = (
        ('memRef', None),
        ('mark_prefix', mark_prefix),
        ('existed', False),
        ('option', "Select reference point"),
        ('leftWP', Point3D(0,0,0)),
        ('rightWP', Point3D(0,0,0)),
        ('ctrPT', Point3D(0,0,0)),
        ('embed_vertical_offset', 3.0),
        ('which_end', "Left End"),
        ('plate_seq', Job().sequences()[-1]),
        ('stud_diam', 0.75),
        ('stud_length', 6.0),
        ('stud_finish', "None"),
        ('stud_color', "255,255,0"),
        ('studCols', 2),
        ('studRows', 2),
        ('plate_length', 12.0),
        ('plate_depth', 18.0),
        ('plate_thk', 0.5),
        ('plate_finish', "None"),
        ('plate_color', "120,120,120"),
        ('x_off', 0.0),
        ('z_off', 0.0),
        ('studXSpa', 6.0),
        ('studZSpa', 8.0),
        ('nailer_holes', 2),
        ('nailer_edge_dist', 0.75),
        ('nailer_hole_size', 0.5625),
        ('embed_plan_rotation', 0.0),
        ('embed_slope', 0.0),
        ('axis_rotation', 0.0),
        ('plate_grade', Job().steel_grades("Plate").keys()[0]),
        ('brgPl_dist', 0.5),
        ('dbaCols', 1),
        ('dbaRows', 3),
        ('dbaXSpa', 6.0),
        ('dbaZSpa', 6.0),
        ('dbaType', 'Straight'),
        ('dbaDiam', '1/2'),
        ('dbaLength', 12.0),
        ('dbaHook', 3.0),
        ('dbaGrade', Job().steel_grades("Plate").keys()[-1]),
        ('dbaZRot', 90),
        ('holeCols', 0),
        ('holeRows', 0),
        ('holeXSpa', 5.5),
        ('holeZSpa', 5.5),
        ('boltSize', 0.75),
        ('holeSize', 0.8125),
        ('boltType', Job().bolt_sched()[0]),
        ('holeType', "Anchor Bolt Hole"),
        ('slotLength', 0.0),
        ('slotRot', 0.0))

    _arguments[1] = _arguments[0] + \
        (('anchorType', 'Studs, DBAs, Holes'),
         ('anchorCols', 2),
         ('anchorRows', 3),
         ('anchorColSpa', '8'),
         ('anchorRowSpa', '8'),
         ('anchorPatt', 'dd,ss,ss'),
         ('rotateAltDBAs', 'No'),
         ('member_version', 1))
    # Warn("\n".join([str(item) for item in _arguments[1]]))

    def __init__(self, *args, **kw):
        Units("feet")
        self.existed = False
        StateAccessor.__init__(self, *args, **kw)
        MemberBase.__init__(self)
        self.SetMemberType("EmbedPL")
        self.memRef = None
        self.option = "Select reference point"
        self.ccList = []

        '''
        Initialize module constants for use in Dialog Box and saving and
        retrieving default values'''
        for attr in ['default_file_path',
                     'def_file',
                     'script_name',
                     'image_path',
                     'image_name1',
                     'image_name2',
                     'image_name3',
                     'image_name4',
                     'image_name5',
                     'stud_diaList',
                     'dba_diaList',
                     'dba_diaListM1',
                     'dba_diaListM2',
                     'finishList',
                     'dbaTypeList',
                     'dbaGradeList',
                     'holeTypeList',
                     'boltTypeList',
                     'memDescription']:
            setattr(self, attr, eval(attr))

        ## Initialize setup data to be retrieved from XML file
        self._initializeXMLdata()

        ## Initialize instance variables ##################################
        self.embed_elev = 0.0
        self.axis_rotation = 0.0
        ###################################################################
        ## Import defaults if default file exists
        dd0 = import_data(os.path.join(default_file_path, def_file))
        if dd0:
            for key in dd0:
                setattr(self, key, dd0[key])
            '''
            Default values must be formatted for ComboBox or StrEntry
            since import_data() will type cast to integer, float, float
            from a fraction (ex. 1/2), or list object where possible. '''
            if isinstance(self.stud_diam, (int, float)):
                self.stud_diam = dim_print(dim(self.stud_diam))
            if isinstance(self.dbaDiam, (int, float)):
                self.dbaDiam = dim_print(dim(self.dbaDiam))
            self.embed_plan_rotation = float(self.embed_plan_rotation)
            self.plate_seq = str(self.plate_seq)
            self.anchorColSpa = str(self.anchorColSpa)
            self.anchorRowSpa = str(self.anchorRowSpa)

        ###################################################################
        '''
        self.plate_seq is originaly assigned by StateAccessor. If defaults
        file has an invalid value for sequence, reassign to
        Job().sequences()[0]'''
        if self.plate_seq not in Job().sequences():
            self.plate_seq = Job().sequences()[0]
        '''
        If named colors saved in defaults file do not exist in job, set
        color variables to the format "xx,xx,xx" where "xx" is an integer
        between 0 and 255.
        '''
        for attr, color in (("plate_color", (80,80,80)), ("stud_color", (255,255,0))):
            v = validColTup(getattr(self, attr), color)
            if isinstance(v, tuple):
                setattr(self, attr, ",".join(map(str, v)))
        
        self.version_vars()
        # Existing member data is read from disc after __init__() is executed

    def version_vars(self):
        if self.member_version == 0:
            self.rotateAltDBAs = 'No'
            self.anchorType = 'Studs, DBAs, Holes'
            self.anchorTypeList = ['Studs, DBAs, Holes',]
        elif self.member_version == 1:
            self.anchorTypeList = ['Studs, DBAs, Holes', 'Mixed Anchors',
                                   'Anchor Holes', 'Plain']
        if self.anchorType == 'Studs and DBAs':
            self.anchorType = "Mixed Anchors"

    def __setstate__(self, args):
        # Warn("__setstate__")
        self.member_version = args[1]
        self.version_vars()
        # Warn(str(type(self.member_version)))
        return StateAccessor.__setstate__(self, args)

    def __getstate__(self):
        self.version_vars()
        self.member_version = StateAccessor.__getstate__(self)[1]
        # Warn("Version written to disc: %s" % (p[1]))
        # Warn("self.existed written to disc: %s" % (p[4]))
        return StateAccessor.__getstate__(self)
    
    def _initializeXMLdata(self):
        # Warning("Initializing XML")
        # Get setup options from setup file
        # func_data_or_last, mark_prefix
        self.xmlDoc = EmbedPL_XMLParser.XMLParser(setupDataFile,
                                                  'EmbedPLData',
                                                  'setupinfo',
                                                  'DialogData',
                                                  ('studinfo', 'stud_diam'),
                                                  ('plateinfo', 'nom_depth'),
                                                  ('anchordata', 'depth'),
                                                  ('jstanchordata', 'series'))

        # Convert keys of self.xmlDoc.anchordata to integer and assign to 
        # dictionary
        self.AnchorDataDict1 = dict(zip([int(s) for s in self.xmlDoc.anchordata.keys()],
                                        self.xmlDoc.anchordata.values()))
        # Validate patt for each dict in self.AnchorDataDict1
        for key in self.AnchorDataDict1:
            patt = self.AnchorDataDict1[key]['patt']
            v = self.validate_patt(patt)
            if not v:
                raise TypeError, "Invalid XML data"
            else:
                self.AnchorDataDict1[key]['patt'] = (v, patt)

        # Modify code_version and _version XML data tag text elements
        self.xmlDoc.updateDataChanges('code_version', code_version)
        self.xmlDoc.updateDataChanges('_version', EmbedPL._version)
        self.code_version = code_version
        self._version = EmbedPL._version
        
        for key in self.xmlDoc.setupinfo:
            setattr(self, key, self.xmlDoc.setupinfo[key])
            
        for key in self.xmlDoc.DialogData:
            setattr(self, key, self.xmlDoc.DialogData[key])

        # Convert keys of self.xmlDoc.plateinfo to integer
        self.plateinfo = dict(zip([int(s) for s in self.xmlDoc.plateinfo.keys()],
                                  self.xmlDoc.plateinfo.values()))
        
    def _savewindow(self, dlg, attr):
        nodeList = self.xmlDoc.getElemsByTagName('DialogData')
        setattr(self, attr, dlg.window.geometry())
        # if getattr(self, attr) != dlg.window.geometry():
        # Warning("Saving %s (%s) dialog box information." % (attr, dlg.window.geometry()))
        self.xmlDoc.setAttrValue(nodeList, attr, getattr(self, attr))

    def _savesetup(self, attr, newValue):
        nodeList = self.xmlDoc.getElemsByTagName('setupinfo')
        self.xmlDoc.setAttrValue(nodeList, attr, newValue)

    def _writesetup(self):
        # Warning("Writing XML data")
        self.xmlDoc.writeXML(setupDataFile)

    def _saveinfo(self, keyWord, keyValueList, optionDict):
        # Ensure all elements of keyValueList are str objects
        keyValueList = map(str, keyValueList)
        dd = {'stud_diam': [str, 'studinfo'],
              'nom_depth': [int, 'plateinfo'],
              'depth':     [int, 'anchordata'],
              'series':    [str, 'jstanchordata']}
        nodeList = self.xmlDoc.getElemsByTagName(dd[keyWord][1])
        nodeListFiltered = []
        for node in nodeList:
            if node.hasAttribute(keyWord) and node.getAttribute(keyWord) in keyValueList:
                nodeListFiltered.append(node)
        for node in nodeListFiltered:
            for attr, value in optionDict[dd[keyWord][0](node.getAttribute(keyWord))].items():
                self.xmlDoc.setAttrValue(node, attr, str(value))
                # print "Setting %s: %s - %s" % (node.getAttribute("nom_depth"), attr, value)
        # print self.xmlDoc.doc.toprettyxml(indent="  ", newl="")
        self.xmlDoc.writeXML(setupDataFile)
        self._initializeXMLdata()

    def validate_patt(self, value):
        # argument 'value' must be in the format 'ddd,sss,s-s,sss,h-h'
        # 'd' or 'D' denotes DBA, 's' or 'S' denotes stud,
        # 'h' or 'H' denotes hole, '-' denotes no anchor
        # Ver 4.02 removed strip() in str(value).strip().split(',')
        try:
            valueList = [list(item) for item in str(value).split(',')]
            for i, item in enumerate(valueList):
                for j, s in enumerate(item):
                    if s.lower() not in ['s','d', '-', 'h']:
                        valueList[i,j] = "-"
        except Exception, e:
            Warning(str(e))
            return []
        return valueList

    def Add(self):
        Units("feet")
        #################################
        ## For SDS/2 Version 7.226
        self.existed = False
        #################################
        # sets self.option transparently
        if not self.optionDialog():
            return
        ''' Options:
        "Preselected member",
        "Select member",
        "Select member, bearing plate",
        "Select Embed PL end points",
        "Select reference point",
        "Edit setup data",
        "Exit"'''
        if self.option == "Preselected member":
            # self.memRef is set in optionDialog()
            self.embed_slope = 0
        elif self.option in ["Select member", "Select member, bearing plate"]:
            memList = mem_select("Select a Beam or Joist member or RETURN",
                                 ['Beam', 'Joist'], ['All',], single=True,
                                 all_mks=False)
            if memList:
                self.memRef = memList[0]
                SelectionAdd(self.memRef)
                self.embed_slope = 0
            else:
                Warning("No member was selected")
                ClearSelection()
                self._writesetup()
                return
        elif self.option == "Select Embed PL end points":
            leftWP, rightWP = None, None
            leftWP = PointLocate("Locate Member Point 1")
            if leftWP != None:
                self.ccList.append(add_cc(leftWP, 1, 'Magenta'))
                rightWP = PointLocate("Locate Member Point 2", leftWP)
                if rightWP != None:
                    self.ccList.append(add_cc(rightWP, 1, 'Magenta'))
                    if leftWP.dist(rightWP) < 0.25:
                        Warning("The embed is too short. OK to exit.")
                        remove_cc(self.ccList)
                        self._writesetup()
                        return
            if None in [leftWP, rightWP]:
                remove_cc(self.ccList)
                self._writesetup()
                return
            self.leftWP, self.rightWP = leftWP, rightWP
            self.ctrPT = midPt(leftWP, rightWP)
            self.embed_elev = self.ctrPT.z
            self.memRef = None
            self.plate_length = self.leftWP.dist(self.rightWP)
            embed_slope, embed_plan_rotation = self.memRotation(rightWP,
                                                                leftWP)
            self.embed_slope = degrees(embed_slope)
            self.embed_plan_rotation = degrees(embed_plan_rotation)
            ###########################################################
            ###########################################################
            '''Following code required using SDS/2 version 7.226'''
            self.SetLeftLocation(Point3D(self.leftWP))
            self.SetRightLocation(Point3D(self.rightWP))
            ###########################################################
            ###########################################################
            
        elif self.option == "Select reference point":
            ctrPT = PointLocate("Locate embed CENTER WP")
            if ctrPT != None:
                self.ccList.append(add_cc(ctrPT, 1, 'Magenta'))
                self.memRef = None
                self.ctrPT = ctrPT
                self.embed_elev = self.ctrPT.z
                self.embed_slope = 0
                ###########################################################
                ###########################################################
                '''Following code required using SDS/2 version 7.226'''
                self.leftWP = Point3D(self.ctrPT+SPt3D(-self.plate_length/2,
                                                       radians(-self.embed_slope)+pi/2,
                                                       radians(self.embed_plan_rotation)).toPt3D())
                self.rightWP = Point3D(self.ctrPT+SPt3D(self.plate_length/2,
                                                        radians(-self.embed_slope)+pi/2,
                                                        radians(self.embed_plan_rotation)).toPt3D())
                self.SetLeftLocation(Point3D(self.leftWP))
                self.SetRightLocation(Point3D(self.rightWP))
                ###########################################################
                ###########################################################
            else:
                self._writesetup()
                return
        elif self.option == "Edit setup data":
            d = EmbedPLDialog.EmbedDialog(self)
            try:
                dlg1 = d.get()
                dlg1.done()
                self._savewindow(dlg1, 'mainDlgPos')
            except ResponseNotOK:
                pass
            self._writesetup()
            return
        elif self.option == "Exit":
            self._writesetup()
            return

        remove_cc(self.ccList)
        self.ccList = []

        if self.func_data_or_last == 'XML Data' and self.memRef and \
           self.option != "Select member, bearing plate":
            
            # Assign plate dimensions from setup data if self.memRef a Beam
            if self.memRef.type == "Beam":
                for key, value in self.embed_plate_dims(self.memRef).items():
                    setattr(self, key, value)
                    
            if self.AnchorDataDict1 and self.memRef.type == "Beam":
                d = self.memRef.nom_depth
                if d in self.AnchorDataDict1:
                    setattr(self, 'anchorCols', len(self.AnchorDataDict1[d]['patt'][0][0]))
                    setattr(self, 'anchorRows', len(self.AnchorDataDict1[d]['patt'][0]))
                    setattr(self, 'anchorPatt', self.AnchorDataDict1[d]['patt'][1])
                    for key in ['anchorColSpa', 'anchorRowSpa']:
                        setattr(self, key, str(self.AnchorDataDict1[d][key]))

            elif self.AnchorDataDict1 and self.memRef.type == "Joist":
                if self.memRef.series in self.xmlDoc.jstanchordata:
                    for attr in ('anchorColSpa','anchorRowSpa','anchorPatt',
                                 'plate_length','plate_depth','plate_thk',
                                 'dbaCols','dbaRows','dbaXSpa','dbaZSpa',
                                 'studCols','studRows','studXSpa','studZSpa'):
                        setattr(self, attr, self.xmlDoc.jstanchordata[self.memRef.series][attr])
                    v = self.validate_patt(self.anchorPatt)
                    if not v:
                        raise TypeError, "Invalid XML data"
                    else:
                        setattr(self, 'anchorCols', len(v[0]))
                        setattr(self, 'anchorRows', len(v))
            
        self.mem = Member(self.GetMemberNumber())
        EmbedPLDialog.MemberAttrController("ErectionSequence").Set(self, str(self.plate_seq))
        EmbedPLDialog.MemberAttrController("description").Set(self, self.memDescription)
        EmbedPLDialog.MemberAttrController("IsExisting").Set(self, "No")

        return True

    def Edit(self):
        Units("feet")
        if self.anchorType == 'Studs and DBAs':
            self.anchorType = "Mixed Anchors"

        self.mem = Member(self.GetMemberNumber())
        
        if self.member_version != EmbedPL._version and self.existed:
            s = "This member was created with EmbedPL._version %s" % (self.member_version)
            s += "\nand will be updated to EmbedPL._version %s" % (EmbedPL._version)
            s += "\nDo you want to continue?"
            a = OptionDlg(s, ["Continue", "EXIT"], btnWidth=10, columns=2,
                          title="EmbedPL._version", parent=None)
            if a.value == "EXIT":
                return
            
        if self.existed:
            #Calculate slope, plan rotation, plate length, center point
            #Point objects cannot be pickled
            self.leftWP = Point3D(self.mem.left.location)
            self.rightWP = Point3D(self.mem.right.location)
            self.ctrPT = Point3D(midPt(self.leftWP, self.rightWP))
            self.embed_elev = self.ctrPT.z
            self.OLD_embed_elev = self.embed_elev
            self.plate_length = self.leftWP.Distance(self.rightWP)
            embed_slope, embed_plan_rotation = self.memRotation(self.rightWP,
                                                                self.leftWP)
            self.embed_slope = degrees(embed_slope)
            self.embed_plan_rotation = degrees(embed_plan_rotation)

        # Set stud display strings for dialog box
        self.setStudInfo(self.stud_diam)
        
        # Model attributes are modified transparently by dialog box
        d = EmbedPLDialog.EmbedDialog(self)
        try:
            dlg1 = d.get()
            if dlg1.Run():
                # save window info cannot be done until method Run() is called
                self._savewindow(dlg1, 'mainDlgPos')
                
                # Prepare to export varSaveList values to disk file
                dd1 = {}
                # plate_seq is indirectly controlled by MemberAttrController
                self.plate_seq = self.mem.ErectionSequence
                # memDescription is indirectly controlled by MemberAttrController
                self.memDescription = self.mem.description
                for var in varSaveList:
                    value = getattr(self, var, None)
                    if not value is None:
                        dd1[var] = value
                export_data(os.path.join(default_file_path, def_file),
                            dd1, script_name, 'ts')
                self._writesetup()
            else:
                ClearSelection()
                remove_cc(self.ccList)
                self._savewindow(dlg1, 'mainDlgPos')
                self._writesetup()
                return False
            
        except Exception, e:
            ClearSelection()
            Warning(formatExceptionInfo())
            remove_cc(self.ccList)
            self._writesetup()
            return False

        # Calculate member WPs if new member
        if self.option in ["Preselected member", "Select member"] and self.memRef is not None:
            if self.which_end == "Left End":
                self.ctrPT = Pt3D(self.memRef.left.location)
            elif self.which_end == "Right End":
                self.ctrPT = Pt3D(self.memRef.right.location)
            self.ctrPT.z += self.embed_vertical_offset
            self.embed_elev = self.ctrPT.z
            self.OLD_embed_elev = self.embed_elev
            
        elif self.option == "Select member, bearing plate" and self.memRef is not None:
            if self.memRef.type == "Joist":
                brgDepth = self.memRef.brg_depth
            elif self.memRef.type == "Beam":
                brgDepth = self.memRef.depth
                
            if self.which_end == "Left End":
                self.ctrPT = Pt3D(self.memRef.left.location) + \
                             self.memRef.translate(self.brgPl_dist,
                                                 -brgDepth, 0.0)
            elif self.which_end == "Right End":
                self.ctrPT = Pt3D(self.memRef.right.location) + \
                             self.memRef.translate(-self.brgPl_dist,
                                                 -brgDepth, 0.0)
                
            self.ctrPT.z += self.embed_vertical_offset
            self.embed_elev = self.ctrPT.z
            self.OLD_embed_elev = self.embed_elev
            
        elif self.option == "Select reference point" and not self.existed:
            self.ctrPT.z += self.embed_vertical_offset
            self.embed_elev = self.ctrPT.z
            self.OLD_embed_elev = self.embed_elev
            
        elif self.option == "Select Embed PL end points" and not self.existed:
            self.ctrPT = midPt(self.leftWP, self.rightWP)
            self.embed_elev = self.ctrPT.z
            self.OLD_embed_elev = self.embed_elev
        
        self.ctrPT = Point3D(self.ctrPT)
        self.ctrPT.z = self.embed_elev
        self.leftWP = Point3D(self.ctrPT+SPt3D(-self.plate_length/2,
                                               radians(-self.embed_slope)+pi/2,
                                               radians(self.embed_plan_rotation)).toPt3D())
        self.rightWP = Point3D(self.ctrPT+SPt3D(self.plate_length/2,
                                                radians(-self.embed_slope)+pi/2,
                                                radians(self.embed_plan_rotation)).toPt3D())

        self.SetLeftLocation(self.leftWP)
        self.SetRightLocation(self.rightWP)
        self.SetRotation(radians(self.axis_rotation))
        self.SetColumnOrientation()
        self.memRef = None
        remove_cc(self.ccList)
        if self.option != "Preselected member":
            ClearSelection()
        # If True, SDS/2 sees the member as changed
        return Member(self.member_number).model_complete == 'NOT SET'
    '''
    def Design(self):
        return True
    
    def Hash(self):
        return True'''

    def CreateMaterial( self ):
        Units("feet")
        self.SetPiecemarkPrefix(self.mark_prefix)
        # Add rectangular plate material to member as main material
        rp1 = self.add_rect_plate(pt3DToPoint(self.GetLeftLocation()),
                                  pt3DToPoint(self.GetRightLocation()),
                                  self.plate_length,
                                  self.plate_depth,
                                  self.plate_thk,
                                  self.plate_grade,
                                  self.plate_finish,
                                  self.plate_color)
        self.rp1 = rp1
        
        # Add nailer holes
        if self.nailer_holes in [2, 4]:
            ptWP3 = pt3DToPoint(self.GetLeftLocation()) + \
                    rp1.translate(0.0, -self.plate_depth, 0.0)
            ptWP4 = pt3DToPoint(self.GetRightLocation()) + \
                    rp1.translate(0.0, -self.plate_depth, 0.0)
            self.add_nlr_holes(rp1, pt3DToPoint(self.GetLeftLocation()),
                               self.nailer_edge_dist, "Below Right",
                               self.nailer_hole_size)
            self.add_nlr_holes(rp1, ptWP4, self.nailer_edge_dist, "Above Left",
                               self.nailer_hole_size)
        if self.nailer_holes == 4:
            self.add_nlr_holes(rp1, ptWP3, self.nailer_edge_dist,
                               "Above Right", self.nailer_hole_size)
            self.add_nlr_holes(rp1, pt3DToPoint(self.GetRightLocation()),
                               self.nailer_edge_dist, "Below Left",
                               self.nailer_hole_size)

        # Set stud dimensions
        dd = self.stud_dim(self.stud_diam)
        for key in dd:
            setattr(self, key, dd[key])

        action = getattr(self, 'anchorType', 'Studs, DBAs, Holes')

        if action == 'Studs, DBAs, Holes':
            # Add studs
            first_dist_horiz = ((self.plate_length-self.studXSpa * \
                                 (self.studCols-1))/2)+self.x_off
            first_dist_vert = ((self.plate_depth-self.studZSpa * \
                                (self.studRows-1))/2)-self.z_off

            firstPT = rp1.pt1 + rp1.translate(first_dist_horiz,
                                              -first_dist_vert,
                                              self.plate_thk)
            x_dist = 0.0
            for i in range(self.studCols):
                z_dist = 0.0
                x_dist = i*self.studXSpa
                for j in range(self.studRows):
                    z_dist = j*self.studZSpa
                    ptWP = firstPT + rp1.translate(x_dist, -z_dist, 0.0)
                    self.apply_stud(ptWP, self.stud_length, self.stud_diam,
                                    self.head_thk, self.head_diam,
                                    self.stud_finish, self.stud_color)

            # Add DBAs
            first_dist_horiz = ((self.plate_length - \
                                 self.dbaXSpa*(self.dbaCols-1))/2) + self.x_off
            first_dist_vert = ((self.plate_depth - \
                                self.dbaZSpa*(self.dbaRows-1))/2) - self.z_off

            firstPT = rp1.pt1 + rp1.translate(first_dist_horiz,
                                              -first_dist_vert,
                                              self.plate_thk)
            x_dist = 0.0
            for i in range(self.dbaCols):
                z_dist = 0.0
                x_dist = i*self.dbaXSpa
                for j in range(self.dbaRows):
                    if j%2 and getattr(self, 'rotateAltDBAs', 'No') == 'Yes':
                        DBArotation = self.dbaZRot+180.0
                    else:
                        DBArotation = self.dbaZRot
                    z_dist = j*self.dbaZSpa
                    ptWP = firstPT + rp1.translate(x_dist, -z_dist, 0.0)
                    # NOTE - Material grade "A496" should exist
                    self.apply_DBA(ptWP, self.dbaLength, self.dbaDiam,
                                   self.stud_finish, self.stud_color,
                                   self.dbaType, self.dbaHook,self.dbaGrade,
                                   DBArotation)
        elif action == 'Mixed Anchors':
            '''
            self.anchor2Darray is created interactively in the dialog box
            and not serialized with other member data. To enable member
            copy, if self not hasattr self.anchor2Darray, create from
            self.anchorPatt which is serialized with other member data.
            '''
            if not hasattr(self, 'anchor2Darray'):
                # initialize array anchorCols anchorRows
                self.anchor2Darray = [["-" for i in range(self.anchorCols)] for j in range(self.anchorRows)]
                # Validate pattern and create 2D list
                anchorPattList = [[c for c in list(s) if c.lower() in ['s', 'd', 'h', '-']] \
                                  for s in self.anchorPatt.strip().split(",") if s]
                for j, row in enumerate(self.anchor2Darray):
                    for i, col in enumerate(row):
                        try:
                            self.anchor2Darray[j][i] = anchorPattList[j][i]
                        except:
                            pass
            '''
            Parse horizontal and vertical spacing strings which were
            validated in the dialog box.
            '''
            horizSpaList = self.parse_spacing(self.anchorColSpa, self.anchorCols)
            horizSpaList.append(0)
            vertSpaList = self.parse_spacing(self.anchorRowSpa, self.anchorRows)
            vertSpaList.append(0)
            
            first_dist_horiz = (self.plate_length-sum(horizSpaList))/2 + self.x_off
            first_dist_vert = (self.plate_depth-sum(vertSpaList))/2 - self.z_off
            firstPT = rp1.pt1 + rp1.translate(first_dist_horiz,
                                              -first_dist_vert,
                                              self.plate_thk)
            x_dist = 0.0
            for i in range(self.anchorCols):
                z_dist = 0.0
                for j in range(self.anchorRows):
                    ptWP = firstPT + rp1.translate(x_dist, -z_dist, 0.0)
                    if self.anchor2Darray[j][i].lower() == 'd':
                        # Add a DBA
                        if j%2 and getattr(self, 'rotateAltDBAs', 'No') == 'Yes':
                            DBArotation = self.dbaZRot+180.0
                        else:
                            DBArotation = self.dbaZRot
                        self.apply_DBA(ptWP,
                                       self.dbaLength,
                                       self.dbaDiam,
                                       self.stud_finish,
                                       self.stud_color,
                                       self.dbaType,
                                       self.dbaHook,
                                       self.dbaGrade,
                                       DBArotation)
                    elif self.anchor2Darray[j][i].lower() == 's':
                        # Add a stud
                        self.apply_stud(ptWP,
                                        self.stud_length,
                                        self.stud_diam,
                                        self.head_thk,
                                        self.head_diam,
                                        self.stud_finish,
                                        self.stud_color)
                    elif self.anchor2Darray[j][i].lower() == 'h':
                        # Add a hole
                        self.add_holes(rp1, ptWP, self.holeXSpa, self.holeZSpa,
                                       1, 1, self.boltSize, self.holeSize,
                                       self.boltType, self.holeType,
                                       self.slotLength, self.slotRot)
                    z_dist += vertSpaList[j]
                x_dist += horizSpaList[i]
                
        if action in ['Studs, DBAs, Holes', 'Anchor Holes']:
            # Add holes
            if self.holeCols > 0 and self.holeRows > 0:
                # reference point of the pattern is the center of the plate,
                # adjusted by offsets
                ptWP = rp1.pt1 + rp1.translate(self.plate_length/2+self.x_off,
                                               -self.plate_depth/2+self.z_off, 0)

                self.add_holes(rp1, ptWP, self.holeXSpa, self.holeZSpa,
                               self.holeCols, self.holeRows, self.boltSize,
                               self.holeSize, self.boltType, self.holeType,
                               self.slotLength, self.slotRot)
        
        # Move user added material if elevation changed
        # Member copy and move skip Edit() which is where self.OLD_embed_elev
        # is assigned.
        self.OLD_embed_elev = getattr(self, 'OLD_embed_elev', self.embed_elev)
        elevDiff = self.embed_elev - self.OLD_embed_elev
        if abs(elevDiff) > epsilon:
            self.move_user_mtrl(elevDiff)
        self.existed = True
        return True

    def user_material(self, mem_num):
        return [i for i, mtrl in enumerate(SDSmodel.member(mem_num).materials) \
                 if not mtrl.sys_gened]

    def transform_mtrl(self, mem_num, idx, transform):
        x, y, z, t = Transform3D.GetXYZT(transform)
        # SetMaterialXform from MemberBase
        SetMaterialXform(mem_num, idx,
                         x.x, x.y, x.z,
                         y.x, y.y, y.z,
                         z.x, z.y, z.z,
                         t.x, t.y, t.z)

    def move_user_mtrl(self, dist):
        n = self.GetMemberNumber()
        Member(n).Update(False)
        m = Transform3D.Transform3D().Translate(Point3D(0., 0., dist))
        for i in self.user_material(n):
            self.transform_mtrl(n,i,Transform3D.MaterialIndexTransform(n,i)*m)

    def parse_spacing(self, s, n):
        resultList = [item.strip() for item in s.split(',') if item.strip()]
        while len(resultList) < n-1:
            resultList.append(resultList[-1])
        if len(resultList) > n-1:
            resultList = resultList[:n-1]
        return [DimensionStyled()(item).Dim for item in resultList]

    def embed_plate_dims(self, mem):
        '''
        Return default number of stud columns, stud rows, embed plate length,
        embed plate depth, embed plate thickness, user_piece_mark. If
        mem.nom_depth is not in the dictionary, return dictionary dd.'''
        vars = ('studCols','studRows','studXSpa','studZSpa','plate_length',
                'plate_depth','plate_thk','mark_prefix')
        dd = dict(zip(vars, [getattr(self,item, None) for item in vars]))
        return self.plateinfo.get(mem.nom_depth, dd)

    def add_rect_plate(self, p1, p2, length, width, thk,
                       grade, finish, color):
        '''
        Add rectangular plate to the custom member'''
        mem = Member(self.GetMemberNumber())
        self.plate = RectPlate()
        self.plate.member = mem
        self.plate.pt1 = p1
        self.plate.pt2 = p2
        self.plate.grade = grade
        self.plate.origin = "FS"
        self.plate.width = width
        self.plate.thick = thk
        self.plate.work_pt_dist = length
        self.plate.setback_left = 0
        self.plate.setback_right = 0
        self.plate.length = length
        self.plate.mtrl_type = "Plate"
        self.plate.mtrl_usage = "EmbedPL"
        self.plate.finish = finish
        self.plate.color = validColTup(color)
        self.plate.ref_pt_offset = (length/2.0,0,0)
        self.plate.mtrl_is_main = "Yes"
        self.plate.add()
        self.plate.rotate(mem, (360,0,0))
        # rectangular plate end
        return self.plate

    def add_nlr_holes (self, mtrl, ref_pt, edge_dist,
                  pattern_orientation, hz):
        '''
        Add nailer holes to the plate material'''
        # hole group add begin
        hl = Hole()
        hl.mtrl = [mtrl, ]
        hl.pt1 = ref_pt
        hl.hole_type = "Standard Round"
        hl.face = "NS Face"
        hl.valid_cnc = "Yes"
        hl.x_ref_offset = edge_dist
        hl.y_ref_offset = edge_dist
        hl.x_spa = 0.0
        hl.y_spa = 0.0
        hl.group_rot = 0.0
        hl.locate = pattern_orientation
        hl.columns = 1
        hl.rows = 1
        hl.bolt_type = "Auto"
        hl.bolt_dia = hz - 0.0625
        hl.hole_dia = hz
        hl.show_window = "No"
        hl.create()
        # hole group add end
        return hl

    def apply_stud(self, pt1, length, diam, head_thk, head_diam,
                   finish, color):
        # shear stud begin
        m1 = ShrStud()
        m1.member = Member(self.GetMemberNumber())
        m1.Point1 = pt1
        m1.Point2 = pt1 + self.rp1.translate(0,0,length)
        m1.stud_dia = DimensionStyled()(diam).Dim
        m1.head_thick = head_thk
        m1.head_dia = head_diam
        m1.length = length
        m1.mtrl_type = "Shear stud"
        m1.mtrl_usage = "EmbedPLStud"
        m1.finish = finish
        m1.color = validColTup(color)
        m1.ref_pt_offset = (0.000000, 0.000000, 0.000000)
        # Cannot set grade of stud material SDS/2 7.208
        # m1.grade = Job().steel_grades("Shear Stud").keys()[0]
        m1.add()
        m1.SetTransform(Transform3D.Transform3D(Point3D(
                            self.rp1.translate(0,0,1)),
                            Point3D(self.rp1.translate(1,0,0)),
                            Point3D(self.rp1.translate(0,1,0)),
                            Point3D(m1.Point1)))
        # shear stud end
        return m1
    
    def apply_DBA(self, pt1, length, diam, finish, color,
                  DBAtype="Straight", hook=3.0, grade='A496',
                  DBArotation=0.0):
        mem = Member(self.GetMemberNumber())
        s1, s2, s3 = dbaDescrDict.get(grade, ("Smooth Dowel", "None", "None"))
        s2 = eval(s2)
        s3 = eval(s3)
        if DBAtype == "Straight":
            rb1 = RndBar()
            rb1.Member = mem
            rb1.Point1 = pt1
            rb1.Point2 = pt1 + self.rp1.translate(0,0,length)
            rb1.Centered = "Yes"
            rb1.BarDiameter = DimensionStyled()(diam).Dim
            rb1.OrderLength = rb1.Point1.dist(rb1.Point2)
            rb1.WorkpointSlopeDistance = rb1.Point1.dist(rb1.Point2)
            rb1.MaterialType = "Round bar"
            rb1.mtrl_usage = s1
            rb1.SurfaceFinish = finish
            rb1.MaterialGrade = grade
            if s2 is not None:
                rb1.ImperialDescription = s2
            if s3 is not None:
                rb1.MetricDescription = s3
            rb1.mtrl_is_main = "No"
            rb1.MaterialColor3d = validColTup(color)
            rb1.ReferencePointOffset = (0,0,0)
            rb1.Add()
            rb1.SetTransform(Transform3D.Transform3D(
                                Point3D(self.rp1.translate(0,0,1)),
                                Point3D(self.rp1.translate(1,0,0)),
                                Point3D(self.rp1.translate(0,1,0)),
                                Point3D(pt1)))
            return rb1

        elif DBAtype in ["Square Hook","J Hook"]:
            layout = Layout3D()
            ptList = []
            fdiam = DimensionStyled()(diam).Dim
            if DBAtype == "Square Hook":
                ptList.append((Pt3D(pt1), 0))
                ptList.append((Pt3D(pt1 + mem.translate(length+fdiam/2.0,0,0)), fdiam))
                ptList.append((Pt3D(ptList[-1][0] + mem.translate(0,0,-(hook+fdiam/2.0))),0))
                calcLength = length+hook-fdiam+fdiam*(pi/2)
            elif DBAtype == "J Hook":
                rad=(hook+fdiam)/1.9999
                ptList.append((Pt3D(pt1), 0))
                ptList.append((Pt3D(pt1 + mem.translate(length+fdiam/2.0,0,0)), rad))
                ptList.append((Pt3D(ptList[-1][0] + mem.translate(0,0,-(hook+fdiam))), rad))
                ptList.append((Pt3D(ptList[-1][0] + mem.translate(-(hook/2.0+fdiam/2.0),0,0)), rad))
                calcLength = length-(hook/2)+(hook+fdiam)*(pi/2)
            for pt, r in ptList:
                layout.add_node(Point3D(pt.x, pt.y, pt.z),r)
            a = Plane3D(ptList[0][0],ptList[1][0],ptList[2][0])
            layout.set_depth_vectors(Point3D(a.N), False)
            rb1 = RndBar()
            rb1.Member = mem
            rb1.MaterialGrade = grade
            rb1.Centered = "Yes"
            rb1.BarDiameter = fdiam
            
            rb1.WorkpointSlopeDistance = calcLength
            
            rb1.MaterialType = "Round bar"
            rb1.mtrl_usage = s1
            rb1.SurfaceFinish = finish
            rb1.MaterialColor3d = validColTup(color)
            if s2 is not None:
                rb1.ImperialDescription = s2
            if s3 is not None:
                rb1.MetricDescription = s3
            rb1.ReferencePointOffset = (0, 0, 0)
            rb1.mtrl_is_main = "No"
            rb1.layout = layout
            rb1.Add()
            rb1.Rotate(rb1.Member, (0, 90, DBArotation))
            return rb1

    def add_holes(self, mtrl, ptWP, holeXSpa, holeZSpa, holeCols, holeRows,
                  boltSize, holeSize, boltType, holeType, slotLength,
                  slotRot):
        ''' Available hole types
        "Standard Round", "Short Slot", "Oversized round", "Long Slot",
        "Anchor Bolt Hole", "Cope Hole", "Erection Pin Hole",
        "Plug Weld Hole"'''
        
        holeDict = {0: 0,
                    1: 1,
                    2: 1,
                    3: 2,
                    4: 2,
                    5: 3,
                    6: 3,
                    7: 4,
                    8: 4,
                    9: 5,
                    10: 5,
                    11: 6}
        hzStr = "holeObj.CalculateHoleSize()"
        
        if holeType == "Long Slot" and slotLength > boltSize:
            slotStr = "slotLength"
        elif holeType in ["Long Slot", "Short Slot"]:
            slotStr = "holeObj.calc_slot_length()"
        elif holeType in ["Anchor Bolt Hole", "Cope Hole",
                          "Erection Pin Hole", "Plug Weld Hole"] \
                          and holeSize > boltSize:
            hzStr = "holeSize"

        if holeType not in ["Short Slot", "Long Slot"]:
            slotRot = 0.0
        
        # hole group add begin
        holeObj = Hole()
        holeObj.mtrl = [mtrl, ]
        holeObj.pt1 = ptWP
        holeObj.hole_type = holeType
        holeObj.face = "NS Face"
        holeObj.valid_cnc = "Yes"

        if holeCols%2:
            holeObj.x_ref_offset = 0
        else:
            holeObj.x_ref_offset = holeXSpa/2
    
        if holeRows%2:
            holeObj.y_ref_offset = 0
        else:
            holeObj.y_ref_offset = holeZSpa/2
            
        holeObj.x_spa = holeXSpa
        holeObj.y_spa = holeZSpa
        holeObj.group_rot = 0.0
        holeObj.locate = "Center"
        holeObj.columns = holeDict[holeCols]
        holeObj.rows = holeDict[holeRows]
        holeObj.bolt_type = boltType
        holeObj.bolt_dia = boltSize
        holeObj.slot_rot = slotRot
        if holeType in ["Long Slot", "Short Slot"]:
            holeObj.length = eval(slotStr)
        holeObj.hole_dia = eval(hzStr)
        holeObj.create()
        # hole group add end
        return holeObj


    def memRotation(self, rightWP, leftWP):
        sv = Pt3D(rightWP-leftWP).toSPt3D()
        # Warning("Vertical slope: %s Horiz Rotation: %s" % (degrees((pi/2)-sv.theta), degrees(sv.phi)))
        # Return vertical slope angle and horiz slope angle
        return (pi/2)-sv.theta, sv.phi

    def optionDialog(self):
        ''' If a Beam or Joist member is preselected, set self.option to
        "Preselected member" and bypass option dialog box. If the wrong
        type of member is preselected, proceed to option dialog box.'''
        memList = MembersSelected()
        if memList and Member(memList[0]).type in ['Beam', 'Joist']:
            self.memRef = Member(memList[0])
            self.option = "Preselected member"
            return True
        dlg = Dialog()
        dlg.window.geometry(self.choiceDlgPos)
        dlg.model = [self,]
        mainFrame = Frame(dlg)
        mainFrame.Pack(fill='both', expand=True)
        s = "Select option for entering Embed PL".center(50)
        option = Combobox(mainFrame, "option",
                          ["Select member",
                           "Select member, bearing plate",
                           "Select Embed PL end points",
                           "Select reference point",
                           "Edit setup data",
                           "Exit"],s)
        dlg.SetButtons(['cancel', 'okay'])
        try:
            dlg.done()
            self._savewindow(dlg, 'choiceDlgPos')
            return True
        except ResponseNotOK:
            return False
        except Exception, e:
            Warning(formatExceptionInfo())
            return False

    def stud_dim(self, dia):
        '''
        Return stud information.
        Dictionary data:
            key (diameter): {'head_thk': value,
                             'burn_off': value,
                             'head_diam': value}'''
        dd = None
        if type(dia) == str:
            dd= self.xmlDoc.studinfo.get(dia, None)

        elif type(dia) in (int, float):
            dd = self.xmlDoc.studinfo.get(dim_print(dia), None)
        if not dd:
            return {'head_thk': 0.5, 'burn_off': 0.1875, 'head_diam': 1.375}
        return dd

    def setStudInfo(self, studDia):
        dd = self.stud_dim(studDia)
        self.default_dim_string1 = "%s dia.x %s" % (dim_print(dd['head_diam']),
                                                     dim_print(dd['head_thk']))
        self.default_dim_string2 = "%s" % (dim_print(dd['burn_off']))
        return self.default_dim_string1, self.default_dim_string2
