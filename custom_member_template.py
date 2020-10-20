import bolt_add
import CustomProperties
import dialog.combobox
import dialog.controller
import dialog.date
import dialog.dimension
import dialog.entry
import dialog.rule
import dialog.rules
import Hash
import hole_add
import job
import math
import member
import MemberBase
import mtrl_list
import param
import point
import Point3D
import rect_plate
import StateAccessor
import Status
import Tkinter
import Transform3D
import WebBrowser
##import additional modules as necessary
''' CUSTOM MEMBER TEMPLATE FOUND ON SDS2 SUPPORT FORUM'''


def mark_read_only( obj ):
    if hasattr( obj, 'read_only' ):
        obj.read_only = True
    for c in obj.children:
        mark_read_only( c )

def is_read_write_station():
    return param.StationType() in [ 'Full Station', 'EAD/2 Station',
                                    'Modelling Station' ]

def dialog_buttons( f ):
    h = Tkinter.Button( f.Buttons, text = "Help", default = 'active',
                        height = 1, width = 10, padx = 0, pady = '.25m' )
    def help_cmd():
        WebBrowser.OpenHelp( "MyCustomMember.htm" ) #help documentation #rename
    h.config( command = help_cmd )
    f.Buttons_dict[ 'help' ] = h

    member_number_entry = dialog.entry.IntEntry( f, 'member_number' )
    member_number_entry.PackForget()

    p = Tkinter.Button( f.Buttons, text = "Properties", default = 'active',
                        height = 1, width = 10, padx = 0, pady = '.25m' )

    def cust_prop_edit():
        CustomProperties.EditMemberProperties( member_number_entry.Get() )
    p.config( command = cust_prop_edit )
    f.Buttons_dict[ 'properties' ] = p

    s = Tkinter.Button( f.Buttons, text = "Status", default = 'active',
                        height = 1, width = 10, padx = 0, pady = '.25m' )

    def status_edit():
        Status.EditMemberStatus( member_number_entry.Get() )
    s.config( command = status_edit )
    f.Buttons_dict[ 'status' ] = s

    f.SetButtons( [ 'help', 'reset', 'cancel', 'okay',
                    'status', 'properties' ] )
    return f

class MemberAttrController( dialog.controller.ItemController ):
    def __init__( self, val ):
        dialog.controller.ItemController.__init__( self, val )
        self.kind = str
    def Get( self, model ):
        return getattr( member.Member( model.member_number ), self )
    def Set( self, model, value ):
   mem = member.Member( model.member_number )
   setattr( mem, self, self.kind( value ) )
        if mem.DateModelCompleted == 'NOT SET' and is_read_write_station():
            mem.Update( False )

def FloatMemberAttrController( name ):
    c = MemberAttrController( name )
    c.kind = float
    return c

class MemberDateController( MemberAttrController ):
    def __init__( self, val ):
        MemberAttrController.__init__( self, val )
    def Get( self, model ):
        value = getattr( member.Member( model.member_number ), self )
        if value == 'NOT SET':
            value = '**NOT SET**'
        return value
    def Set( self, model, value ):
        if value == '**NOT SET**':
            value = 'NOT SET'
        MemberAttrController.Set( self, model, value )

class MyCustomMember( StateAccessor.StateAccessor, MemberBase.MemberBase ): #rename

    _version = 2 #Change Version # to match # of arguments
    _arguments = {}
    _arguments[ 0 ] = ( ( 'thickness', 1. ),  #redefine arguements ( 'variable', default_value),
                        ( 'width', 6. ) )     #add more arguements here
    _arguments[ 1 ] = _arguments[ 0 ] + ( ( 'other_member', -1 ), ) # not required
    _arguments[ 2 ] = _arguments[ 1 ] + ( ( 'this_mtrl_guid', None ), # not required
                                          ( 'other_mtrl_guid', None ) ) # not required

    default_length = 12. # additional object defined within the class # not required

    def __init__( self ):
        StateAccessor.StateAccessor.__init__( self )
        MemberBase.MemberBase.__init__( self )
   self.SetMemberType( 'MyCustomMember' ) #must be <= 16 characters #rename
   self.SetPiecemarkPrefix( 'MCM_' )      #used like B_ for a beam
        self.SetImmediateProcess( False )      #material generation immediately?

    def AddByPreselection( self ): #modify preselection function to suit needs
        if len( member.MembersSelected() ) > 0:
            self.other_member = member.MembersSelected()[ 0 ]
            param.ClearSelection()
            m = Transform3D.Transform3D( self.other_member )
            self.left_location = m.GetTranslation()
            l2r = MyCustomMember.default_length * Transform3D.GetY( m ) #rename
            self.right_location = self.left_location + l2r
            return True
        return False

    def AddByTwoPoints( self ):
        p = point.PointLocate( 'Locate left end' )
        if p == None:
            return False
        self.left_location = Point3D.Point3D( p )

        p = point.PointLocate( 'Locate right end', p )
        if p == None:
            return False
        self.right_location = Point3D.Point3D( p )
        return True

    def Add( self ):
        try:
            return self._Add()
        except Exception, e:
##            raise ## use this line and comment next line when troubleshooting the method
            param.Warning( 'MyCustomMember::Add:' + str( e ) ) #rename
        return False

    def _Add( self ):
        param.Units( 'inches' )
        return self.AddByPreselection() or self.AddByTwoPoints() # determine how you want to add

    def Edit( self ):
        try:
            return self._Edit()
        except Exception, e:
##            raise ## use this line and comment next line when troubleshooting the method
            param.Warning( 'MyCustomMember::Edit:' + str( e ) ) #rename
        return False

    def _Edit( self ):
        param.Units( 'inches' )

        orig_hash = None

        if member.Member( self.member_number ).Piecemark is not None:
            orig_hash = self.Hash()

        title = 'MyCustomMember Edit -- Member %s' % self.member_number #rename

        d = param.Dialog(                # dialog box object
            title, loadable_type = 'MyCustomMemberForms', #rename
            loadable_ignore = [ 'member_number', 'DateModelCompleted' ] )

        d.model = [ self ]

        ###########################################
        ######### change edit screen here #########

        #menu of sequences
   dialog.combobox.Combobox(
            d, MemberAttrController( 'ErectionSequence' ),
            job.Job().sequences(), "Sequence" )

        ### keep model complete
        #model complete read only attribute
        model_complete_entry = dialog.date.DateEntry(
            d, MemberDateController( 'DateModelCompleted' ),
            'Model complete date:' )
        model_complete_entry.read_only = True

        d.AddRule(
            dialog.rules.State,
            dialog.rules.expr( "not DateModelCompleted == '**NOT SET**'" ),
            dialog.rule.DISABLED, [ model_complete_entry ] )
        ### keep model complete

        #integer of other member number
        dialog.entry.IntEntry( d, 'other_member', 'Other member:' )


        #dimension of thickness
        dialog.dimension.DimensionEntry(
            d, 'thickness', 'thick', 'Thickness:' ).Validate(
            'thickness > 0.', 'Must be greater than 0' )


        #dimension of width
        dialog.dimension.DimensionEntry(
            d, 'width', 'default', 'Width:' ).Validate(
            'width > 0.', 'Must be greater than 0' )

        #rotation of plate around member line
        dialog.entry.FloatEntry(
            d, FloatMemberAttrController( 'Rotation' ), 'Rotation:' )

        ######### change edit screen end  #########
        ###########################################

        dialog_buttons( d )

        can_write = is_read_write_station()

        if not can_write:
            mark_read_only( d )

        return d.Run() and can_write and orig_hash != self.Hash()

    def CreateDependentMaterial( self ):  #only used if you have a preselected member
        try:
            return self._CreateDependentMaterial()
        except Exception, e:
##            raise ## use this line and comment next line when troubleshooting the method
            param.Warning(
                'MyCustomMember::CreateDependentMaterial:' + str( e ) ) #rename
        return False

    def _CreateDependentMaterial( self ):
        if self.this_mtrl_guid is None or self.other_mtrl_guid is None:
            return False
        param.Units( 'inches' )
        b = bolt_add.Bolt()
        this_mtrl = mtrl_list.MtrlByGuid( self.member_number,
                                          self.this_mtrl_guid )
        b.Material = [ this_mtrl ]
        b.Match = [ mtrl_list.MtrlByGuid( self.other_member,
                                          self.other_mtrl_guid ) ]
        h0 = this_mtrl.HoleList()[ 0 ]
        b.Diameter = h0.BoltDiameter
        b.BoltType = h0.BoltType
        b.Direction = 'Out'
        b.SuppressWarnings = 'Yes'
        b.IsFieldBolt = 'Field'
        b.AddMatch()
        return True

    def CreateHoleMatchOther( self, other ): #only used if you have a preselected member
        try:
            return self._CreateHoleMatchOther( other )
        except Exception, e:
##            raise ## use this line and comment next line when troubleshooting the method
            param.Warning( 'MyCustomMember::CreateHoleMatchOther:' + str( e ) ) #rename
        return False
   
    def _CreateHoleMatchOther( self, other ):
        if self.this_mtrl_guid is None or self.other_mtrl_guid is None:
            return False
        param.Units( 'inches' )
        h = hole_add.Hole()
        h.Material = [ mtrl_list.MtrlByGuid( self.other_member,
                                             self.other_mtrl_guid ) ]
        holes = mtrl_list.MtrlByGuid( self.member_number,
                                          self.this_mtrl_guid ).HoleList()
        h.Holes = holes
        h0 = holes[ 0 ]
        h.BoltDiameter = h0.BoltDiameter
        h.BoltType = h0.BoltType
        h.HoleType = 'Standard Round'
        h.Diameter = h.CalculateHoleSize()
        h.SlotLength = h.CalculateSlotLength()
        h.Create()
        return True

    def CreateMaterial( self ):
        try:
            return self._CreateMaterial()
        except Exception, e:
##            raise ## use this line and comment next line when troubleshooting the method
            param.Warning( 'MyCustomMember::CreateMaterial:' + str( e ) ) #rename
        return False
   
    def _CreateMaterial( self ):  #modifiy this to create needed material
        ### note:   for all independent variables, you need a self. before the object
        ### usage:  self.thickness  for the object 'thickness'
        param.Units( 'inches' )
        m = rect_plate.RectPlate()
        m.Thickness = self.thickness
        m.Width = self.width
        m.Point1 = point.Point( self.left_location )
        m.Point2 = point.Point( self.right_location )
        m.MaterialOriginPoint = 'FS'
        m.WorkpointSlopeDistance = m.Point1.dist( m.Point2 )
        m.Member = member.Member( self.member_number )
        m.mtrl_is_main = 'Yes'
        m.Add()
        xform = Transform3D.MemberTransform(
            self.left_location, self.right_location,
            math.radians( m.Member.Rotation ) )
        m.SetTransform( xform )
        self.this_mtrl_guid = m.guid

        h = hole_add.Hole()
        h.Material = [ m ]
        mid = Point3D.Interpolate( self.left_location, self.right_location, .5 )
        center_width = -self.width / 2. * xform.GetBasisVectorY()
        h.pt1 = point.Point( mid + center_width )
        h.face = 'FS Face'
        h.Columns = h.Rows = 1
        h.Locate = 'Center'
        h.BoltDiameter = 1.
        h.BoltType = 'AUTO'
        h.HoleType = 'Standard Round'
        h.Diameter = h.CalculateHoleSize()
        h.SlotLength = h.CalculateSlotLength()
        h.Create()
        return True

    def CreateMaterialOther( self, other ): #only used if you have a preselected member
        try:
            return self._CreateMaterialOther( other )
        except Exception, e:
##            raise ## use this line and comment next line when troubleshooting the method
            param.Warning( 'MyCustomMember::CreateMaterialOther:' + str( e ) ) #rename
        return False
   
    def _CreateMaterialOther( self, other ):
        param.Units( 'inches' )
        m = rect_plate.RectPlate()
        m.Thickness = self.thickness
        m.Width = self.width
        m.Point1 = point.Point( self.left_location )
        m.Point2 = point.Point( self.right_location )
        m.MaterialOriginPoint = 'NS'
        m.WorkpointSlopeDistance = m.Point1.dist( m.Point2 )
        m.Member = member.Member( other )
        m.mtrl_is_main = 'No'
        m.Add()
        m.SetTransform( Transform3D.MemberTransform(
            self.left_location, self.right_location,
            math.radians( member.Member( self.member_number ).Rotation ) ) )
        self.other_mtrl_guid = m.guid
        return True

    def Modifies( self ):
        return [ self.other_member ]

    def Hash( self ):
        h = Hash.Hash()
        for pair in MyCustomMember._arguments[ MyCustomMember._version ]: #rename
            v = getattr( self, pair[ 0 ] )
            if v is None:
                v = 0
            h.Add( v )
        return h.GetResult()