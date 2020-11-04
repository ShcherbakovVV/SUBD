from tkintertable import *

#пользовательская модификация классов Tkintertable
class MyColumnHeader(ColumnHeader):
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
    def addRows(self, num=None):
        if num == None:
            num = simpledialog.askinteger("Сколько записей?",
                                            "Количество записей",initialvalue=1,
                                             parent=self.parentframe)
        if not num:
            return
        keys = self.model.autoAddRows(num)
        self.redrawTable()
        self.setSelectedRow(self.model.getRecordIndex(keys[0]))
        return
    
    def deleteRow(self):
        if len(self.multiplerowlist)>1:
            n = messagebox.askyesno("Удаление",
                                      "Удалить выбранные записи?",
                                      parent=self.parentframe)
            if n == True:
                rows = self.multiplerowlist
                self.model.deleteRows(rows)
                self.clearSelected()
                self.setSelectedRow(0)
                self.redrawTable()
        else:
            n = messagebox.askyesno("Удаление",
                                      "Удалить эту запись?",
                                      parent=self.parentframe)
            if n:
                row = self.getSelectedRow()
                self.model.deleteRow(row)
                self.setSelectedRow(row-1)
                self.clearSelected()
                self.redrawTable()
        return    
    
    def popupMenu(self, event, rows=None, cols=None, outside=None):
        defaultactions = {"Новая запись" : lambda : self.addRows(),
                          "Удалить записи" : lambda : self.deleteRow(),
                          "Filter Records" : self.showFilteringBar,}
        general = ["Новая запись" , "Удалить записи", "Filter Records"]

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