###########################################################################
## EmbedPL_XMLParser.py Version 4.14
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

from xml.dom.minidom import parse, parseString
import os
try:
    import param
except:
    pass

code_version = '4.14'

def convertType(s):
    for func in (int, float):
        try:
            n = func(s)
            return n
        except:
            pass
    return s

class XMLParser(object):
    '''
    Parse an XML document and create data objects for assigning attribute
    names and values in other applications. Each element of argument "args"
    must be a string or tuple of two strings. For the string elements, the
    parser creates an instance attribute named 'string element' consisting
    of a dictionary with attribute name/value pairs. For the tuple elements,
    the parser creates an instance attribute named 'tuple of two strings'[0]
    consisting of a dictionary of dictionaries with 'tuple of two
    strings'[1] attribute value as the keys and values consisting of
    dictionaries of the remaining attribute name/value pairs. Example XML
    document string:

    <?xml version="1.0" ?>
    <EmbedPLData>
      <!-- EmbedPL custom member data file -->
      <code_version>3.02</code_version>
      <_version>0</_version>
      <StudData>
        <studinfo stud_diam="1/4" head_thk="0.1875" head_diam="0.5" />
        <studinfo stud_diam="3/4" head_thk="0.375" head_diam="1.25" />
      </StudData>
      <PlateData>
        <plateinfo nom_depth="12" no_cols="2" no_rows="2" />
        <plateinfo nom_depth="18" no_cols="2" no_rows="4" />
      </PlateData>
      <SetupData>
        <setupinfo func_data_or_last="Last values used" />
        <setupinfo mark_prefix="EM_" />
      </SetupData>
      <!-- Size and location of dialog boxes -->
      <DialogData choiceDlgPos="564x96+95+133" mainDlgPos="577x529+187+209" />
    </EmbedPLData>

    In the above document, we want the StudData, PlateData, and SetupData.
    Create an instance with arguments file name, root element tag,
    'setupinfo', 'DialogData', ('studinfo','stud_diam'), and
    ('plateinfo', 'nom_depth').
    The instance will have attributes 'setupinfo', 'DialogData', 'studinfo',
    and 'plateinfo'.

    Example:
    self.xmlDoc = EmbedPL_XMLParser.XMLParser(setupDataFile,
                                              'EmbedPLData',
                                              'setupinfo',
                                              'DialogData',
                                              ('studinfo', 'stud_diam'),
                                              ('plateinfo', 'nom_depth'))
    Example self.plateinfo with 'nom_depth' of '11' and '10':
    {'11': {'mark_prefix': 'EM_', 'dbaZSpa': 6.0, 'studRows': 2,
            'dbaRows': 0, 'holeRows': 0, 'dbaXSpa': 6.0, 'plate_thk': 0.5,
            'studCols': 2, 'plate_depth': 12.0, 'holeZSpa': 5.5,
            'dbaCols': 0, 'studZSpa': 6.0, 'studXSpa': 6.0, 'holeXSpa': 5.5,
            'holeCols': 0, 'plate_length': 12.0},
     '10': {'mark_prefix': 'EM_', 'dbaZSpa': 6.0, 'studRows': 2,
            'dbaRows': 0, 'holeRows': 0, 'dbaXSpa': 6.0, 'plate_thk': 0.5,
            'studCols': 2, 'plate_depth': 12.0, 'holeZSpa': 5.5,
            'dbaCols': 0, 'studZSpa': 6.0, 'studXSpa': 6.0, 'holeXSpa': 5.5,
            'holeCols': 0, 'plate_length': 12.0}
     }
    Example self.DialogData:
    {'plateOptionDlgPos': '738x323+91+163',
     'mainDlgPos': '577x529+187+209',
     'studOptionDlgPos': '600x177+176+313',
     'plateEditDlgPos': '252x54+237+434',
     'studEditDlgPos': '252x104+236+385',
     'choiceDlgPos': '564x96+157+193'}

    All attribute values must be integer, float, or string and are type cast
    using function convertType().

    Attribute dictionary keys are str. If another type is required (such as
    required to match EmbedPL instance attribute mem.nom_depth), the
    dictionary must be converted.

    The constructor accepts a file name or an XML document string.
    '''

    errorStr = "Invalid pathname argument or XML document string."

    def __init__(self, data, dataID, *args):
        if '<%s' % (dataID) in data:
            # this is the actual XML string
            self.doc = parseString(data)
            self.fn = None
        try:
            f = open(data, 'rb')
            # print "Opening file %s" % s
            self.doc = parseString(f.read())
            f.close()
            self.fn = data
        except IOError, e:
            raise IOError, XMLParser.errorStr
        
        # find the root ELEMENT node
        self.rootNode = self.doc.firstChild
        # check for root element starting with dataID
        self.rootID = self.rootNode.nodeName
        if not self.rootID.startswith(dataID):
            s = "Invalid XML document type - must be %s" % (dataID)
            raise TypeError, s
        
        self.nodeNames = self.getNodeNames(self.rootNode)
        self.dataTagNames = args
        self.dataDict = self.getNodeDict(self.nodeNames, {})
        
        for item in self.dataTagNames:
            if isinstance(item, (list, tuple)):
                name,key = item
                setattr(self, name, self.tagDict(name, key))
            elif isinstance(item, str):
                dd = self.dataDict[item].pop(0)
                for pair in self.dataDict[item]:
                    dd.update(pair)
                setattr(self, item, dd)

    def backToXML(self, encoding='utf-8'):
        ''' Return the document XML string. '''
        return self.doc.toxml().encode(encoding)

    def writeXML(self, fn=None):
        '''Write the XML document to disk. A valid file name must be
        supplied if instance argument "s" is an XML string.'''
        if not fn:
            fn = self.fn
        f = open(fn, 'w')
        f.write(self.backToXML())
        f.close()

    def getAttrNames(self, node):
        '''Return the attribute names of a node.'''
        return [str(s) for s in node.attributes.keys()]

    def getAttrValues(self, node):
        '''Return the values of the attributes in a node.'''
        return [str(node.getAttribute(name)) for name in self.getAttrNames(node)]

    def getAttrs(self, node):
        '''Return the attribute dictionary of a node.'''
        return dict(zip(self.getAttrNames(node),
                        self.getAttrValues(node)))

    def getTextFromElem(self, *args):
        '''Return a list of text found in the child nodes of a parent node,
        discarding whitespace.'''
        textList = []
        for parent in args:
            for n in parent.childNodes:
                # TEXT_NODE - 3
                if n.nodeType == 3 and n.nodeValue.strip():
                    textList.append(str(n.nodeValue.strip()))
        return textList

    def setTextElem(self, parent, text):
        '''Set the text element data of parent element.'''
        success = False
        for n in parent.childNodes:
            # TEXT_NODE - 3
            if n.nodeType == 3:
                n.data = text
                success = True
        return success

    def getElemsByTagName(self, tag):
        '''Return a list of ELEMENT_NODE objects given a tag name.'''
        return self.doc.getElementsByTagName(tag)

    def getNodeNames(self, parent):
        '''Return a list of unique node names found below the parent node.'''
        if parent == None: return None
        names = []
        try:
            for child in parent.childNodes:
                # if ELEMENT_NODE
                if child.nodeType == 1:
                    name = str(child.nodeName).strip()
                    if name not in names:
                        names.append(str(child.nodeName).strip())
                    if child.hasChildNodes():
                        names.extend(self.getNodeNames(child))
            return names
        except: return None

    def getNodeDict(self, nameList, dd={}):
        '''Return a dictionary of node names and attribute values found
        below the parent node. The keys are the node names and the values
        are dictionaries of attribute name/value pairs. Skip any nodes
        that have child nodes.'''
        for name in nameList:
            elemList = self.getElemsByTagName(name)
            for elem in elemList:
                # Skip nodes except ELEMENT_NODE and if no children
                if not elem.hasChildNodes() and elem.nodeType == 1:
                    dd.setdefault(str(elem.nodeName), []).append(self.getAttrs(elem))
        return dd

    def setAttrValue(self, node, attrName, attrValue):
        ''' Set the value of node attrName to attrValue.'''
        if isinstance(node, list):
            for item in node:
                if item.hasAttribute(attrName):
                    item.setAttribute(attrName, attrValue)
        else:
            if node.hasAttribute(attrName):
                node.setAttribute(attrName, attrValue)

    def tagDict(self, name, key):
        ''' Return dictionary of the value of key (as key to subdictionary)
        and remaining key/value pairs as a subdictionary. Remove key
        name/value from subdictionary.'''
        dd0 = {}
        for dd in self.dataDict[name]:
            keys, values = dd.keys(), dd.values()
            idx = keys.index(key)
            keys.pop(idx)
            newKey = values.pop(idx)
            dd0[newKey] = dict(zip(keys, [convertType(s) for s in values]))
        # Warning(str(dd0))
        return dd0

    def updateDataChanges(self, tag, var):
        '''Update the first child text node of a parent node if different
        from var. '''
        x = self.getElemsByTagName(tag)[0]
        xs = self.getTextFromElem(x)[0]
        # param.Warning(', '.join([str(item) for item in [tag, var, xs]]))
        # 'var' may not be str object
        if str(xs) != str(var):
            a = self.setTextElem(x, var)
            if a:
                self.writeXML()

if __name__ == '__main__':

    fn = r'D:\SDS2_7.2\plugins\EmbedPL\EmbedPLData.xml'
        
    doc = XMLParser(fn, 'EmbedPLData', ('anchordata', 'depth'),
                    'setupinfo', 'DialogData',
                    ('studinfo','stud_diam'),
                    ('plateinfo','nom_depth'))
    
    studKeys = ['head_thk', 'head_diam', 'burn_off']
    print
    for key in doc.studinfo:
        print "doc.studinfo key: %s" % (key)
        for item in studKeys:
            print "    %s: %s" % (item, doc.studinfo[key][item])
    print

    plateKeys = ['studCols', 'studRows', 'studXSpa', 'studZSpa',
                 'dbaCols', 'dbaRows', 'dbaXSpa', 'dbaZSpa',
                 'holeCols', 'holeRows', 'holeXSpa', 'holeZSpa',
                 'plate_thk', 'plate_length', 'plate_depth', 'mark_prefix']
    keys = [int(key) for key in doc.plateinfo]
    keys.sort()
    '''
    for key in keys:
        print "doc.plateinfo key: %s" % (key)
        for item in plateKeys:
            print "    %s: %s" % (item, doc.plateinfo[str(key)][item])
    print

    for key in doc.setupinfo:
        print "%s: %s" % (key, doc.setupinfo[key])
        
    for key in doc.DialogData:
        print "%s: %s" % (key, doc.DialogData[key])'''
    
    for key in doc.anchordata:
        print "%s: %s" % (key, doc.anchordata[key])