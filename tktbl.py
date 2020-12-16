import os, sys, csv
from tkinter import *
from tkinter.ttk import *
from tkintertable.Tables import *
from tkintertable.TableModels import *

#пользовательская модификация классов Tkintertable
class MyTableModel(TableModel):
    edited_records = []
    del_edit_records = []
    def deleteRow(self, rowIndex=None, key=None, update=True):
        """Delete a row"""
        if key == None or not key in self.reclist:
            key = self.getRecName(rowIndex)
        self.del_edit_records.append( list( self.getRecordAtRow(rowIndex).values() ) )
        del self.data[key]
        if update==True:
            self.reclist.remove(key)
        return
    
    def setValueAt(self, value, rowIndex, columnIndex):
        """Changed the dictionary when cell is updated by user"""
        name = self.getRecName(rowIndex)
        colname = self.getColumnName(columnIndex)
        coltype = self.columntypes[colname]
        if not self.edited_records:
            self.edited_records.append( list( self.getRecordAtRow(rowIndex).values() ) )
        elif list( self.getRecordAtRow(rowIndex).values() ) != self.edited_records[ len(self.edited_records)-1 ]:
            self.edited_records.append('NEXT')
            self.edited_records.append( list( self.getRecordAtRow(rowIndex).values() ) )
        if coltype == 'number':
            try:
                if value == '': 
                    self.data[name][colname] = ''
                    self.edited_records.append( list( self.getRecordAtRow(rowIndex).values() ) )
                else:
                    self.data[name][colname] = float(value)
                    self.edited_records.append( list( self.getRecordAtRow(rowIndex).values() ) )
            except:
                pass
        else:
            self.edited_records.append( list( self.getRecordAtRow(rowIndex).values() ) )
            self.data[name][colname] = value
        self.edited_records.append( list( self.getRecordAtRow(rowIndex).values() ) )
        print(self.edited_records)
        return
    
    def copy(self):
        M = MyTableModel()
        data = self.getData()
        M.setupModel(data)
        return M

class MyColumnHeader(ColumnHeader):
    def handle_left_click(self,event):
        """Does cell selection when mouse is clicked on canvas"""
        pass
    def handle_left_release(self,event):
        """When mouse released implement resize or col move"""
        pass
    def handle_mouse_drag(self, event):
        """Handle column drag, will be either to move cols or resize"""
        pass
    def handle_mouse_move(self, event):
        """Handle mouse moved in header, if near divider draw resize symbol"""
        pass
    def handle_left_shift_click(self, event):
        """Handle shift click, for selecting multiple cols"""
        pass
    def draw_resize_symbol(self, col):
        """Draw a symbol to show that col can be resized when mouse here"""
        pass
    def drawRect(self,col, tag=None, color=None, outline=None, delete=1):
        """User has clicked to select a col"""
        pass
    
    def popupMenu(self, event):
        """Add left and right click behaviour for column header"""
        colname = self.model.columnNames[self.table.currentcol]
        collabel = self.model.columnlabels[colname]
        currcol = self.table.currentcol
        popupmenu = Menu(self, tearoff = 0)
        def popupFocusOut(event):
            popupmenu.unpost()
        popupmenu.add_command(label="По возрастанию", command=lambda : self.table.sortTable(currcol))
        popupmenu.add_command(label="По убыванию", command=lambda : self.table.sortTable(currcol,reverse=1))

        popupmenu.bind("<FocusOut>", popupFocusOut)
        #self.bind("<Button-3>", popupFocusOut)
        popupmenu.focus_set()
        popupmenu.post(event.x_root, event.y_root)
        return popupmenu

class MyTableCanvas(TableCanvas):
    del_records = []
    def __init__(self, parent=None, model=None, data=None, read_only=False,
                 width=None, height=None,
                 rows=10, cols=5, **kwargs):
        Canvas.__init__( self, parent, bg='white',
                         width=width, height=height,
                         relief=GROOVE,
                         scrollregion=(0,0,300,200))
        self.parentframe = parent
        #get platform into a variable
        self.ostyp = self.checkOSType()
        self.platform = platform.system()
        self.width = width
        self.height = height
        self.set_defaults()

        self.currentpage = None
        self.navFrame = None
        self.currentrow = 0
        self.currentcol = 0
        self.reverseorder = 0
        self.startrow = self.endrow = None
        self.startcol = self.endcol = None
        self.allrows = False       #for selected all rows without setting multiplerowlist
        self.multiplerowlist=[]
        self.multiplecollist=[]
        self.col_positions=[]       #record current column grid positions
        self.mode = 'normal'
        self.read_only = read_only
        self.filtered = False

        self.loadPrefs()
        #set any options passed in kwargs to overwrite defaults and prefs
        for key in kwargs:
            self.__dict__[key] = kwargs[key]

        if data is not None:
            self.model = MyTableModel()
            self.model.importDict(data)
        elif model is not None:
            self.model = model
        else:
            self.model = MyTableModel(rows=rows,columns=cols)

        self.rows = self.model.getRowCount()
        self.cols = self.model.getColumnCount()
        self.tablewidth = (self.cellwidth)*self.cols
        self.do_bindings()
        #initial sort order
        self.model.setSortOrder()

        #column specific actions, define for every column type in the model
        #when you add a column type you should edit this dict
        self.columnactions = {'text' : {"Edit":  'drawCellEntry' },
                              'number' : {"Edit": 'drawCellEntry' }}
        self.setFontSize()
        return
    
    def addRow( self, key=None, **kwargs ):
        key = self.model.addRow( key, **kwargs )
        self.redrawTable()
        added_row = int( self.model.getRecordIndex( key ) )
        self.setSelectedRow( added_row )
        #self.movetoSelectedRow( added_row-1, added_row-1 )
        return

    def createfromDict(self, data):
        """Attempt to create a new model/table from a dict"""
        try:
            namefield=self.namefield
        except:
            namefield=data.keys()[0]
        self.model = MyTableModel()
        self.model.importDict(data, namefield=namefield)
        self.model.setSortOrder(0,reverse=self.reverseorder)
        return
    
    def deleteRow(self):
        if len(self.multiplerowlist)>1:
            n = messagebox.askyesno( "Удаление",
                                     "Удалить выбранные записи?",
                                     parent=self.parentframe )
            if n == True:
                rows = self.multiplerowlist
                for i in rows:
                    del_rec_as_list = list(self.model.getRecordAtRow(i).values())
                    self.del_records.append( del_rec_as_list )
                    #del_rec_as_list[1]
                    #self.columnNames.index(columnName)
                self.model.deleteRows(rows)
                self.clearSelected()
                self.setSelectedRow(0)
                self.redrawTable()
        else:
            n = messagebox.askyesno( "Удаление",
                                     "Удалить эту запись?",
                                     parent=self.parentframe )
            if n:
                row = self.getSelectedRow()
                del_rec_as_list = list(self.model.getRecordAtRow(row).values())
                self.del_records.append( del_rec_as_list )
                self.model.deleteRow(row)
                self.setSelectedRow(row-1)
                self.clearSelected()
                self.redrawTable()
        return

    def drawTooltip(self, row, col):
        """Draw a tooltip showing contents of cell"""
        pass

    def drawCellEntry(self, row, col, text=None):
        """When the user single/double clicks on a text/number cell, bring up entry window"""

        if self.read_only == True or col == 7:
            return
        #absrow = self.get_AbsoluteRow(row)
        h=self.rowheight
        model=self.getModel()
        cellvalue = self.model.getCellRecord(row, col)
        if Formula.isFormula(cellvalue):
            return
        else:
            text = self.model.getValueAt(row, col)
        x1,y1,x2,y2 = self.getCellCoords(row,col)
        w=x2-x1
        #Draw an entry window
        txtvar = StringVar()
        txtvar.set(text)
        def callback(e):
            value = txtvar.get()
            coltype = self.model.getColumnType(col)
            if coltype == 'number':
                sta = self.checkDataEntry(e)
                if sta == 1:
                    model.setValueAt(value,row,col)
            elif coltype == 'text':
                model.setValueAt(value,row,col)

            color = self.model.getColorAt(row,col,'fg')
            self.drawText(row, col, value, color, align=self.align)
            if e.keysym=='Return':
                self.delete('entry')
                #self.drawRect(row, col)
                #self.gotonextCell(e)
            return

        self.cellentry=Entry(self.parentframe,width=20,
                        textvariable=txtvar,
                        #bg=self.entrybackgr,
                        #relief=FLAT,
                        takefocus=1,
                        font=self.thefont)
        self.cellentry.icursor(END)
        self.cellentry.bind('<Return>', callback)
        self.cellentry.bind('<KeyRelease>', callback)
        self.cellentry.focus_set()
        self.entrywin=self.create_window(x1+self.inset,y1+self.inset,
                                width=w-self.inset*2,height=h-self.inset*2,
                                window=self.cellentry,anchor='nw',
                                tag='entry')
        return

    def drawMultipleCells(self):
        """Draw an outline box for multiple cell selection"""
        if self.read_only == True:
            pass
        else:
            self.delete('multicellrect')
            rows = self.multiplerowlist
            cols = self.multiplecollist
            w=2
            x1,y1,a,b = self.getCellCoords(rows[0],cols[0])
            c,d,x2,y2 = self.getCellCoords(rows[len(rows)-1],cols[len(cols)-1])
            rect = self.create_rectangle(x1+w/2,y1+w/2,x2,y2,
                                 outline='blue',width=w,activefill='red',activestipple='gray25',
                                 tag='multicellrect')
        return

    def drawMultipleRows(self, rowlist):
        """Draw more than one row selection"""
        if self.read_only == True:
            pass
        else:
            self.delete('multiplesel')
            for r in rowlist:
                if r not in self.visiblerows or r > self.rows-1:
                    continue
                x1,y1,x2,y2 = self.getCellCoords(r,0)
                x2 = self.tablewidth
                rect = self.create_rectangle(x1,y1,x2,y2,
                                          fill=self.multipleselectioncolor,
                                          outline=self.rowselectedcolor,
                                          tag=('multiplesel','rowrect'))
            self.lower('multiplesel')
            self.lower('fillrect')
        return

    def drawRect(self, row, col, color=None, tag=None, delete=1):
        """Cell is colored"""
        if self.read_only == True:
            pass
        else:
            if delete==1:
                self.delete('cellbg'+str(row)+str(col))
            if color==None or color==self.cellbackgr:
                return
            else:
                bg=color
            if tag==None:
                recttag='fillrect'
            else:
                recttag=tag
            w=1
            x1,y1,x2,y2 = self.getCellCoords(row,col)
            rect = self.create_rectangle(x1+w/2,y1+w/2,x2-w/2,y2-w/2,
                                      fill=bg,
                                      outline=bg,
                                      width=w,
                                      tag=(recttag,'cellbg'+str(row)+str(col)))
            self.lower(recttag)
        return

    def drawRowHeader(self):
        """User has clicked to select a cell"""
        if self.read_only == True:
            pass
        else:
            self.delete('rowheader')
            x_start=self.x_start
            y_start=self.y_start
            h=self.rowheight
            rowpos=0
            for row in self.rowrange:
                x1,y1,x2,y2 = self.getCellCoords(rowpos,0)
                self.create_rectangle(0,y1,x_start-2,y2,
                                          fill='gray75',
                                          outline='white',
                                          width=1,
                                          tag='rowheader')
                self.create_text(x_start/2,y1+h/2,
                                          text=row+1,
                                          fill='black',
                                          font=self.thefont,
                                          tag='rowheader')
                rowpos+=1
        return

    def drawSelectedCol(self, col=None, delete=1):
        """Draw an outline rect fot the current column selection"""
        if self.read_only == True:
            pass
        else:
            if delete == 1:
                self.delete('colrect')
            if col == None:
                col=self.currentcol
            w=2
            x1,y1,x2,y2 = self.getCellCoords(0,col)
            y2 = self.rows * self.rowheight
            rect = self.create_rectangle(x1+w/2,y1+w/2,x2,y2+w/2,
                                         outline='blue',width=w,
                                         tag='colrect')
        return

    def drawSelectedRect(self, row, col, color=None):
        """User has clicked to select a cell"""
        if self.read_only == True:
            pass
        else:
            if col >= self.cols:
                return
            self.delete('currentrect')
            bg = self.selectedcolor
            if color == None:
                color = 'gray25'
            w=3
            x1,y1,x2,y2 = self.getCellCoords(row,col)
            rect = self.create_rectangle(x1+w/2,y1+w/2,x2-w/2,y2-w/2,
                                         fill=bg,
                                         outline=color,
                                         width=w,
                                         stipple='gray50',
                                         tag='currentrect')
            #self.lower('currentrect')
            #raise text above all
            self.lift('celltext'+str(col)+'_'+str(row))
        return

    def drawSelectedRow(self):
        """Draw the highlight rect for the currently selected row"""
        if self.read_only == True:
            pass
        else:
            self.delete('rowrect')
            row = self.currentrow
            x1,y1,x2,y2 = self.getCellCoords(row,0)
            x2 = self.tablewidth
            rect = self.create_rectangle(x1,y1,x2,y2,
                                         fill=self.rowselectedcolor,
                                         outline=self.rowselectedcolor,
                                         tag='rowrect')
            self.lower('rowrect')
            self.lower('fillrect')
            self.tablerowheader.drawSelectedRows(self.currentrow)
        return

    def importCSV(self, filename=None):
        """Import from csv file"""
        if filename is None:
            from .Tables_IO import TableImporter
            importer = TableImporter()
            importdialog = importer.import_Dialog(self.master)
            self.master.wait_window(importdialog)
            model = MyTableModel()
            model.importDict(importer.data)
        else:
            model = MyTableModel()
            model.importCSV(filename)
        self.updateModel(model)
        return
    
    '''def movetoSelectedRow( self, row=None, recname=None ):
        row=self.model.getRecordIndex(recname)
        self.setSelectedRow(row)
        self.drawSelectedRow()
        x,y = self.getCanvasPos(row, 0)
        self.yview('moveto', y-0.01)
        self.tablecolheader.yview('moveto', y)
        self.updateModel(self.model)
        return'''

    def new(self):
        """Clears all the data and makes a new table"""
        mpDlg = MultipleValDialog(title='Create new table',
                                  initialvalues=(10, 4),
                                  labels=('rows','columns'),
                                  types=('int','int'),
                                  parent=self.parentframe)

        if mpDlg.result == True:
            rows = mpDlg.results[0]
            cols = mpDlg.results[1]
            model = MyTableModel(rows=rows,columns=cols)
            self.updateModel(model)
        return
    
    def popupMenu(self, event, rows=None, cols=None, outside=None):
        defaultactions = { "Новая запись" : lambda : self.addRow(),
                           "Удалить" : lambda : self.deleteRow() }
        general = [ "Новая запись" , "Удалить" ]

        def createSubMenu(parent, label, commands):
            menu = Menu(parent, tearoff = 0)
            popupmenu.add_cascade(label=label,menu=menu)
            for action in commands:
                menu.add_command(label=action, command=defaultactions[action])
            return menu

        popupmenu = Menu(self, tearoff = 0)
        def popupFocusOut(event):
            popupmenu.unpost()

        if outside == None:
            row = self.get_row_clicked(event)
            col = self.get_col_clicked(event)
            coltype = self.model.getColumnType(col)
            def add_defaultcommands():
                """now add general actions for all cells"""
                for action in main:
                    if action == 'Fill Down' and (rows == None or len(rows) <= 1):
                        continue
                    if action == 'Fill Right' and (cols == None or len(cols) <= 1):
                        continue
                    else:
                        popupmenu.add_command(label=action, command=defaultactions[action])
                return

        for action in general:
            popupmenu.add_command(label=action, command=defaultactions[action])

        popupmenu.bind("<FocusOut>", popupFocusOut)
        popupmenu.focus_set()
        popupmenu.post(event.x_root, event.y_root)
        return popupmenu

    def show(self, callback=None):
        self.tablerowheader = RowHeader(self.parentframe, self, width=self.rowheaderwidth)
        self.tablecolheader = MyColumnHeader(self.parentframe, self)
        self.Yscrollbar = AutoScrollbar(self.parentframe,orient=VERTICAL,command=self.set_yviews)
        self.Yscrollbar.grid(row=1,column=2,rowspan=1,sticky='news',pady=0,ipady=0)
        self.Xscrollbar = AutoScrollbar(self.parentframe,orient=HORIZONTAL,command=self.set_xviews)
        self.Xscrollbar.grid(row=2,column=1,columnspan=1,sticky='news')
        self['xscrollcommand'] = self.Xscrollbar.set
        self['yscrollcommand'] = self.Yscrollbar.set
        self.tablecolheader['xscrollcommand'] = self.Xscrollbar.set
        self.tablerowheader['yscrollcommand'] = self.Yscrollbar.set
        self.parentframe.rowconfigure(1,weight=1)
        self.parentframe.columnconfigure(1,weight=1)

        self.tablecolheader.grid(row=0,column=1,rowspan=1,sticky='news',pady=0,ipady=0)
        self.tablerowheader.grid(row=1,column=0,rowspan=1,sticky='news',pady=0,ipady=0)
        self.grid(row=1,column=1,rowspan=1,sticky='news',pady=0,ipady=0)

        self.adjustColumnWidths()
        self.redrawTable(callback=callback)
        self.parentframe.bind("<Configure>", self.redrawVisible)
        self.tablecolheader.xview("moveto", 0)
        self.xview("moveto", 0)
        return

    def updateModel(self, model):
        self.model = model
        self.rows = self.model.getRowCount()
        self.cols = self.model.getColumnCount()
        self.tablewidth = (self.cellwidth)*self.cols
        self.tablecolheader = MyColumnHeader(self.parentframe, self)
        self.tablerowheader = RowHeader(self.parentframe, self)
        self.createTableFrame()
        return
    
