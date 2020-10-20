###########################################################################
## EmbedPLDialog.py Version 4.14
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
Main dialog box for EmbedPL.py
"""
import sys
import os
import Tkinter
import re
from dialog import Dialog, ResponseNotOK
from dialog.entry import Entry, StrEntry
from dialog.entry import FloatEntry, IntEntry
from dialog.frame import Frame, Column
from dialog.label import Label
from dialog.combobox import Combobox
from dialog.radio import Radio
from dialog.choose_file import ChooseMtrl
from dialog.rule import DISABLED, ENABLED
from dialog.rules import *
from dialog.dimension import DimensionEntry, DimensionStyled, IsValidDimension
from dialog.tabset import Tabset, Tab
from dialog.checkbox import CheckButtons, Checkbox
from dialog.text import Text
from dialog.scrollbar import Scrollbar
from dialog.date import Date
from dialog.date import DateEntry
from dialog.button import Button
from dialog.controller import ItemController
from dialog.field import Modified
from dialog.image import Image
from dialog.table import *
from dialog.labeledfield import Labeled
from dialog import text
from dialog import item as dlgItem
from param import Warning, dim_print, dim, Units

from assembly import *
from CustomProperties import *
from Status import *
from WebBrowser import *
from member import Member
import model as SDSmodel

from job import Job

from macrolib.OptionDlg import OptionDlg, MultiOptionDlg, ManageColor
from macrolib.OptionDlg import Warning as Warn, ColorSelect, validColTup, isValidColTup
import TableDlg

code_version = '4.14'
pw = 56

textFont1 = ("Arial", 10, "bold italic")
textFont2 = ("Arial", 12, "bold")
textFont3 = ("Arial", 16, "bold")
textFont4 = ("Tahoma", 14, "bold")
textFont5 = ("Courier New", 12, "bold")
textFont6 = ("Tahoma", 10, "bold")
textFont7 = ("Tahoma", 8, "normal")

geomPatt = re.compile(r"(\d+)?x?(\d+)?([+-])(\d+)([+-])(\d+)")

def build_geom_str(geometryStr, parts=False, size=False, offset=(0,0)):
    '''
    Window size requirements can vary depending on how many widgets are
    displayed. Return complete specification if size is True and size
    specification is present, otherwise return position specification only.
    Argument offset is added to position specification.
    If parts is True, return a list of the specification elements.'''
    
    m = geomPatt.search(geometryStr)
    if m:
        output = []
        if m.group(1) and m.group(2) and size:
            output.append("%sx%s" % (m.group(1), m.group(2)))
        output.append("%s%s%s%s" % (m.group(3),
                                    int(m.group(4))+offset[0],
                                    m.group(5),
                                    int(m.group(6))+offset[1]))
        if parts:
            return output
        return "".join(output)
    return geometryStr

class MemberAttrController(ItemController):
    def __init__(self, val):
        self.val = val
        ItemController.__init__(self, val)
    def Get(self, model):
        return getattr(Member(model.member_number), self.val)
    def Set(self, model, value):
        num = model.member_number
        mem = Member(num)
        setattr(mem, self, value)
        mem.Update(False)
        model.mem = Member(num)

class MemberDateController(MemberAttrController):
    def __init__(self, val):
        MemberAttrController.__init__(self, val)
    def Get(self, model):
        value = getattr( Member(model.member_number), self)
        if value == "NOT SET":
            value = "**NOT SET**"
        return value
    def Set(self, model, value):
        if value == "**NOT SET**":
            value = "NOT SET"
        MemberAttrController.Set(self, model, value)

class LabelWidget(Tkinter.Entry):
    def __init__(self, master, x, y, text):
        self.text = Tkinter.StringVar(master)
        self.text.set(text)
        Tkinter.Entry.__init__(self, master=master)
        self.config(relief="ridge", font=textFont1,
                    bg="#ffffff000", fg="#000000fff",
                    readonlybackground="#ffffff000",
                    justify='center',width=8,
                    textvariable=self.text,
                    state="readonly",
                    takefocus=0)
        self.grid(column=x, row=y)

class EntryWidget(Tkinter.Entry):
    def __init__(self, master, x, y, v):
        Tkinter.Entry.__init__(self, master=master)
        self.value = Tkinter.StringVar(master)
        self.config(textvariable=self.value, width=8,
                    relief="ridge", font=textFont1,
                    bg="#ddddddddd", fg="#000000000",
                    justify='center')
        self.grid(column=x, row=y)
        self.value.set(v)

class EntryGrid(Frame):
    ''' SDS/2 Frame with Tkinter.Entry widgets arranged in columns and rows.'''
    def __init__(self, parent, obj, cols, rows, pattern, anchorPattVar):
        self.anchorPattVar = anchorPattVar
        self.obj = obj
        self.cols = cols
        self.colList = range(1, cols+1)
        self.colList.insert(0, "Row\\Col")
        self.rows = rows
        self.rowList = range(1, rows+1)
        Frame.__init__(self,parent)
        self.widget.config(padx='3.0m', pady='3.0m')

        btnFrame = Frame(self)
        btnFrame.widget.config(padx='3.0m', pady='3.0m')
        btnFrame.no_pack = True
        btnList = ["Clear", "Fill 'D'", "Fill 'S'", "Fill 'H'"]
        dd = dict(zip(btnList, [lambda: self.fill("-"),
                                lambda: self.fill("D"),
                                lambda: self.fill("S"),
                                lambda: self.fill("H")]))
        for col, name in enumerate(btnList):
            btn = Tkinter.Button(btnFrame.widget,
                                 text=name,
                                 anchor='center',
                                 bd=3,
                                 bg='#ffffff000',
                                 fg="#000000fff",
                                 activebackground = "#000000fff",
                                 activeforeground = "#ffffff000",
                                 font=textFont6,
                                 padx='0.25m',
                                 pady='0.25m',
                                 relief='raised',
                                 state='normal',
                                 width=8,
                                 command=dd[name])
            btn.grid(row=0, column=col)
            
        tableFrame = Frame(self)
        tableFrame.widget.config(padx='3.0m', pady='3.0m')
        tableFrame.no_pack = True
        self.tableFrame = tableFrame
        
        self.make_header()
        # initialize array
        self.obj.anchor2Darray = [["-" for i in range(self.cols)] for j in range(self.rows)]
        # Validate pattern and create 2D list
        anchorPattList = [[c for c in list(s) if c.lower() in ['s', 'd', 'h', '-']] \
                          for s in pattern.strip().split(",") if s]
        for j, row in enumerate(self.obj.anchor2Darray):
            for i, col in enumerate(row):
                try:
                    self.obj.anchor2Darray[j][i] = anchorPattList[j][i]
                except:
                    pass
        self.gridDict = {}
        for j in range(len(self.rowList)):
            for i in range(len(self.colList)-1):
                w = EntryWidget(tableFrame.widget, i+1, j+1, self.obj.anchor2Darray[j][i])
                self.gridDict[(i,j)] = w.value
                def handler(event, col=i, row=j):
                    return self.__entryhandler(event, col, row)
                w.bind(sequence="<FocusOut>", func=handler)
                w.bind(sequence="<FocusIn>", func=handler, add="+")
                w.bind(sequence="<Any-KeyRelease>", func=handler, add="+")
        self.update_array()

    def update_array(self):
        for row in range(self.rows):
            for col in range(self.cols):
                self.obj.anchor2Darray[row][col] = self.get(col,row)
        self.obj.anchorPatt = ",".join(["".join(row) for row in self.obj.anchor2Darray])
        self.anchorPattVar.set(self.obj.anchorPatt)

    def make_header(self):
        self.hdrDict = {}
        for i, label in enumerate(self.colList):
            w = LabelWidget(self.tableFrame.widget, i, 0, label)
            self.hdrDict[(i,0)] = w

        for i, label in enumerate(self.rowList):
            w = LabelWidget(self.tableFrame.widget, 0, i+1, label)
            self.hdrDict[(0,i+1)] = w

    def __entryhandler(self, event, col, row):
        event.widget.selection_range(0, Tkinter.END)
        if self.get(col,row).lower() not in ['s', 'd', 'h', '-']:
            event.widget.focus_set()
            event.widget.selection_range(0, Tkinter.END)
            event.widget.configure(bg='yellow') 
        else:
            event.widget.configure(bg='#ddddddddd')
            self.update_array()

    def fill(self, s):
        '''Enter a character into each Entry field'''
        for i in range(self.cols):
            for j in range(len(self.rowList)):
                self.set(i,j,s)
        self.update_array()

    def get(self, x, y):
        return self.gridDict[(x,y)].get()

    def set(self, x, y, v):
        self.gridDict[(x,y)].set(v)
        return v

class EmbedDialog(object):
    
    def __init__(self, model):
        Units("feet")
        dlglabel = "Embed PL [%d]" % model.member_number
        dlg = Dialog(dlglabel)
        self.dlg = dlg
        self.dlg.window.geometry(model.mainDlgPos)
        self.dlg.window.minsize(width=535, height=580)
        dlg.model = [model,]
        self.model = model
        
        self.dlgFrame = Frame(dlg)
        self.dlgFrame.PackForget()
        self.dlgFrame.Pack(side="top", fill='x', anchor='n')

        self.mainColA = Column(self.dlgFrame)
        self.mainColA.PackForget()
        self.mainColA.Pack(fill='x', side='left', anchor='n')
        
        self.mainColB = Column(self.dlgFrame)
        self.mainColB.PackForget()
        self.mainColB.Pack(fill='x', side='top', anchor='n')
        
        self.mainFrame = Frame(dlg)
        self.mainFrame.PackForget()
        self.mainFrame.Pack(side="top", fill='both', expand=True)
        
        if model.option == "Edit setup data":
            self.setup(self.mainFrame)
        else:
            if self.model.existed:

                modelComp = DateEntry(self.mainColA,
                                      MemberDateController('DateModelCompleted'),
                                      label="Model complete date:")
                modelComp.read_only = True

                self.model.swapEnds = False
                swapChk = Checkbox(self.mainColA,"swapEnds",
                                   "Swap end points", default="False")
                def assignRot():
                    def f(arg):
                        if arg['model']['swapEnds']:
                            arg['model']['embed_plan_rotation'] += 180.0
                        else:
                            arg['model']['embed_plan_rotation'] -= 180.0
                    return f
                swapChk.AddRule(Changed, assignRot())

            self.typeCombo = Combobox(self.mainColA, 'anchorType',
                                      model.anchorTypeList,
                                      "Plate Anchor Type")
            def display_min_dims(event):
                if self.typeCombo.Get() in ['Studs, DBAs, Holes',
                                            'Mixed Anchors',
                                            'Anchor Holes']:
                    self.plateLabel.pack()
                else:
                    self.plateLabel.pack_forget()

            zero_btn = Tkinter.Button(self.mainColB.widget,
                                      text="Zero Rows/Columns",
                                      anchor='center',
                                      bd=3,
                                      bg='#ffffff000',
                                      fg="#000000fff",
                                      activebackground = "#000000fff",
                                      activeforeground = "#ffffff000",
                                      font=textFont7,
                                      padx='0.25m',
                                      pady='0.25m',
                                      relief='raised',
                                      state='normal',
                                      command=self.zero_entries)
            zero_btn.pack(side="top", anchor='n')

            tabs = Tabset(self.mainFrame)
            tabs.PackForget()
            tabs.Pack(fill='both', expand=True, anchor='n')
            self.general(tabs)
            self.common(tabs)
            self.stud_info(tabs)
            self.DBA_info(tabs)
            self.plate_holes(tabs)
            if not model.existed or model.member_version > 0:
                self.studDBA_info(tabs)
            self.nailer_holes(tabs)
            self.images(tabs)
            self.setup(tabs)
            '''
            If member is set Model Complete, add label to display Model
            Complete date and disable all fields.'''
            d = Member(model.member_number).model_complete
            self.plateVar = Tkinter.StringVar(self.dlg.window)
            if self.model.existed and d != "NOT SET":
                f = Frame(self.mainFrame)
                f.widget.config(padx=2, pady=2)
                w = Tkinter.Label(f.widget,
                                  text="Model Complete Date: %s" % (d))
                w.config(relief="raised",
                         font=("Tahoma", 10, "bold"),
                         bg="#ffffff000",
                         padx=2, pady=2)
                w.pack()
                for widget in dlg.Find(lambda widget: hasattr(widget, 'read_only')):
                    widget.read_only = True
                    
            elif d == "NOT SET":
                lblFame = Frame(self.mainFrame)
                self.plateLabel = Tkinter.Label(lblFame.widget,
                                                textvariable=self.plateVar)
                self.plateLabel.pack()
                if self.model.anchorType != 'Studs, DBAs, Holes':
                    self.plateLabel.pack_forget()
                self.plateLabel.config(relief="raised", font=("Arial", 8, "bold"), bg="#ff0")
                
                self.typeCombo.AddRule(Always, display_min_dims)
                self.typeCombo.AddRule(Always, self.assignPlateDims)
                
        self.dialog_buttons(dlg)

    def get(self):
        return self.dlg

    def zero_entries(self):
        for obj in [self.scolEntry, self.srowEntry,
                    self.dcolEntry, self.drowEntry,
                    self.bcolCombo, self.browCombo,
                    self.colEntry, self.rowEntry]:
            obj.Set(0)

    def minimum_plate_dims(self):
        if self.typeCombo.Get() == 'Studs, DBAs, Holes':
            minLen = max((self.scolEntry.Get()-1)* \
                         self.sxEntry.Get().Dim+ \
                         DimensionStyled()(self.sdiamCombo.Get()).Dim*2,
                         (self.dcolEntry.Get()-1)* \
                         self.dxEntry.Get().Dim+ \
                         DimensionStyled()(self.ddiamCombo.Get()).Dim*2,
                         (self.bcolCombo.Get()-1)* \
                         self.bxEntry.Get().Dim+ \
                         self.bsEntry.Get().Dim*2.0)
            minDep = max((self.srowEntry.Get()-1)* \
                         self.szEntry.Get().Dim+ \
                         DimensionStyled()(self.sdiamCombo.Get()).Dim*2,
                         (self.drowEntry.Get()-1)* \
                         self.dzEntry.Get().Dim+ \
                         DimensionStyled()(self.ddiamCombo.Get()).Dim*2,
                         (self.browCombo.Get()-1)* \
                         self.bzEntry.Get().Dim+ \
                         self.bsEntry.Get().Dim*2.0)
            s = "Minimum plate dimensions for Studs, DBAs and Holes"
            
        elif self.typeCombo.Get() == 'Mixed Anchors':
            sList = self.model.parse_spacing(self.xEntry.Get(), self.colEntry.Get())
            minLen = sum(sList) + \
                     max(DimensionStyled()(self.sdiamCombo.Get()).Dim*2,
                         DimensionStyled()(self.ddiamCombo.Get()).Dim*2)
            sList = self.model.parse_spacing(self.zEntry.Get(), self.rowEntry.Get())
            minDep = sum(sList) + \
                     max(DimensionStyled()(self.sdiamCombo.Get()).Dim*2,
                         DimensionStyled()(self.ddiamCombo.Get()).Dim*2)
            s = "Minimum plate dimensions for Mixed Anchors"
            
        elif self.typeCombo.Get() == 'Anchor Holes':
            minLen = (self.bcolCombo.Get()-1)* \
                     self.bxEntry.Get().Dim+ \
                     self.bsEntry.Get().Dim*2.0
            minDep = (self.browCombo.Get()-1)* \
                     self.bzEntry.Get().Dim+ \
                     self.bsEntry.Get().Dim*2.0
            s = "Minimum plate dimensions for Anchor Holes"
            
        elif self.typeCombo.Get() == 'Plain':
            minLen = self.plEntry.Get().Dim
            minDep = self.pdEntry.Get().Dim
            s = ""
        
        self.plateVar.set(s + " pattern to fit: %sx%s" % \
                          (DimensionStyled()(max(0.0,minLen)),
                           DimensionStyled()(max(0.0,minDep))))
        return max(0.0,minLen), max(0.0,minDep)

    def assignPlateDims(self, event):
        minLen, minDep = self.minimum_plate_dims()
        event['model']['plate_length'] = max(minLen, event['model']['plate_length'].Dim)
        event['model']['plate_depth'] = max(minDep, event['model']['plate_depth'].Dim)
    
    def colorDlg(self, widget):
        def menuItem(menu1):
            def retrieve(arg):
                app = ColorSelect(self.model,
                                  parent=self.dlg,
                                  initial=widget.Get(),
                                  geometry=build_geom_str(self.dlg.window.geometry(),
                                                          offset=(100,100)))
                if app.dlg1.Run():
                    widget.Set(app.namedColor)
                    x = ManageColor(app.namedColor)
                    widget.GetWidget("Label").config(bg=x.tkName, fg=x.tkNameRev)
                    self.dlg.window.focus_set()
            menu1.add_command(label="Color Dialog",
                              command=CreateInvokableRule(widget, retrieve),
                              underline=1)
            
            menu1.add_separator()
            submenu = dlgItem.Tkinter.Menu(menu1._MenuFacade__menu)
            menu1.add_cascade(label="Named Colors", menu=submenu)

            def __color_handler(color):
                widget.Set(color)
                x = ManageColor(color)
                widget.GetWidget("Label").config(bg=x.tkName, fg=x.tkNameRev)

            for name in Job().default_colors():
                def handler(arg, color=name):
                    return __color_handler(color)
                submenu.add_command(label=name,
                                    command=CreateInvokableRule(widget, handler))
        return menuItem

    def addDlg(self, modelName, widget, vartype='dim'):
        def menuItem(menu):
            def retrieve(arg):
                app = AddSelect(self.model, modelName, self.dlg, vartype)
                if app.Run():
                    if vartype == 'dim':
                        widget.Set(widget.Get().Dim+app.value)
                    else:
                        widget.Set(widget.Get()+app.value)
                    '''
                    Dialog Entry fields lose the ability to accept focus.
                    As a workaround, pick another window or Combobox. PR19727'''
            menu.add_command(label="Add Dialog",
                             command=CreateInvokableRule(widget, retrieve),
                             underline=1)
        return menuItem

    def chgcolors(self, widget, color):
        if not isValidColTup(widget.Get(), testname=True):
            widget.Set(str(validColTup(widget.Get(), color)))
        x = ManageColor(widget.Get())
        widget.GetWidget("Label").config(bg=x.tkName, fg=x.tkNameRev)

    def widget_switcher(self, arg):
        if arg['model']['dbaGrade'][-1] == "M":
            values = self.model.dba_diaListM1
            
        elif arg['model']['dbaGrade'] in ["400R", "300W", "400W", "500W"]:
            values = self.model.dba_diaListM2
            
        else:
            values = self.model.dba_diaList

        if arg['model']['dbaDiam'] not in values:
            self.ddiamComboList[-1].PackForget()
            arg['model']['dbaDiam'] = values[0]
            self.ddiamCombo = Combobox(self.diaFrame, "dbaDiam", values,
                                       "DBA diameter".center(pw))
            self.ddiamCombo.AddRule(Changed, self.assignPlateDims)
            self.ddiamComboList.append(self.ddiamCombo)


    def general(self, parent):
        generalFrame = Tab(parent, 'General')
        if self.model.option in ["Preselected member",
                                 "Select member",
                                 "Select member, bearing plate"] and \
                                 not self.model.existed:
            locationFrame = Frame(generalFrame, 'Embedded plate orientation')
            Combobox(locationFrame, "which_end", ["Left End", "Right End"],
                     "Place embed at which end of beam member".center(pw))
            FloatEntry(locationFrame, "embed_plan_rotation",
                       label="Member plan rotation".center(pw))
            
            if self.model.option == "Select member, bearing plate":
                self.model.axis_rotation = 90.0
                self.model.embed_vertical_offset = 0.0
                DimensionEntry(locationFrame, "brgPl_dist", "dim",
                               "Distance from end of beam member WP to member line".center(pw))
                DimensionEntry(locationFrame, "embed_vertical_offset", "dim",
                               "Distance from bottom of beam to top of embed".center(pw))
            else:
                DimensionEntry(locationFrame, "embed_vertical_offset", "dim",
                               "Distance from top of beam to top of embed".center(pw))
            FloatEntry(locationFrame, "axis_rotation",
                       label="Member X axis rotation".center(pw))
            
        elif self.model.option == "Select Embed PL end points" and not self.model.existed:
            locationFrame = Frame(generalFrame, 'Embedded plate plan rotation')
            s = "Member plan rotation = %0.4f" % (self.model.embed_plan_rotation)
            s += "    Member slope = %0.4f" % (self.model.embed_slope)
            FloatEntry(locationFrame, "axis_rotation",
                       label="Member X axis rotation".center(pw))
            Labeled(locationFrame, s)
            
        elif self.model.option == "Select reference point" and not self.model.existed:
            locationFrame = Frame(generalFrame, 'Embedded plate plan rotation, vertical offset')
            FloatEntry(locationFrame, "embed_plan_rotation",
                       label="Member plan rotation".center(pw))
            FloatEntry(locationFrame, "axis_rotation",
                       label="Member X axis rotation".center(pw))            
            DimensionEntry(locationFrame, "embed_vertical_offset", "dim",
                           "Distance from reference point to top of embed".center(pw))
            DimensionEntry(locationFrame, "ctrPT.z", "dim",
                           "Reference point elevation".center(pw))
            
        elif self.model.existed:
            locationFrame = Frame(generalFrame, 'Embedded plate plan rotation and slope')
            rotEntry = FloatEntry(locationFrame, "embed_plan_rotation",
                                  label="Member plan rotation".center(pw))
            rotEntry.entry.AddRule(dlgItem.Context, self.addDlg("embed_plan_rotation", rotEntry, 'float'))
            ''' Highlight the label widget depending on the value entered
            def showred(event):
                if rotEntry.Get() == 0.0:
                    rotEntry.label_widget.config(bg="red")
                else:
                    rotEntry.label_widget.config(bg="#dedede")
            rotEntry.AddRule(Always, showred)'''
            # rotEntry.label_widget.config(bg="red")
            # rotEntry.GetWidget("Label").config(bg="red")
            # Next line has no effect
            # rotEntry.GetWidget("Entry").config(background="red")
            # rotEntry.GetWidget("Entry").config(show="*", width=75)
            slopeEntry = FloatEntry(locationFrame, "embed_slope",
                                    label="Member vertical slope".center(pw))
            slopeEntry.entry.AddRule(dlgItem.Context, self.addDlg("embed_slope", slopeEntry, 'float'))
            
            axisEntry = FloatEntry(locationFrame, "axis_rotation",
                                   label="Member X axis rotation".center(pw))
            axisEntry.entry.AddRule(dlgItem.Context, self.addDlg("axis_rotation", axisEntry, 'float'))
            
            elevEntry = DimensionEntry(locationFrame, "embed_elev", "dim",
                                       "Embed elevation".center(pw))
            elevEntry.entry.AddRule(dlgItem.Context, self.addDlg("embed_elev", elevEntry))
        locationFrame.widget.config(relief="ridge", bd=3)
        ###################################################################
        markFrame = Frame(generalFrame, 'General')
        markFrame.widget.config(relief="ridge", bd=3)

        if not self.model.existed:
            Entry(markFrame, "mark_prefix", str,
                  "Piecemark prefix".center(pw))
        else:
            # Piecemark cannot be modified
            memObj = SDSmodel.member(self.model.GetMemberNumber())
            # memObj.system_piecemark returns True or False
            if memObj.system_piecemark:
                s = "System"
            else:
                s = "User"
            self.markEntry = StrEntry(markFrame, MemberAttrController('piecemark'),
                                      "%s Piecemark  ".center(pw) % (s))
            self.markEntry.read_only=True

        Combobox(markFrame, "plate_grade",
                 Job().steel_grades("Plate").keys(),
                 "Plate material grade".center(pw))
        Combobox(markFrame, "plate_finish", self.model.finishList,
                 "Plate material finish".center(pw))
        
        pcEntry = Entry(markFrame, "plate_color", str,
                        "Plate material color".center(pw))
        x = ManageColor(self.model.plate_color)
        pcEntry.GetWidget("Label").config(bg=x.tkName, fg=x.tkNameRev)
        pcEntry.entry.AddRule(dlgItem.Context, self.colorDlg(pcEntry))
        pcEntry.AddRule(Always, lambda arg: self.chgcolors(pcEntry, (60,60,60)))
        
        ###################################################################
        dimFrame = Frame(generalFrame, "Embedded plate dimensions")
        dimFrame.widget.config(relief="ridge", bd=3)

        self.plEntry = DimensionEntry(dimFrame, "plate_length", "dim",
                                      "Member plate length".center(pw))
        self.plEntry.AddRule(Always, self.assignPlateDims)
        
        self.pdEntry = DimensionEntry(dimFrame, "plate_depth", "dim",
                                      "Member plate depth".center(pw))
        self.pdEntry.AddRule(Always, self.assignPlateDims)
                
        ptEntry = DimensionEntry(dimFrame, "plate_thk", "dim",
                                 "Member plate thickness".center(pw))
        
        ptEntry.AddRule(Validate, expr("plate_thk >= 0.03125"),
                        "Plate thickness must be at least 1/32.")
        
        ###################################################################
        seqFrame = Frame(generalFrame, "Sequence")
        seqFrame.widget.config(relief="ridge", bd=3)
        select = Combobox(seqFrame,
                          MemberAttrController('ErectionSequence'),
                          Job().sequences(),
                          "Select sequence".center(pw))
        
    def common(self, parent):
        commonFrame = Tab(parent, 'Common')
        ###################################################################
        finishFrame = Frame(commonFrame, "Material finish and color")
        finishFrame.widget.config(relief="ridge", bd=3)
        Combobox(finishFrame, "stud_finish", self.model.finishList,
                 "Stud/DBA material finish".center(pw))
        colEntry = Entry(finishFrame, "stud_color", str,
                         "Stud/DBA material color".center(pw))
        x = ManageColor(self.model.stud_color)
        colEntry.GetWidget("Label").config(bg=x.tkName, fg=x.tkNameRev)
        colEntry.entry.AddRule(dlgItem.Context, self.colorDlg(colEntry))
        colEntry.AddRule(Always, lambda arg: self.chgcolors(colEntry, (255,255,0)))
        ###################################################################
        offsetFrame = Frame(commonFrame, "Pattern offset")
        offsetFrame.widget.config(relief="ridge", bd=3)
        DimensionEntry(offsetFrame, "x_off", style="dim",
                       label="Studs/DBA/Hole horizontal pattern offset".center(pw))
        DimensionEntry(offsetFrame, "z_off", style="dim",
                       label="Studs/DBA/Hole vertical pattern offset (+ = UP)".center(pw))
        s = "EmbedPL Member Key Plan"
        picsFrame = Frame(commonFrame, s)
        picsFrame.widget.config(relief="ridge", bd=3)
        picsFrame.image(self.model.image_name5)

    def stud_info(self, parent):
        ruleStr = "['Mixed Anchors', 'Anchor Holes', 'Plain']"
        studFrame = Tab(parent, 'Studs')
        w = Tkinter.Label(studFrame.widget,
                          text="Enter 0 stud columns or rows for no studs.")
        w.pack()
        w.config(relief="raised",
                 font=("Arial", 10, "bold italic"),
                 bg="#ffffff000")
        ###################################################################
        infoFrame = Frame(studFrame, "Stud information, default diameter")
        infoFrame.widget.config(relief="ridge", bd=3)
        infoEntry1 = Entry(infoFrame, 'default_dim_string1', str,
                          "Head dimensions".center(pw))
        infoEntry1.read_only = True
        infoEntry2 = Entry(infoFrame, 'default_dim_string2', str,
                          "Burn off".center(pw))
        infoEntry2.read_only = True
        ###################################################################
        def assignStudInfo(s1, s2):
            def stud(e):
                e['model'][s1], e['model'][s2] = self.model.setStudInfo(e['model']['stud_diam'])
            return stud

        attrFrame = Frame(studFrame, "Stud attributes")
        attrFrame.widget.config(relief="ridge", bd=3)
        self.sdiamCombo = Combobox(attrFrame, "stud_diam",
                                   self.model.stud_diaList,
                                   "Stud diameter".center(pw))
        self.sdiamCombo.AddRule(Always,
                                assignStudInfo('default_dim_string1',
                                               'default_dim_string2'))
        self.sdiamCombo.AddRule(Changed, self.assignPlateDims)
        
        DimensionEntry(attrFrame, "stud_length", "dim",
                       "Stud length".center(pw))
        ###################################################################
        pattFrame = Frame(studFrame, "Stud pattern")
        pattFrame.widget.config(relief="ridge", bd=3)
        
        self.scolEntry = Entry(pattFrame, "studCols", int,
                               "Number of stud columns".center(pw))
        self.scolEntry.AddRule(Changed, self.assignPlateDims)
        
        self.srowEntry = Entry(pattFrame, "studRows", int,
                               "Number of stud rows".center(pw))
        self.srowEntry.AddRule(Changed, self.assignPlateDims)
        
        self.sxEntry = DimensionEntry(pattFrame, "studXSpa", style="dim",
                                      label="Horizontal stud spacing".center(pw))
        self.sxEntry.AddRule(Changed, self.assignPlateDims)
        
        self.szEntry = DimensionEntry(pattFrame, "studZSpa", style="dim",
                                      label="Vertical stud spacing".center(pw))
        self.szEntry.AddRule(Changed, self.assignPlateDims)
        
        for widget in (self.scolEntry, self.srowEntry,
                       self.sxEntry, self.szEntry):
            widget.AddRule(State, expr("anchorType in %s" % (ruleStr)),
                            DISABLED, [self.typeCombo,])

    def DBA_info(self, parent):
        ruleStr = "['Mixed Anchors', 'Anchor Holes', 'Plain']"
        dbaFrame = Tab(parent, 'DBAs')
        w = Tkinter.Label(dbaFrame.widget,
                          text="Enter 0 DBA columns or rows for no DBAs.")
        w.pack()
        w.config(relief="raised", font=("Arial", 10, "bold italic"),
                 bg="#ffffff000")
        
        ###################################################################
        attrFrame = Frame(dbaFrame, "DBA attributes")
        attrFrame.widget.config(relief="ridge", bd=3)
        typeBox = Combobox(attrFrame, "dbaType", self.model.dbaTypeList,
                           "DBA type".center(pw))

        # Frame place holder for self.ddiamCombo
        self.diaFrame = Frame(attrFrame)
        if self.model.dbaGrade[-1] == "M":
            values = self.model.dba_diaListM1
            
        elif self.model.dbaGrade  in ["400R", "300W", "400W", "500W"]:
            values = self.model.dba_diaListM2
            
        else:
            values = self.model.dba_diaList
        self.ddiamCombo = Combobox(self.diaFrame, "dbaDiam", values,
                                   "DBA diameter".center(pw))
        self.ddiamCombo.AddRule(Changed, self.assignPlateDims)
        self.ddiamComboList = [self.ddiamCombo,]

        DimensionEntry(attrFrame, "dbaLength", "dim",
                       "DBA length".center(pw))
        hookEntry = DimensionEntry(attrFrame, "dbaHook", "dim",
                                   "DBA hook".center(pw))

        self.gradeCombo = Combobox(attrFrame, "dbaGrade",
                                   self.model.dbaGradeList,
                                   "DBA material grade".center(pw))
        self.gradeCombo.AddRule(Always, self.widget_switcher)

        hookEntry.AddRule(State, expr("dbaType in ['Straight',]"),
                          DISABLED, [typeBox,])
        rotZCombo = Combobox(attrFrame, "dbaZRot", [0,90,180,270],
                             "DBA rotation member Z axis".center(pw))
        rotZCombo.AddRule(State, expr("dbaType == 'Straight'"),
                          DISABLED, [typeBox])
        rotAltCombo = Combobox(attrFrame, "rotateAltDBAs", ('Yes', 'No'),
                            "Rotate alternate DBA rows 180 deg".center(pw))
        rotAltCombo.AddRule(State, expr("dbaType == 'Straight'"),
                            DISABLED, [typeBox])
        
        ###################################################################
        pattFrame = Frame(dbaFrame, "DBA pattern")
        pattFrame.widget.config(relief="ridge", bd=3)
        self.dcolEntry = Entry(pattFrame, "dbaCols", int,
                               "Number of DBA columns".center(pw))
        self.dcolEntry.AddRule(Changed, self.assignPlateDims)
        
        self.drowEntry = Entry(pattFrame, "dbaRows", int,
                               "Number of DBA rows".center(pw))
        self.drowEntry.AddRule(Changed, self.assignPlateDims)
        
        self.dxEntry = DimensionEntry(pattFrame, "dbaXSpa", style="dim",
                                      label="Horizontal DBA spacing".center(pw))
        self.dxEntry.AddRule(Changed, self.assignPlateDims)
        
        self.dzEntry = DimensionEntry(pattFrame, "dbaZSpa", style="dim",
                                      label="Vertical DBA spacing".center(pw))
        self.dzEntry.AddRule(Changed, self.assignPlateDims)

        for widget in (self.dcolEntry, self.drowEntry,
                       self.dxEntry, self.dzEntry):
            widget.AddRule(State, expr("anchorType in %s" % (ruleStr)),
                            DISABLED, [self.typeCombo,])

    def validate_spacing(self, val):
        val = val.Get().strip(" ,")
        if ',' in val:
            sList = val.split(',')
            for item in sList:
                if not IsValidDimension(item):
                    return False
        else:
            return IsValidDimension(val)
        return True

    def update_grid(self):
        def f(arg):
            self.entryTable.widget.destroy()
            self.entryTable = EntryGrid(self.gridFrame, self.model,
                                        arg['model']['anchorCols'],
                                        arg['model']['anchorRows'],
                                        str(self.anchEntryVar.get()),
                                        self.anchEntryVar)
        return f

    def studDBA_info(self, parent):
        ruleStr = "['Studs, DBAs, Holes', 'Anchor Holes', 'Plain']"
        combFrame = Tab(parent, 'Mixed')
        s = "Enter 'S', 'D' 'H', or '-' into the table for STUD, DBA, HOLE, or NO ANCHOR."
        s += "\nConfigure stud and DBA attributes on their respective tabs."
        s += "\nSpacing Example 1: 8.25 (evenly spaced)"
        s += "\nSpacing Example 2: 8.25,6.75,6.75,8.25"
        w = Tkinter.Label(combFrame.widget,text=s)
        w.pack(side="top")
        w.config(relief="raised", font=("Arial", 10, "bold italic"),
                 bg="#ffffff000", pady=3)

        archEntryFrame = Frame(combFrame, 'Anchor Pattern')
        archEntryFrame.widget.config(relief="ridge", labelanchor='n',
                                     bd=3, padx=1, pady=3)
        
        self.anchEntryVar = Tkinter.StringVar(combFrame.widget)
        self.anchEntryVar.set(self.model.anchorPatt)
        self.anchEntry = Tkinter.Label(archEntryFrame.widget,
                                       textvariable=self.anchEntryVar,
                                       anchor="center", justify="center",
                                       font=textFont5,
                                       height=1, pady=1)
        self.anchEntry.pack(side="top", fill="x", expand=1)

        mainFrame = Frame(combFrame, "Anchor Pattern Attributes")
        mainFrame.widget.config(relief="ridge", bd=3)
        ###################################################################
        self.colEntry = IntEntry(mainFrame, "anchorCols",
                                 "Number of anchor columns".center(pw))
        self.colEntry.AddRule(Changed, self.update_grid())
        self.colEntry.AddRule(Changed, self.assignPlateDims)
        
        self.rowEntry = IntEntry(mainFrame, "anchorRows",
                                 "Number of anchor rows".center(pw))
        self.rowEntry.AddRule(Changed, self.update_grid())
        self.rowEntry.AddRule(Changed, self.assignPlateDims)
        
        self.model.anchorColSpa = str(self.model.anchorColSpa)
        self.xEntry = StrEntry(mainFrame, "anchorColSpa",
                               "Horizontal anchor spacing".center(pw))
        self.xEntry.PopupValidate(self.validate_spacing,
                                  "Invalid spacing string")
        self.xEntry.AddRule(Changed, self.assignPlateDims)
        
        self.model.anchorRowSpa = str(self.model.anchorRowSpa)
        self.zEntry = StrEntry(mainFrame, "anchorRowSpa",
                               "Vertical anchor spacing".center(pw))
        self.zEntry.PopupValidate(self.validate_spacing,
                                  "Invalid spacing string")
        self.zEntry.AddRule(Changed, self.assignPlateDims)

        for widget in (self.colEntry, self.rowEntry,
                       self.xEntry, self.zEntry):
            widget.AddRule(State, expr("anchorType in %s" % (ruleStr)),
                            DISABLED, [self.typeCombo,])

        self.gridFrame = Frame(combFrame)
        self.entryTable = EntryGrid(self.gridFrame, self.model,
                                    self.model.anchorCols,
                                    self.model.anchorRows,
                                    self.model.anchorPatt,
                                    self.anchEntryVar)
        def manage_show(arg):
            if arg['model']['anchorType'] != 'Mixed Anchors':
                self.gridFrame.PackForget()
            else:
                self.gridFrame.Pack()
        self.typeCombo.AddRule(Always, manage_show)
        
    def nailer_holes(self, parent):
        holeFrame = Tab(parent, "Nlr Holes")
        ###################################################################
        def assignNlrED(s1, s2):
            def nlr(event):
                event['model'][s1] = max(event['model'][s2].Dim*0.75,
                                         event['model'][s1].Dim)
            return nlr
        ###################################################################
        infoFrame = Frame(holeFrame, "Nailer hole variables")
        infoFrame.widget.config(relief="ridge", bd=3)
        Combobox(infoFrame, "nailer_holes", [0, 2, 4],
                       "Number of nailer holes".center(pw))

        sizeEntry = DimensionEntry(infoFrame, "nailer_hole_size", style="dim",
                                   label="Nailer hole size".center(pw))
        
        sizeEntry.AddRule(Changed, assignNlrED('nailer_edge_dist',
                                              'nailer_hole_size'))
        
        distEntry = DimensionEntry(infoFrame, "nailer_edge_dist", style="dim",
                                   label="Nailer hole edge distance".center(pw))
        
        distEntry.AddRule(Changed, assignNlrED('nailer_edge_dist',
                                              'nailer_hole_size'))
        ###################################################################
        s = "Embed PL with 180 degree plan rotation"
        picsFrame = Frame(holeFrame, s)
        picsFrame.widget.config(relief="ridge", bd=3)
        picsFrame.image(self.model.image_name4)

    def plate_holes(self, parent):
        ''' Available hole types
        "Standard Round", "Short Slot", "Oversized round", "Long Slot",
        "Anchor Bolt Hole", "Cope Hole", "Erection Pin Hole",
        "Plug Weld Hole"'''
        ruleStr = "['Mixed Anchors', 'Plain']"
        holeFrame = Tab(parent, "Holes")
        w = Tkinter.Label(holeFrame.widget,
                          text="Enter 0 hole columns or rows for no holes.")
        w.pack()
        w.config(relief="raised",
                 font=("Arial", 10, "bold italic"),
                 bg="#ffffff000")
        
        infoFrame = Frame(holeFrame, "Plate hole variables")
        infoFrame.widget.config(relief="ridge", bd=3)
        
        self.bcolCombo = Combobox(infoFrame, "holeCols", [0,1,2,3,4,5,6,7,8,9,10,11],
                                 "Number of hole columns".center(pw))
        self.bcolCombo.AddRule(State, expr("anchorType in %s" % (ruleStr)),
                              DISABLED, [self.typeCombo,])
        self.bcolCombo.AddRule(Changed, self.assignPlateDims)
        
        self.browCombo = Combobox(infoFrame, "holeRows", [0,1,2,3,4,5,6,7,8,9,10,11],
                                 "Number of hole rows".center(pw))
        self.browCombo.AddRule(State, expr("anchorType in %s" % (ruleStr)),
                               DISABLED, [self.typeCombo,])
        self.browCombo.AddRule(Changed, self.assignPlateDims)
        
        self.bxEntry = DimensionEntry(infoFrame, "holeXSpa", style="dim",
                                      label="Hole column spacing".center(pw))
        self.bxEntry.AddRule(State, expr("anchorType in %s" % (ruleStr)),
                            DISABLED, [self.typeCombo,])
        self.bxEntry.AddRule(Changed, self.assignPlateDims)
        
        self.bzEntry = DimensionEntry(infoFrame, "holeZSpa", style="dim",
                                       label="Hole row spacing".center(pw))
        self.bzEntry.AddRule(State, expr("anchorType in %s" % (ruleStr)),
                            DISABLED, [self.typeCombo,])
        self.bzEntry.AddRule(Changed, self.assignPlateDims)
        
        self.bsEntry = DimensionEntry(infoFrame, "boltSize", "dim",
                                      "Bolt size".center(pw))
        self.bsEntry.AddRule(Changed, self.assignPlateDims)
        
        Combobox(infoFrame, "boltType", Job().bolt_sched(),
                 "Bolt type".center(pw))
        htBox = Combobox(infoFrame, "holeType", self.model.holeTypeList,
                         "Hole type".center(pw))
        hzEntry = DimensionEntry(infoFrame, "holeSize", "dim",
                                 "Hole size".center(pw))
        s1 = "holeType not in ['Anchor Bolt Hole', 'Cope Hole',"
        s1 += " 'Erection Pin Hole', 'Plug Weld Hole']"
        hzEntry.AddRule(State, expr(s1), DISABLED, [htBox])
        slotlenEntry = DimensionEntry(infoFrame, "slotLength", "dim",
                                      "Long slot length".center(pw))
        slotlenEntry.AddRule(State, expr("holeType != 'Long Slot'"),
                             DISABLED, [htBox])
        slotrotEntry = FloatEntry(infoFrame, "slotRot",
                                  label="Slot rotation".center(pw))
        s2 = "holeType not in ['Long Slot', 'Short Slot']"
        slotrotEntry.AddRule(State, expr(s2), DISABLED, [htBox])

    def images(self, parent):
        imagesFrame = Tab(parent, "Image")
        if self.model.existed:
            imageChild = Frame(imagesFrame, "EmbedPL with Studs, DBAs, Holes")
            image1 = Frame(imageChild)
            image1.Pack(side='left', expand=1)
            image1.image(self.model.image_name3)
        else:
            imageChild = Frame(imagesFrame, "Wall Embed PLs")
            #imageChild.Pack(side="top")
            image1 = Frame(imageChild)
            image1.Pack(side='left', expand=1)
            image1.image(self.model.image_name1)
            image2 = Frame(imageChild)
            image2.Pack(side='left', expand=1)
            image2.image(self.model.image_name2)
        imageChild.widget.config(relief="ridge", bd=3)
        
    def updatesetup(self, name):
        def S(event):
            self.model._savesetup(name, event['model'][name])
        return S
        
    def setup(self, parent):
        if self.model.option != "Edit setup data":
            setupFrame = Tab(parent, "Setup")
        else:
            setupFrame = parent
        varFrame = Frame(setupFrame, "Embedded plate variable control options")
        varFrame.widget.config(relief="ridge", bd=3, padx=6, pady=6)
        s = "member_version: %s  " % (self.model.member_version)
        s += "_version: %s  code_version: %s" % (self.model._version,
                                                  self.model.code_version)
        verLabel = Label(varFrame, s)

        verLabel.widget.config(relief="ridge",
                               font=("Arial", 10, "bold"),
                               bg="#ddddddddd", padx=6, pady=4) 

        funcCombo = Combobox(varFrame, "func_data_or_last",
                             ['XML Data', 'Last values used'],
                             "Determine variables options".center(pw))
        funcCombo.AddRule(Changed, self.updatesetup("func_data_or_last"))
        
        windowEntry = Entry(varFrame, "mainDlgPos", str,
                            "Window Information".center(pw))
        windowEntry.read_only = True

        markEntry = Entry(varFrame, "mark_prefix", str,
                          "Member mark prefix".center(pw))
        markEntry.read_only = True

        editFrame = Frame(setupFrame, "Edit setup information")
        editFrame.widget.config(relief="ridge", bd=3, padx=6, pady=6)

        self.setupButtonList = []
        for i, label in enumerate(("Stud Table", "Plate Table", "Joist Table", "Mixed Table")):
            col = Column(editFrame)
            btn = Tkinter.Button(Frame(col).widget,
                                  text=label,
                                  anchor='center',
                                  bd=3,
                                  bg='#ffffff000',
                                  fg="#000000fff",
                                  activebackground = "#000000fff",
                                  activeforeground = "#ffffff000",
                                  font=("Arial", 10, "bold"),
                                  padx='1.0m',
                                  pady='1.0m',
                                  relief='raised',
                                  state='normal',
                                  width=10)
            self.setupButtonList.append((btn, label))
            btn.pack(anchor='center')
            def handler(event, i=i, parent=self.dlg):
                return self._buttonHandler(event, i, parent)
            btn.bind(sequence="<ButtonRelease-1>", func=handler)
            col.PackForget()
            col.Pack(side="left", fill="both", expand=1)


    def _buttonHandler(self, event, btnNumber, parent):
        # Raise button back up
        self.setupButtonList[btnNumber][0].config(relief='raised')
        if self.setupButtonList[btnNumber][1] == "Stud Table":
            self.model._initializeXMLdata()
            app = TableDlg.GridDlg(self.model.xmlDoc.studinfo,
                                   title="Stud Table",
                                   parent=self.dlg,
                                   text="Var\\Diam",
                                   geometry=build_geom_str(self.model.studEditDlgPos))
            if app.get().Run():
                self.model._saveinfo('stud_diam',
                                     self.model.xmlDoc.studinfo.keys(),
                                     app.table.dd)
                # Warning("Stud Table saved to XML")
            # Warning("Saving Stud Table window (%s)" % (app.dlg.window.geometry()))
            self.model._savewindow(app.dlg, 'studEditDlgPos')
            self.model.studEditDlgPos = app.dlg.window.geometry()
            
        elif self.setupButtonList[btnNumber][1] == "Plate Table":
            self.model._initializeXMLdata()
            app = TableDlg.GridDlg(self.model.plateinfo,
                                   title="Plate Table",
                                   parent=self.dlg,
                                   text="Var\\Nom D",
                                   geometry=build_geom_str(self.model.plateEditDlgPos))
            if app.get().Run():
                self.model._saveinfo('nom_depth',
                                     self.model.plateinfo.keys(),
                                     app.table.dd)
                # Warning("Plate Table saved to XML")
            # Warning("Saving Plate Table window (%s)" % (app.dlg.window.geometry()))
            self.model._savewindow(app.dlg, 'plateEditDlgPos')
            self.model.plateEditDlgPos = app.dlg.window.geometry()

        elif self.setupButtonList[btnNumber][1] == "Joist Table":
            self.model._initializeXMLdata()
            app = TableDlg.GridDlg(self.model.xmlDoc.jstanchordata,
                                   title="Joist Table",
                                   parent=self.dlg,
                                   text="Var\\Series",
                                   geometry=build_geom_str(self.model.plateEditDlgPos))
            if app.get().Run():
                self.model._saveinfo('series',
                                     self.model.xmlDoc.jstanchordata.keys(),
                                     app.table.dd)
                # Warning("Plate Table saved to XML")
            # Warning("Saving Plate Table window (%s)" % (app.dlg.window.geometry()))
            self.model._savewindow(app.dlg, 'plateEditDlgPos')
            self.model.plateEditDlgPos = app.dlg.window.geometry()

        elif self.setupButtonList[btnNumber][1] == "Mixed Table":
            self.model._initializeXMLdata()
            # convert self.model.AnchorDataDict1 to usable form
            dd = {}
            for key, value in self.model.AnchorDataDict1.items():
                dd[key] = value
                dd[key]['patt'] = dd[key]['patt'][1]
            app = TableDlg.GridDlg(dd,
                                   title="Mixed Table",
                                   parent=self.dlg,
                                   text="Var\\Depth",
                                   geometry=build_geom_str(self.model.plateEditDlgPos))
            if app.get().Run():
                self.model._saveinfo('depth',
                                     dd.keys(),
                                     app.table.dd)
                # Warning("Plate Table saved to XML")
            # Warning("Saving Plate Table window (%s)" % (app.dlg.window.geometry()))
            self.model._savewindow(app.dlg, 'plateEditDlgPos')
            self.model.plateEditDlgPos = app.dlg.window.geometry()

    def __help__(self):
        OpenHelp("webhome.htm")

    def __prop_edit__(self):
        EditMemberProperties(self.model.member_number)

    def __status_edit__(self):
        EditMemberStatus(self.model.member_number)
        
    def dialog_buttons(self, parent):
        helpButton = Tkinter.Button(parent.Buttons, text="Help",
                               default='active', height=1,
                               width=10, padx=0, pady='.25m')
        helpButton.config(command=self.__help__)
        parent.Buttons_dict['help'] = helpButton
        
        propButton = Tkinter.Button(parent.Buttons, text="Properties",
                               default='active', height=1,
                               width=10, padx=0, pady='.25m')

        propButton.config(command=self.__prop_edit__)
        parent.Buttons_dict['properties'] = propButton

        statusButton = Tkinter.Button(parent.Buttons, text="Status",
                                 default='active', height=1,
                                 width=10, padx=0, pady='.25m')

        statusButton.config(command=self.__status_edit__)
        parent.Buttons_dict['status'] = statusButton

        parent.SetButtons(['help', 'reset', 'cancel',
                           'okay', 'status', 'properties'])

def select_text_and_focus(widget):
    widget.selection_range( 0, Tkinter.END )
    widget.focus_set()

class AddSelect(Dialog):
    def __init__(self, model, attr, master=None, vartype='dim'):
        # Possible values of vartype: dim, float
        Dialog.__init__(self, "Increment Dialog Box Value", master=master)
        self.window.geometry(build_geom_str(master.window.geometry(), offset=(100,100)))
        self.window.minsize(width=150, height=100)
        self.model = [self,]
        if vartype == 'float':
            self.w = FloatEntry(self, 'value',
                                label="Enter amount to add to %s" % (attr.replace("_", "\\_")),
                                default=0.0)
        else:
            self.w = DimensionEntry(self, 'value', style='dim',
                                    label="Enter amount to add to %s" % (attr.replace("_", "\\_")),
                                    default=0.0)
        self.AddStartup(lambda: select_text_and_focus(self.w.GetWidget("Entry")))
        self.SetButtons(['cancel','okay'])

'''
This should work, but doesn't.
widget.GetWidget("Entry").focus_set()
widget.GetWidget("Entry").selection_range(0, Tkinter.END)'''