import os
import subprocess
import math
import maya.cmds as cmds
import maya.mel as mel

class FBXexporter(object):
    
    
    class LayoutSetting(object):
        CLWIDTH = 130
        BWIDTH = 100
        SPACING = 5 
    
    
    def setExportConfig(self):
        mel.eval('FBXExportInAscii -v true') 
        mel.eval('FBXExportTangents -v true')       
        mel.eval('FBXExportAnimationOnly -v false')
        mel.eval('FBXExportBakeComplexAnimation -v true')
        mel.eval('FBXExportCameras -v false')
        mel.eval('FBXExportLights -v false')
        mel.eval('FBXExportEmbeddedTextures -v false')
        mel.eval('FBXExportUpAxis z')   
        mel.eval('FBXExportFileVersion FBX201200')
        
    def button_ExportAll_pressed( self, *args ):
        sceneName = cmds.file( query=True, sceneName=True )
        if not sceneName:
            cmds.confirmDialog( title='Error', message='Save Maya scene file first.', button=['OK','Cancel'], defaultButton='OK', cancelButton='Cancel' )
            return
        root, ext = os.path.splitext( sceneName )
        self.setExportConfig()
        mel.eval('FBXExport -f "'+ root + '.fbx"')
        
        
    def button_ExportSelected_pressed( self, *args ):
        sceneName = cmds.file( query=True, sceneName=True )
        if not sceneName: 
            cmds.confirmDialog( title='Error', message='Save Maya scene file first.', button=['OK','Cancel'], defaultButton='OK', cancelButton='Cancel' )
            return
        if not len( cmds.ls(selection=True) ):
            cmds.confirmDialog( title='Error', message='Active list is empty.', button=['OK','Cancel'], defaultButton='OK', cancelButton='Cancel' )
            return            
        root,ext = os.path.splitext( sceneName )
        self.setExportConfig()
        mel.eval('FBXExport -f "'+ root + '.fbx" -s')
            
            
    def button_OpenCurrentScene_pressed( self, *args ):
        sceneName = cmds.file( query=True, sceneName=True )  
        dir = os.path.dirname( sceneName )
        subprocess.call( 'explorer.exe ' + dir  )


    def button_Close_pressed( self, *args ):
        cmds.deleteUI( self.windowID )


    def button_AddFolder_pressed( self, *args ):
        multipleFilters = 'Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb)'
        dirArray = cmds.fileDialog2( fileFilter=multipleFilters, caption='add a folder', dialogStyle=2, fileMode=3, \
                                     okCaption='Add' )
        if not dirArray:
            return 
        for dir in dirArray:
            for dirPath, dirNames, fileNames in os.walk( dir.encode('ascii','ignore') ):
                for f in fileNames:
                    if f.endswith(".ma") or f.endswith(".mb"):
                        path = dirPath + '/'+ f
                        if not path in self.fileList:
                            self.fileList.append( path )
        cmds.textScrollList('scrollList', edit=True, removeAll=True, append=self.fileList )


    def button_ExportAllFiles_pressed( self, *args ):
        count = len( self.fileList )
        if not count:
            cmds.confirmDialog( title='Error', message='List is empty, add some Maya scene files first.', button=['OK','Cancel'], defaultButton='OK', cancelButton='Cancel' )
        increment = math.floor( 100.0 / count )
        for item in self.fileList:
            print 'item = ' + item
            cmds.file( item, open=True, force=True )
            head, ext = os.path.splitext(item)    
            self.setExportConfig()  
            mel.eval('FBXExport -f "'+ head + '.fbx"')
            cmds.progressBar('ProgressBar', edit=True, step=increment )
            cmds.textScrollList('scrollList', edit=True, removeItem=item )
        cmds.progressBar('ProgressBar', edit=True, progress=100 ) 
        cmds.confirmDialog( title='Exporter', message='Complete.', button=['OK','Cancel'], defaultButton='OK', cancelButton='Cancel' )
        cmds.progressBar('ProgressBar', edit=True, progress=0 )
        self.fileList[:] = []   
        
    def button_DeleteSelected_pressed( self, *args ):
        item = cmds.textScrollList( 'scrollList', query=True, selectItem=True )[0]
        self.fileList.remove( item )
        cmds.textScrollList('scrollList', edit=True, removeAll=True, append=self.fileList )
        
    def InitWindow( self ):
        self._window = cmds.window( self.windowID, title = 'FBX Exporter', sizeable=False, resizeToFitChildren=True ) 
        cmds.columnLayout()
        cmds.rowColumnLayout( numberOfColumns=3, columnWidth=[(1,self.Layout.CLWIDTH), (2,self.Layout.CLWIDTH), (3,self.Layout.CLWIDTH)], \
                              rowSpacing=[(1,self.Layout.SPACING), (2,self.Layout.SPACING), (3,self.Layout.SPACING)] )
        cmds.text( label='Export current scene' )
        cmds.separator(visible=False)   
        cmds.separator(visible=False)
        cmds.button( 'Export All', width=self.Layout.BWIDTH, command=self.button_ExportAll_pressed )
        cmds.button( 'Export Selected', width=self.Layout.BWIDTH, command=self.button_ExportSelected_pressed )
        cmds.button( 'Open Current Scene', width=self.Layout.BWIDTH, command=self.button_OpenCurrentScene_pressed )
        cmds.text( label='Batch export' )
        cmds.separator(visible=False)   
        cmds.separator(visible=False)
        cmds.button( 'Add Folder', width=self.Layout.BWIDTH, command=self.button_AddFolder_pressed )
        cmds.button( 'Export All Files', width=self.Layout.BWIDTH, command=self.button_ExportAllFiles_pressed ) 
        cmds.button( 'Delete Selected', width=self.Layout.BWIDTH, command=self.button_DeleteSelected_pressed )
        cmds.separator()
        cmds.separator()
        cmds.separator()
        cmds.setParent( '..' )
        cmds.rowColumnLayout( numberOfColumns=1, columnWidth=(1,3*self.Layout.CLWIDTH) )
        cmds.progressBar('ProgressBar', width=3*self.Layout.BWIDTH )
        cmds.textScrollList( 'scrollList', allowMultiSelection=False)
        cmds.setParent( '..' )
        cmds.rowColumnLayout( numberOfColumns=3, columnWidth=[(1,self.Layout.CLWIDTH), (2,self.Layout.CLWIDTH), (3,self.Layout.CLWIDTH)], \
                              rowSpacing=[(1,self.Layout.SPACING), (2,self.Layout.SPACING), (3,self.Layout.SPACING)] )
        cmds.separator()
        cmds.separator()
        cmds.separator()
        cmds.separator(visible=False)
        cmds.separator(visible=False)
        cmds.button( 'Close', width=self.Layout.BWIDTH, command=self.button_Close_pressed )
    
    
    def show(self):  
        cmds.showWindow( self._window ) 


    def __init__( self ):
        self.Layout = FBXexporter.LayoutSetting()   
        self.windowID = 'fbxexporterID'
        self.fileList = []  
        if cmds.window( self.windowID , exists = True ):
            cmds.deleteUI( self.windowID ) 
        self.InitWindow() 
   
   
def main():
    exporter = FBXexporter()
    exporter.show()

if __name__ == '__main__':
    main()