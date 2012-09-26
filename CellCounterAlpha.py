#This program is written for Python 2.6 and requires addon modules wxpython, numpy, and scipy
import wx
import numpy as np
import scipy.io

#These are program variables to be manipulated by a slightly savvy user - eventually many will be accessible from gui

#drawing object parameters - UNFINISHED these are not yet changeable and are set as defaults in the code
rectwide = 1
crosswide = 1
crosslong = 15

#set pen colors - UNFINISHED will add menu to chg later
#This is the color used to draw
pencolor = ("BLACK")

#This is the library of colors that can be switched to
pencolor0 = "BLACK"
pencolor1 = "BLUE"
pencolor2 = "GREEN"
pencolor3 = "PURPLE"

#Assume scaled image will be requested, used for achieving consistent output between scaled and unscaled images
unscaledtrue = 0

#default celltype is none (type 0) - cannot be uniquely exported
celltype = 0

#default cell number is zero
cellcounter = 0

#default drawing mode is boxes
drawtype = 1

#set default image size very small so it works with most screens
scalebmpwidth = 640
scalebmpheight = 480


#All arrays used have a blank header line because I found it easiest with my limited python skills - DO NOT CHANGE
cellrecord = np.array([0, 0, 0, 0, 0])
cellrecordscaled = np.array([0, 0, 0, 0, 0])
cellrecorddot = np.array([0, 0, 0])
cellrecorddotscaled = np.array([0, 0, 0])


#This is the main class in which cell marking and image movement takes place
class CellCounter(wx.Frame):
    def __init__(self, parent, mysize):
        wx.Frame.__init__(self, parent, wx.ID_ANY, size=mysize, 
                          title="Cell Counter Alpha")
        # Matrices for adding locations
        self.points = []
        self.scaledpoints = []
        markercount = 0


        # create scrollbar
#        self.scroll=wx.ScrolledWindow(self, -1)
#        self.scroll.SetScrollbars(1, 1, 600, 400)
        
        # create menu, statusbar
        status=self.CreateStatusBar()
        menubar=wx.MenuBar()
        filemenu=wx.Menu()
        popselectmenu=wx.Menu()
        countselectmenu=wx.Menu()
        imagectrlmenu=wx.Menu()
        markerctrlmenu=wx.Menu()

        #assign first menu values
        FILE_SCALED_OPEN = 101
        FILE_UNSCALED_OPEN = 102
        EXPORT_MAT = 103
        EXPORT_MAT_NEURON = 104
        EXPORT_MAT_GLIA = 105
        EXPORT_MAT_BV = 106
        IMPORT_MAT = 107

        #assign second menu values
        NEURON_SELECT = 201
        GLIA_SELECT = 202
        BV_SELECT = 203

        #assign third menu values
        IMAGEMOVE_OFF = 301
        DOT_SWITCH = 302
        RECT_SWITCH = 303

        #assign fifth menu values
        RECTSIZE_SET = 401
        CROSSWIDE_SET = 402
        CROSSLONG_SET = 403

        #assign fourth menu values
        IMAGEMOVE_ON = 501
        MACRO_SHOW = 502

        #create menu contents
        #menu 1 - file handling menu
        filemenu.Append(FILE_SCALED_OPEN,"Open Scaled Image","This will open a scaled image file")
        filemenu.Append(FILE_UNSCALED_OPEN,"Open Unscaled Image","This will open an unscaled image file")
        filemenu.Append(EXPORT_MAT,"Export whole .mat","This will export a complete .mat file")
        filemenu.Append(EXPORT_MAT_NEURON,"Export Neuron .mat","This will export a .mat file containing neurons")
        filemenu.Append(EXPORT_MAT_GLIA,"Export Glia .mat","This will export a .mat file containing glia")
        filemenu.Append(EXPORT_MAT_BV,"Export BV .mat","This will export a .mat file containing cells in a blood vessel")
        filemenu.Append(IMPORT_MAT,"Import tracing from .mat","This will import a .mat file not selected for celltype")

        #menu 2 - counting target selection menu
        popselectmenu.Append(NEURON_SELECT,"Neurons","This will select neurons to count")
        popselectmenu.Append(GLIA_SELECT,"Glia","This will select glia to count")
        popselectmenu.Append(BV_SELECT,"Blood Vessel","This will select blood vessel cells to count")

        #menu 3 - counting methods menu
        countselectmenu.Append(IMAGEMOVE_OFF,"Mark Objects",
                             "This turns on marking and turns off image move,drag like touchscreen to move")
        countselectmenu.Append(DOT_SWITCH,"Point Mode","This will count objects with a single point")
        countselectmenu.Append(RECT_SWITCH,"Box Mode","This will count objects with a surrounding box")

        #menu 4 - pen color and cursor control tools
        markerctrlmenu.Append(RECTSIZE_SET,"Change box size","This changes the thickness of your box lines")
        markerctrlmenu.Append(CROSSWIDE_SET,"Change cross width","This changes the thickness of your point cross lines")
        markerctrlmenu.Append(CROSSLONG_SET,"Change cross length","This changes the length of your point cross lines")
        
        #menu 5 - movement and macro view menu
        imagectrlmenu.Append(IMAGEMOVE_ON,"Move Image","This turns on image move mode and turns off marking")
        imagectrlmenu.Append(MACRO_SHOW,"Macro View","This turns macroview off and on")

        #menu headers
        menubar.Append(filemenu,"File")
        menubar.Append(popselectmenu,"Select Pop")
        menubar.Append(countselectmenu,"Count Objects")
        menubar.Append(markerctrlmenu,"Change Markers")
        menubar.Append(imagectrlmenu,"Move Image")
        self.SetMenuBar(menubar)
        
        #assign menu functions
        #menu 1
        self.Bind(wx.EVT_MENU, self.ScaledImageOpen, id=FILE_SCALED_OPEN)
        self.Bind(wx.EVT_MENU, self.UnscaledImageOpen, id=FILE_UNSCALED_OPEN)
        self.Bind(wx.EVT_MENU, self.ExportMat, id=EXPORT_MAT)
        self.Bind(wx.EVT_MENU, self.ExportMatNeuron, id=EXPORT_MAT_NEURON)
        self.Bind(wx.EVT_MENU, self.ExportMatGlia, id=EXPORT_MAT_GLIA)
        self.Bind(wx.EVT_MENU, self.ExportMatBV, id=EXPORT_MAT_BV)
        self.Bind(wx.EVT_MENU, self.ImportMat, id=IMPORT_MAT)

        #menu 2
        self.Bind(wx.EVT_MENU, self.NeuronButton, id=NEURON_SELECT)
        self.Bind(wx.EVT_MENU, self.GliaButton, id=GLIA_SELECT)
        self.Bind(wx.EVT_MENU, self.BVButton, id=BV_SELECT)

        #menu 3
        self.Bind(wx.EVT_MENU, self.ImageMoveOff, id=IMAGEMOVE_OFF)
        self.Bind(wx.EVT_MENU, self.DotSwitch, id=DOT_SWITCH)
        self.Bind(wx.EVT_MENU, self.RectSwitch, id=RECT_SWITCH)

        #menu 4
        self.Bind(wx.EVT_MENU, self.RectSizeSet, id=RECTSIZE_SET)
        self.Bind(wx.EVT_MENU, self.CrossWideSet, id=CROSSWIDE_SET)
        self.Bind(wx.EVT_MENU, self.CrossLongSet, id=CROSSLONG_SET)

        #menu 5
        self.Bind(wx.EVT_MENU, self.ImageMoveOn, id=IMAGEMOVE_ON)
        self.Bind(wx.EVT_MENU, self.MacroShow, id=MACRO_SHOW)

        
        #mouseclick setup - default is rectangle counting mode
        self.Bind(wx.EVT_LEFT_DOWN, self.DrawRect)
        self.Bind(wx.EVT_RIGHT_DOWN, self.EraseRect)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_ENTER_WINDOW, self.create_crosshair)

        #keyboard setup for fast celltype switching
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

        #load default frame
        self.SetBackgroundColour("WHITE")
        self.Centre()
        self.Show(True)
        self.buffer = wx.EmptyBitmap(1600, 1200)  # draw to this
        imagebuffer = wx.EmptyBitmap(1600, 1200) # spare for image repair/move
        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        dc.Clear()  # black window otherwise
        dc.SetPen(wx.Pen(pencolor, 2, wx.SOLID))

    def ScaledImageOpen(self, event):
        global scalebmpwidth
        global scalebmpheight
        global unscaledtrue
        global imagebuffer
        
        self.photoTxt = wx.TextCtrl(self, size=(200,-1))
        wildcard = "JPEG files (*.jpg)|*.jpg"
        dialog = wx.FileDialog(None, "Choose a file",
                               wildcard=wildcard,
                               style=wx.OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            self.photoTxt.SetValue(dialog.GetPath())
        dialog.Destroy()
        path = self.photoTxt.GetValue()
        self.photoTxt.Destroy()
        
        bmp=wx.Image(path, wx.BITMAP_TYPE_ANY)
        # this is the wxPython drawing surface/canvas
        scalebmpwidth = float(bmp.GetWidth())
        scalebmpheight = float(bmp.GetHeight())
        bmpscale = bmp.Scale(scalebmpwidth / scalebmpheight * screensize[1] *
                            .80,screensize[1] * .80)
        bmp2 = wx.BitmapFromImage(bmpscale)
        imagebuffer = wx.EmptyBitmap(scalebmpwidth / scalebmpheight * 
                                     screensize[1] * .80,
                                     screensize[1]*.80)
        dc2 = wx.BufferedDC(wx.MemoryDC(), imagebuffer)
        dc2.DrawBitmap(bmp2, 0, 0, True)
        self.buffer = wx.EmptyBitmap(scalebmpwidth / scalebmpheight * 
                                     screensize[1] * .80,
                                     screensize[1] * .80)
        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        dc.DrawBitmap(bmp2, 0, 0, True)
        unscaledtrue=0
        self.Refresh()

    def UnscaledImageOpen(self,event):
        global scalebmpwidth
        global scalebmpheight

        global unscaledtrue
        global currentlocation
        global imagebuffer
        
        self.photoTxt = wx.TextCtrl(self, size=(200,-1))
        wildcard = "JPEG files (*.jpg)|*.jpg"
        dialog = wx.FileDialog(None, "Choose a file",
                               wildcard=wildcard,
                               style=wx.OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            self.photoTxt.SetValue(dialog.GetPath())
        dialog.Destroy()
        path = self.photoTxt.GetValue()
        self.photoTxt.Destroy()
        
        bmp=wx.Image(path, wx.BITMAP_TYPE_ANY)
        scalebmpwidth = float(bmp.GetWidth())
        scalebmpheight = float(bmp.GetHeight())
        bmp2 = wx.BitmapFromImage(bmp)
        imagebuffer = wx.EmptyBitmap(scalebmpwidth, scalebmpheight)
        dc2 = wx.BufferedDC(wx.MemoryDC(), imagebuffer)
        dc2.DrawBitmap(bmp2, 0, 0, True)
        self.buffer = wx.EmptyBitmap(scalebmpwidth,scalebmpheight)
        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        dc.DrawBitmap(bmp2, 0, 0, True)

        #upper left coordinates of picture
        currentlocation = [0,0]
        unscaledtrue = 1
        self.Refresh()
        
    def DrawRect(self,event):
        global cellrecord
        global cellrecordscaled
        global cellcounter
        
        self.points.append(event.GetPosition())
        x1, y1 = self.points[0]
        if len(self.points) == 1:
            dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
            dc.SetPen(wx.Pen(pencolor, rectwide, wx.SOLID))
            dc.DrawLine(x1, y1, (x1 + 1), (y1 + 1))
            self.Update()
        if len(self.points) == 2:
            dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
            dc.SetPen(wx.Pen(pencolor, rectwide, wx.SOLID))
            x1, y1 = self.points[0]
            x2, y2 = self.points[1]
            dc.DrawLine(x1, y1, x1, y2)
            dc.DrawLine(x1, y2, x2, y2)
            dc.DrawLine(x2, y2, x2, y1)
            dc.DrawLine(x2, y1, x1, y1)
            self.Update()
            celladd = np.array([x1, y1, x2, y2, celltype])
            cellrecord = np.vstack((cellrecord, celladd))
            
            #return coords to original image scale for output if image has been rescaled
            if unscaledtrue == 0:
                x1scaled = int(x1 * scalebmpwidth / 
                              (scalebmpwidth / scalebmpheight * 
                               screensize[1] * .80))
                y1scaled = int(y1 * scalebmpheight /(screensize[1] * .80))
                x2scaled = int(x2 * scalebmpwidth /(scalebmpwidth / scalebmpheight * 
                                                    screensize[1] * .80))
                y2scaled = int(y2 * scalebmpheight /(screensize[1]*.80))
            if unscaledtrue==1:
                x1scaled = x1 + currentlocation[0]
                y1scaled = y1 + currentlocation[1]
                x2scaled = x2 + currentlocation[0]
                y2scaled = y2 + currentlocation[1]
            celladdscaled = np.array([x1scaled, y1scaled, x2scaled, y2scaled, celltype])
            cellrecordscaled = np.vstack((cellrecordscaled, celladdscaled))
            print cellrecordscaled
            print cellrecord
            cellcounter += 1
            self.points = []

    def EraseRect(self, event):
        global cellrecord
        global cellcounter
        global cellrecordscaled

        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        dc2 = wx.BufferedDC(wx.MemoryDC(), imagebuffer)
        
        cutrow = np.alen(cellrecordscaled) - 1

        if unscaledtrue == 0:
            x1 = np.rint(cellrecord[cutrow,0])
            y1 = np.rint(cellrecord[cutrow,1])
            x2 = np.rint(cellrecord[cutrow,2])
            y2 = np.rint(cellrecord[cutrow,3])
            
            #replace left side
            dc.Blit(x1-1-(rectwide/2), y1-1-(rectwide/2), (rectwide+2), (y2-y1)+2+rectwide,
                    dc2, x1-1-(rectwide/2), y1-1-(rectwide/2),
                    rop=wx.COPY, useMask=False, xsrcMask=-1, ysrcMask=-1)
            #replace top side
            dc.Blit(x1-1-(rectwide/2), y1-1-(rectwide/2), (x2-x1)+2+rectwide, (rectwide+2),
                    dc2, x1-1-(rectwide/2), y1-1-(rectwide/2),
                    rop=wx.COPY, useMask=False, xsrcMask=-1, ysrcMask=-1)
            #replace right side
            dc.Blit(x2-1-(rectwide/2), y1-1-(rectwide/2), (rectwide+2), (y2-y1)+2+rectwide,
                    dc2, x2-1-(rectwide/2), y1-1-(rectwide/2),
                    rop=wx.COPY, useMask=False, xsrcMask=-1, ysrcMask=-1)
            #replace bottom side
            dc.Blit(x1-1-(rectwide/2), y2-1-(rectwide/2), (x2-x1)+2+rectwide, (rectwide+2),
                    dc2, x1-1-(rectwide/2), y2-1-(rectwide/2),
                    rop=wx.COPY, useMask=False, xsrcMask=-1, ysrcMask=-1)
        if unscaledtrue==1:
            x1=np.rint(cellrecordscaled[cutrow,0])-currentlocation[0]
            y1=np.rint(cellrecordscaled[cutrow,1])-currentlocation[1]
            x2=np.rint(cellrecordscaled[cutrow,2])-currentlocation[0]
            y2=np.rint(cellrecordscaled[cutrow,3])-currentlocation[1]
            
            #replace left side
            dc.Blit(x1-1-(rectwide/2), y1-1-(rectwide/2), (rectwide+2), (y2-y1)+2+rectwide,
                    dc2, x1-1-(rectwide/2)+currentlocation[0], y1-1-rectwide/2+currentlocation[1],
                    rop=wx.COPY, useMask=False, xsrcMask=-1, ysrcMask=-1)
            #replace top side
            dc.Blit(x1-1-(rectwide/2), y1-1-(rectwide/2), (x2-x1)+2+rectwide, (rectwide+2),
                    dc2, x1-1-(rectwide/2)+currentlocation[0], y1-1-(rectwide/2)+currentlocation[1],
                    rop=wx.COPY, useMask=False, xsrcMask=-1, ysrcMask=-1)
            #replace right side
            dc.Blit(x2-1-(rectwide/2), y1-1-(rectwide/2), (rectwide+2), (y2-y1)+2+rectwide,
                    dc2, x2-1-(rectwide/2)+currentlocation[0], y1-1-(rectwide/2)+currentlocation[1],
                    rop=wx.COPY, useMask=False, xsrcMask=-1, ysrcMask=-1)
            #replace bottom side
            dc.Blit(x1-1-(rectwide/2), y2-1-(rectwide/2), (x2-x1)+2+rectwide, (rectwide+2),
                    dc2, x1-1-(rectwide/2)+currentlocation[0], y2-1-(rectwide/2)+currentlocation[1],
                    rop=wx.COPY, useMask=False, xsrcMask=-1, ysrcMask=-1)
        
        self.Update()     
        cellrecord = np.vstack((cellrecord[:cutrow]))
        cellrecordscaled = np.vstack((cellrecordscaled[:cutrow]))
        cellcounter -= 1

    def DrawDot(self, event):
        global cellrecorddot
        global cellrecorddotscaled
        global cellcounter
        
        self.points.append(event.GetPosition())
        x1, y1 = self.points[0]
        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        dc.SetPen(wx.Pen(pencolor, crosswide, wx.SOLID))
        dc.DrawLine(x1 - (crosslong / 2), y1, x1 + (crosslong / 2), y1)
        dc.DrawLine(x1, y1- (crosslong / 2), x1, y1 + (crosslong / 2))
        self.Update()
        celladddot=np.array([x1, y1, celltype])
        cellrecorddot=np.vstack((cellrecorddot, celladddot))            
            #return coords to original image scale for output if image has been rescaled
        if unscaledtrue == 0:
            x1scaled = int(x1 * scalebmpwidth / 
                          (scalebmpwidth / 
                           scalebmpheight * screensize[1] * .80))
            y1scaled = int(y1 * scalebmpheight / (screensize[1]*.80))
        if unscaledtrue == 1:
            x1scaled = x1+currentlocation[0]
            y1scaled = y1+currentlocation[1]
        celladddotscaled = np.array([x1scaled, y1scaled, celltype])
        cellrecorddotscaled = np.vstack((cellrecorddotscaled, 
                                         celladddotscaled))
        print cellrecorddotscaled
        print cellrecorddot
        cellcounter += 1
        self.points = []

    def EraseDot(self, event):
        global cellrecorddot
        global cellrecorddotscaled
        global cellcounter

        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        dc2 = wx.BufferedDC(wx.MemoryDC(), imagebuffer)
        
        cutrow=np.alen(cellrecorddotscaled)-1

        if unscaledtrue==0:
            x1=np.rint(cellrecorddot[cutrow,0])
            y1=np.rint(cellrecorddot[cutrow,1])
            #replace horizontal line
            dc.Blit(x1-1-(crosslong/2), y1-1-(crosswide/2), (crosslong+2), (crosswide+2),
                    dc2, x1-(crosslong/2), y1-1-(crosswide/2),
                    rop=wx.COPY, useMask=False, xsrcMask=-1, ysrcMask=-1)
            #replace vertical line
            dc.Blit(x1-1-(crosswide/2), y1-1-(crosslong/2), (crosswide+2), (crosslong+2),
                    dc2, x1-1-(crosswide/2), y1-1-(crosslong/2),
                    rop=wx.COPY, useMask=False, xsrcMask=-1, ysrcMask=-1)
        if unscaledtrue==1:
            x1=np.rint(cellrecorddotscaled[cutrow,0])-currentlocation[0]
            y1=np.rint(cellrecorddotscaled[cutrow,1])-currentlocation[1]
            #replace horizontal line
            dc.Blit(x1-1-(crosslong/2), y1-1-(crosswide/2), (crosslong+2), (crosswide+2),
                    dc2, x1-1-(crosslong/2)+currentlocation[0], y1-1-(crosswide/2)+currentlocation[1],
                    rop=wx.COPY, useMask=False, xsrcMask=-1, ysrcMask=-1)
            #replace vertical line
            dc.Blit(x1-1-(crosswide/2), y1-1-(crosslong/2), (crosswide+2), (crosslong+2),
                    dc2, x1-1-(crosswide/2)+currentlocation[0], y1-1-(crosslong/2)+currentlocation[1],
                    rop=wx.COPY, useMask=False, xsrcMask=-1, ysrcMask=-1)
        self.Update()     
        cellrecorddot = np.vstack((cellrecorddot[:cutrow]))
        cellrecorddotscaled = np.vstack((cellrecorddotscaled[:cutrow]))
        cellcounter -= 1

    def MouseMove(self, event):
        global selflocation
        
        selflocation=[]
        selflocation.append(event.GetPosition())
        self.Bind(wx.EVT_LEFT_UP, self.MouseStopRedraw)

    def MouseStopRedraw(self, event):
        #Note that this only works with unscaled images!  Scaled images should fit on a single screen and not require movement.
        global selflocation
        global currentlocation
        global cellrecordscaled
        global cellrecorddotscaled
        global pencolor

        #import current image (dc), full image stored in memory (dc2)
        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        dc.Clear()
        dc2 = wx.BufferedDC(wx.MemoryDC(), imagebuffer)

        #get location of movement
        selflocation.append(event.GetPosition())
        x1,y1 = selflocation[0]
        x2,y2 = selflocation[1]
        selflocation = []
        currentlocation[0] = currentlocation[0] + (x1 - x2)
        currentlocation[1] = currentlocation[1] + (y1 - y2)

        #redraw the correct image
        dc.Blit(0, 0, 1600, 1200, dc2, currentlocation[0], currentlocation[1],
                rop=wx.COPY, useMask=False, xsrcMask=-1, ysrcMask=-1)

        #move rectangle objects
        checkcountedrect=np.ndim(cellrecordscaled) 
        if checkcountedrect == 1:
            pass
        else:
            length = np.alen(cellrecordscaled) - 1
            retrace = 1
            while retrace <= length:
                x1 = np.array((cellrecordscaled[retrace,0])) - currentlocation[0]
                y1 = np.array((cellrecordscaled[retrace,1])) - currentlocation[1]
                x2 = np.array((cellrecordscaled[retrace,2])) - currentlocation[0]
                y2 = np.array((cellrecordscaled[retrace,3])) - currentlocation[1]
                celltype = np.array((cellrecordscaled[retrace,4]))
                if celltype == 0:
                    pencolor = pencolor0
                if celltype == 1:
                    pencolor = pencolor1
                if celltype == 2:
                    pencolor = pencolor2
                if celltype == 3:
                    pencolor = pencolor3
                dc.SetPen(wx.Pen(pencolor, rectwide, wx.SOLID))
                dc.DrawLine(x1, y1, x1, y2)
                dc.DrawLine(x1, y2, x2, y2)
                dc.DrawLine(x2, y2, x2, y1)
                dc.DrawLine(x2, y1, x1, y1)
                retrace += 1
        
        # move dot objects
        checkcounteddot=np.ndim(cellrecorddotscaled)
        if checkcounteddot == 1:
            pass
        else:
            length = np.alen(cellrecorddotscaled) - 1
            retrace = 1
            while retrace <= length:
                x1 = np.array((cellrecorddotscaled[retrace,0])) - currentlocation[0]
                y1 = np.array((cellrecorddotscaled[retrace,1])) - currentlocation[1]
                celltype = np.array((cellrecorddotscaled[retrace,2]))
                if celltype == 0:
                    pencolor = pencolor0
                if celltype == 1:
                    pencolor = pencolor1
                if celltype == 2:
                    pencolor = pencolor2
                if celltype == 3:
                    pencolor = pencolor3
                dc.SetPen(wx.Pen(pencolor, crosswide, wx.SOLID))
                dc.DrawLine(x1- (crosslong / 2), y1, x1 + (crosslong / 2), y1)
                dc.DrawLine(x1, y1 - (crosslong / 2), x1, y1 + (crosslong / 2))
                retrace += 1
                
        self.Update()

        self.Bind(wx.EVT_LEFT_DOWN, self.MouseMove)

    def OnKeyDown(self, event):
        global pencolor
        global celltype
        code = event.GetKeyCode()
        if code == 49:
            pencolor = ("BLUE")
            celltype = 1
        if code == 50:
            pencolor = ("GREEN")
            celltype = 2
        if code == 51:
            pencolor = ("PURPLE")
            celltype = 3
        else:
            pass
        
    def NeuronButton(self, event):
        global pencolor
        global celltype
        pencolor = ("BLUE")
        celltype = 1

    def GliaButton(self, event):
        global pencolor
        global celltype
        pencolor = ("GREEN")
        celltype = 2

    def BVButton(self, event):
        global pencolor
        global celltype
        pencolor = ("PURPLE")
        celltype = 3

    def ExportMat(self, event):
        global cellrecord
        global cellrecordscaled
        global cellcounter
        
        self.saveTxt = wx.TextCtrl(self, size=(200,-1))
        dialog = wx.FileDialog(None, "Enter", style=wx.SAVE)
        if dialog.ShowModal() == wx.ID_OK:
            self.saveTxt.SetValue(dialog.GetPath())
        dialog.Destroy()
        path = self.saveTxt.GetValue()
        self.saveTxt.Destroy()

        #export rectangle tracings - note that both dot and rect are currently saved to the same .mat file as different variables, cellexport and cellpointexport
        checkcountedrect=np.ndim(cellrecordscaled)
        if checkcountedrect == 1:
            pass
        else:
            cellexport=np.vstack((cellrecordscaled[1:]))
            scipy.io.savemat(path, mdict={'cellexport': cellexport}, appendmat=True)

        #export dot tracings
        checkcounteddot=np.ndim(cellrecorddotscaled)
        if checkcounteddot == 1:
            pass
        else:
            cellpointexport=np.vstack((cellrecorddotscaled[1:]))
            scipy.io.savemat(path, mdict={'cellpointexport': cellpointexport}, appendmat=True)
                
    def ExportMatNeuron(self, event):
        global cellrecord
        
        self.saveTxt = wx.TextCtrl(self, size=(200,-1))
        dialog = wx.FileDialog(None, "Enter", style=wx.FD_SAVE)
        if dialog.ShowModal() == wx.ID_OK:
            self.saveTxt.SetValue(dialog.GetPath())
        dialog.Destroy()
        path = self.saveTxt.GetValue()
        self.saveTxt.Destroy()

        #export rectangle tracings
        checkcountedrect=np.ndim(cellrecordscaled)
        if checkcountedrect == 1:
            pass
        else:
            checkcell = np.alen(cellrecordscaled)
            singlepass = 0
            neuronarray = np.array([0,0,0,0])
            while singlepass < checkcell:
                if np.array((cellrecordscaled[singlepass,4])) == 1:
                    neuronadd = np.array((cellrecordscaled[singlepass,0:4]))
                    neuronarray = np.vstack((neuronarray,neuronadd))
                singlepass += 1
            cellexport = np.vstack((neuronarray[1:]))
            scipy.io.savemat(path, mdict={'cellexport': cellexport}, appendmat=True)

        #export dot tracings
        checkcounteddot=np.ndim(cellrecorddotscaled)
        if checkcounteddot == 1:
            pass
        else:
            checkcell = np.alen(cellrecorddotscaled)
            singlepass = 0
            neuronarray = np.array([0,0])
            while singlepass < checkcell:
                if np.array((cellrecorddotscaled[singlepass,2])) == 1:
                    neuronadd = np.array((cellrecorddotscaled[singlepass,0:2]))
                    neuronarray = np.vstack((neuronarray,neuronadd))
                singlepass += 1
            cellpointexport = np.vstack((neuronarray[1:]))
            scipy.io.savemat(path, mdict={'cellpointexport': cellpointexport}, appendmat=True)

    def ExportMatGlia(self, event):
        global cellrecord

        self.saveTxt = wx.TextCtrl(self, size=(200,-1))
        dialog = wx.FileDialog(None, "Enter", style=wx.FD_SAVE)
        if dialog.ShowModal() == wx.ID_OK:
            self.saveTxt.SetValue(dialog.GetPath())
        dialog.Destroy()
        path = self.saveTxt.GetValue()
        self.saveTxt.Destroy()

        #export rectangle tracings
        checkcountedrect=np.ndim(cellrecordscaled)
        if checkcountedrect == 1:
            pass
        else:
            checkcell = np.alen(cellrecordscaled)
            singlepass = 0
            gliaarray = np.array([0,0,0,0])
            while singlepass < checkcell:
                if np.array((cellrecordscaled[singlepass,4])) == 2:
                    gliaadd = np.array((cellrecordscaled[singlepass,0:4]))
                    gliaarray = np.vstack((gliaarray,gliaadd))
                singlepass += 1
            cellexport = np.vstack((gliaarray[1:]))
            scipy.io.savemat(path, mdict={'cellexport': cellexport}, appendmat=True)

        #export dot tracings
        checkcounteddot=np.ndim(cellrecorddotscaled)
        if checkcounteddot == 1:
            pass
        else:
            checkcell = np.alen(cellrecorddotscaled)
            singlepass = 0
            gliaarray = np.array([0,0])
            while singlepass < checkcell:
                if np.array((cellrecorddotscaled[singlepass,2])) == 2:
                    gliaadd = np.array((cellrecorddotscaled[singlepass,0:2]))
                    gliaarray = np.vstack((gliaarray,gliaadd))
                singlepass += 1
            cellpointexport = np.vstack((gliaarray[1:]))
            scipy.io.savemat(path, mdict={'cellpointexport': cellpointexport}, appendmat=True)

    def ExportMatBV(self, event):
        global cellrecord

        self.saveTxt = wx.TextCtrl(self, size=(200,-1))
        dialog = wx.FileDialog(None, "Enter", style=wx.FD_SAVE)
        if dialog.ShowModal() == wx.ID_OK:
            self.saveTxt.SetValue(dialog.GetPath())
        dialog.Destroy()
        path = self.saveTxt.GetValue()
        self.saveTxt.Destroy()

        #export rectangle tracings
        checkcountedrect=np.ndim(cellrecordscaled)
        if checkcountedrect == 1:
            pass
        else:
            checkcell = np.alen(cellrecordscaled)
            singlepass = 0
            bvarray = np.array([0,0,0,0])
            while singlepass < checkcell:
                if np.array((cellrecordscaled[singlepass,4])) == 3:
                    bvadd = np.array((cellrecordscaled[singlepass,0:4]))
                    bvarray = np.vstack((bvarray,bvadd))
                singlepass += 1
            cellexport = np.vstack((bvarray[1:]))
            scipy.io.savemat(path, mdict={'cellexport': cellexport}, appendmat=True)

        #export dot tracings
        checkcounteddot=np.ndim(cellrecorddotscaled)
        if checkcounteddot == 1:
            pass
        else:
            checkcell = np.alen(cellrecorddotscaled)
            singlepass = 0
            bvarray = np.array([0,0])
            while singlepass < checkcell:
                if np.array((cellrecorddotscaled[singlepass,2])) == 3:
                    bvadd = np.array((cellrecorddotscaled[singlepass,0:2]))
                    bvarray = np.vstack((bvarray,bvadd))
                singlepass += 1
            cellpointexport = np.vstack((bvarray[1:]))
            scipy.io.savemat(path, mdict={'cellpointexport': cellpointexport}, appendmat=True)

    def ImportMat(self,event):
        global cellrecordscaled
        global cellrecorddotscaled
        global cellrecord

        #UNFINISHED need to clear image of current points
        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        dc2 = wx.BufferedDC(wx.MemoryDC(), imagebuffer)
        
        self.loadTxt = wx.TextCtrl(self, size=(200,-1))
        dialog = wx.FileDialog(None, "Enter", style=wx.OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            self.loadTxt.SetValue(dialog.GetPath())
        dialog.Destroy()
        path = self.loadTxt.GetValue()
        self.loadTxt.Destroy()
        rawimport = scipy.io.loadmat(path, mdict=None, appendmat=True)
        print rawimport

        #redraw a clean image
        dc.Blit(0, 0, 1600, 1200, dc2, currentlocation[0], currentlocation[1],
                rop=wx.COPY, useMask=False, xsrcMask=-1, ysrcMask=-1)

        try:
            cellrecordappend = rawimport['cellexport']
            rectdatatest = 1
        except:
            rectdatatest = 0
        try:
            cellrecorddotappend = rawimport['cellpointexport']
            dotdatatest = 1
        except:
            dotdatatest = 0
        
        cellrecordscaled = np.array([0,0,0,0,0])
        cellrecord = np.array([0,0,0,0,0])
        cellrecorddotscaled = np.array([0,0,0])
        cellrecorddot = np.array([0,0,0])

        #draw rectangle objects
        if rectdatatest == 0:
            pass
        
        else:
            cellrecordscaled = np.vstack((cellrecordscaled,cellrecordappend))
            cellnumber = np.alen(cellrecordscaled)
            drawcounter = 1
            #If the image is scaled:
            if unscaledtrue == 0:                 
                while drawcounter < cellnumber:
                    
                    #convert cellscaled to cellrecord 
                    x1 = np.array((cellrecordscaled[drawcounter,0]))
                    y1 = np.array((cellrecordscaled[drawcounter,1]))
                    x2 = np.array((cellrecordscaled[drawcounter,2]))
                    y2 = np.array((cellrecordscaled[drawcounter,3]))
                    celltype = np.array((cellrecordscaled[drawcounter,4]))
                    x1scaleddown = int(x1/(scalebmpwidth/(scalebmpwidth/scalebmpheight*screensize[1]*.80)))
                    y1scaleddown = int(y1/(scalebmpheight/(screensize[1]*.80)))
                    x2scaleddown = int(x2/(scalebmpwidth/(scalebmpwidth/scalebmpheight*screensize[1]*.80)))
                    y2scaleddown = int(y2/(scalebmpheight/(screensize[1]*.80)))
                    cellrecordadd = np.array(([x1scaleddown, y1scaleddown,
                                               x2scaleddown, y2scaleddown, celltype])) 
                    cellrecord = np.vstack((cellrecord,cellrecordadd))
                    
                    #draw rescaled cellrecord
                    if celltype == 0:
                        pencolor = pencolor0
                    if celltype == 1:
                        pencolor = pencolor1
                    if celltype == 2:
                        pencolor = pencolor2
                    if celltype == 3:
                        pencolor = pencolor3
                    dc.SetPen(wx.Pen(pencolor, rectwide, wx.SOLID))
                    dc.DrawLine(x1scaleddown, y1scaleddown, x1scaleddown, y2scaleddown)
                    dc.DrawLine(x1scaleddown, y2scaleddown, x2scaleddown, y2scaleddown)
                    dc.DrawLine(x2scaleddown, y2scaleddown, x2scaleddown, y1scaleddown)
                    dc.DrawLine(x2scaleddown, y1scaleddown, x1scaleddown, y1scaleddown)
                    drawcounter += 1

            #If the image is unscaled:
            if unscaledtrue == 1:
                cellrecord = cellrecordscaled
                while drawcounter < cellnumber:
                    x1 = np.array((cellrecordscaled[drawcounter,0]))-currentlocation[0]
                    y1 = np.array((cellrecordscaled[drawcounter,1]))-currentlocation[1]
                    x2 = np.array((cellrecordscaled[drawcounter,2]))-currentlocation[0]
                    y2 = np.array((cellrecordscaled[drawcounter,3]))-currentlocation[1]
                    celltype = np.array((cellrecordscaled[drawcounter,4]))
                    if celltype == 0:
                        pencolor = pencolor0
                    if celltype == 1:
                        pencolor = pencolor1
                    if celltype == 2:
                        pencolor = pencolor2
                    if celltype == 3:
                        pencolor = pencolor3
                    dc.SetPen(wx.Pen(pencolor, rectwide, wx.SOLID))
                    dc.DrawLine(x1, y1, x1, y2)
                    dc.DrawLine(x1, y2, x2, y2)
                    dc.DrawLine(x2, y2, x2, y1)
                    dc.DrawLine(x2, y1, x1, y1)
                    drawcounter += 1
                    
        #Draw dot objects
        if dotdatatest == 0:
            pass

        else:
            cellrecorddotscaled = np.vstack((cellrecorddotscaled, 
                                             cellrecorddotappend))
            cellnumber = np.alen(cellrecorddotscaled)
            drawcounter = 1

            #If the image is scaled
            if unscaledtrue == 0:
                while drawcounter < cellnumber:
                    
                    #Convert cellscaled to cellrecord 
                    x1 = np.array((cellrecorddotscaled[drawcounter,0]))
                    y1 = np.array((cellrecorddotscaled[drawcounter,1]))
                    celltype = np.array((cellrecorddotscaled[drawcounter,2]))
                    x1scaleddown = int(x1 / (scalebmpwidth / 
                                            (scalebmpwidth / 
                                             scalebmpheight * 
                                             screensize[1] * .80)))
                    y1scaleddown = int(y1 / (scalebmpheight / 
                                             (screensize[1] * .80)))
                    cellrecorddotadd = np.array(([x1scaleddown, y1scaleddown, 
                                                  celltype])) 
                    cellrecorddot = np.vstack((cellrecorddot, 
                                               cellrecorddotadd))
                    
                    #Draw rescaled cellrecord
                    if celltype == 0:
                        pencolor = pencolor0
                    if celltype == 1:
                        pencolor = pencolor1
                    if celltype == 2:
                        pencolor = pencolor2
                    if celltype == 3:
                        pencolor = pencolor3
                    dc.SetPen(wx.Pen(pencolor, 1, wx.SOLID))
                    dc.DrawLine(x1scaleddown - 5, y1scaleddown, x1scaleddown + 5, y1scaleddown)
                    dc.DrawLine(x1scaleddown, y1scaleddown - 5, x1scaleddown, y1scaleddown + 5)
                    drawcounter += 1

            #If the image is unscaled
            if unscaledtrue == 1:
                cellrecorddot = cellrecorddotscaled
                while drawcounter < cellnumber:
                    x1 = np.array((cellrecorddotscaled[drawcounter,0])) - currentlocation[0]
                    y1 = np.array((cellrecorddotscaled[drawcounter,1])) - currentlocation[1]
                    celltype = np.array((cellrecorddotscaled[drawcounter,2]))
                    if celltype == 0:
                        pencolor = pencolor0
                    if celltype == 1:
                        pencolor = pencolor1
                    if celltype == 2:
                        pencolor = pencolor2
                    if celltype == 3:
                        pencolor = pencolor3
                    dc.SetPen(wx.Pen(pencolor, 1, wx.SOLID))
                    dc.DrawLine(x1 - 5, y1, x1 + 5, y1)
                    dc.DrawLine(x1, y1 - 5, x1, y1 + 5)
                    drawcounter += 1
        
        self.Update() 

                           
    def RectSwitch(self, event):
        global drawtype
        self.Bind(wx.EVT_LEFT_DOWN, self.DrawRect)
        self.Bind(wx.EVT_RIGHT_DOWN, self.EraseRect)
        drawtype=1


    def DotSwitch(self, event):
        global drawtype
        self.Bind(wx.EVT_LEFT_DOWN, self.DrawDot)
        self.Bind(wx.EVT_RIGHT_DOWN, self.EraseDot)
        drawtype=2


    def ImageMoveOn(self, event):
        self.Bind(wx.EVT_LEFT_DOWN, self.MouseMove)


    def ImageMoveOff(self, event):
        if drawtype == 1:
            self.Bind(wx.EVT_LEFT_DOWN, self.DrawRect)
        if drawtype == 2:
            self.Bind(wx.EVT_LEFT_DOWN, self.DrawDot)
        self.Bind(wx.EVT_LEFT_UP, self.does_nothing)


    def MacroShow(self, event):
        #The target of this operation is UNFINISHED
        MacroFrame(None, (300,300)).Show()


    def RectSizeSet(self, event):
        global rectwide

        inputcapture = wx.TextEntryDialog(None, 
                                          "Rectangle draw width in pixels", 
                                          "Set Rectangle Width",
                                          defaultValue=str(rectwide), 
                                          style=wx.OK | wx.CANCEL)
        inputcapture.Show()
        if inputcapture.ShowModal() == wx.ID_OK:
            rectwide = int(inputcapture.GetValue())
        else:
            pass
        

    def CrossWideSet(self, event):
        global crosswide

        inputcapture = wx.TextEntryDialog(None, 
                                          "Cross marker width in pixels", 
                                          "Set Marker Width",
                                          defaultValue=str(crosswide), 
                                          style=wx.OK | wx.CANCEL)
        inputcapture.Show()
        if inputcapture.ShowModal() == wx.ID_OK:
            crosswide = int(inputcapture.GetValue())
        else:
            pass


    def CrossLongSet(self, event):
        global crosslong

        inputcapture = wx.TextEntryDialog(None, 
                                          "Cross marker length in pixels",
                                          "Set Marker Width", 
                                          defaultValue=str(crosslong),
                                          style=wx.OK | wx.CANCEL)
        inputcapture.Show()
        if inputcapture.ShowModal() == wx.ID_OK:
            crosslong = int(inputcapture.GetValue())
        else:
            pass

        
    def create_crosshair(self, event):
        self.SetCursor(wx.StockCursor(wx.CURSOR_CROSS))


    def does_nothing(self, event):
        pass


    def on_paint(self, event):
        wx.BufferedPaintDC(self, self.buffer)


# This class is UNFINISHED
class MacroFrame(wx.Frame):
    def __init__(self, parent, mysize):
        wx.Frame.__init__(self, parent, wx.ID_ANY, size=mysize, 
                          title="MacroFrame Alpha - currently non-functional")
        
        # create menu, statusbar
        status = self.CreateStatusBar()
        menubar = wx.MenuBar()
        filemenu = wx.Menu()
        popselectmenu = wx.Menu()
        countselectmenu = wx.Menu()

app = wx.App()
screensize = wx.GetDisplaySize()
width = screensize[0]
height = screensize[1]*.95
CellCounter(None, (width, height)).Show()
# MacroFrame(None, (300, 300)).Show()
app.MainLoop()