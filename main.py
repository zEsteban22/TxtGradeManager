from io import TextIOWrapper
import tkinter as tk
from tkinter import ttk
import tkinter.filedialog
from tkinter import messagebox
import os
from hashlib import md5

ESQUEMA={
    'Nombre':16,
    'Apellido':16,
    'EVALUACIONES':18,
    'total':6
}

TABLA_VACÍA="""\
Nombre          |Apellido        |Total
                |                |      """

class Document:
    def __init__(self, Frame, textWidget:tk.Text, FileDir=''):
        self.evaluaciones=dict()
        self.textbox = textWidget
        self.file_dir = FileDir
        if not FileDir:
            self.file_name = 'Sin título' 
            self.textbox.insert('end',TABLA_VACÍA)
        else:
            self.file_name = os.path.basename(FileDir) 
            with open(self.file_name) as file:
                self.cargarDatos(file)
        self.status = md5(self.textbox.get(1.0, 'end').encode('utf-8'))
    def cargarDatos(self,file:TextIOWrapper):
        encabezado=file.readline()
        self.evaluaciones=dict([
        (ev,eval(porcentaje.replace("%",""))*0.01) 
        for ev,porcentaje in [
            par.split(":") 
            for par in encabezado.split("|")[2:1]]])
class Editor:
    def __init__(self, master):
        self.master = master
        self.master.title("TxtGradeManager")
        self.frame = tk.Frame(self.master)
        self.frame.pack()
        
        self.filetypes = (("Normal text file", "*.txt"), ("all files", "*.*"))
        self.init_dir = os.path.join(os.path.expanduser('~'), 'Desktop')
        
        self.tabs = {} # { index, text widget }
        
        # Create Notebook ( for tabs ).
        self.nb = ttk.Notebook(master)
        self.nb.bind("<Button-2>", self.close_tab)
        self.nb.bind("<B1-Motion>", self.move_tab)
        self.nb.pack(expand=1, fill="both")
        self.nb.enable_traversal()
        #self.nb.bind('<<NotebookTabChanged>>', self.tab_change)

        # Override the X button.
        self.master.protocol('WM_DELETE_WINDOW', self.exit)
        
        # Create Menu Bar
        menubar = tk.Menu(self.master)
        
        # Create File Menu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Nuevo", command=self.new_file)
        filemenu.add_command(label="Abrir", command=self.open_file)
        filemenu.add_command(label="Guardar", command=self.save_file)
        filemenu.add_command(label="Guardar como...", command=self.save_as)
        filemenu.add_command(label="Cerrar", command=self.close_tab)
        filemenu.add_separator()
        filemenu.add_command(label="Salir", command=self.exit)
        
        # Create Edit Menu
        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Añadir estudiante", command=self.nuevoEstudiante)
        editmenu.add_command(label="Añadir evaluación", command=self.nuevaEvaluacion)
        editmenu.add_separator()
        editmenu.add_command(label="Deshacer", command=self.undo)
        editmenu.add_separator()
        editmenu.add_command(label="Cortar", command=self.cut)
        editmenu.add_command(label="Copiar", command=self.copy)
        editmenu.add_command(label="Pegar", command=self.paste)
        editmenu.add_command(label="Borrar", command=self.delete)
        editmenu.add_command(label="Seleccionar todo", command=self.select_all)
        
        self.master.config(menu=menubar)
        
        # Attach to Menu Bar
        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Edit", menu=editmenu)

        # Create right-click menu.
        self.right_click_menu = tk.Menu(self.master, tearoff=0)
        self.right_click_menu.add_command(label="Añadir estudiante", command=self.nuevoEstudiante)
        self.right_click_menu.add_command(label="Añadir evaluación", command=self.nuevaEvaluacion)
        self.right_click_menu.add_separator()
        self.right_click_menu.add_command(label="Deshacer", command=self.undo)
        self.right_click_menu.add_separator()
        self.right_click_menu.add_command(label="Cortar", command=self.cut)
        self.right_click_menu.add_command(label="Copiar", command=self.copy)
        self.right_click_menu.add_command(label="Pegar", command=self.paste)
        self.right_click_menu.add_command(label="Borrar", command=self.delete)
        self.right_click_menu.add_separator()
        self.right_click_menu.add_command(label="Seleccionar todo", command=self.select_all)
        
        # Create tab right-click menu
        self.tab_right_click_menu = tk.Menu(self.master, tearoff=0)
        self.tab_right_click_menu.add_command(label="Nueva pestaña", command=self.new_file)
        self.nb.bind('<Button-3>', self.right_click_tab)

        # Create Initial Tab
        first_tab = ttk.Frame(self.nb)
        self.tabs[ first_tab ] = Document( first_tab, self.create_text_widget(first_tab) )
        self.nb.add(first_tab, text='Sin título')

    def create_text_widget(self, frame):
        # Horizontal Scroll Bar 
        xscrollbar = tk.Scrollbar(frame, orient='horizontal')
        xscrollbar.pack(side='bottom', fill='x')
        
        # Vertical Scroll Bar
        yscrollbar = tk.Scrollbar(frame)
        yscrollbar.pack(side='right', fill='y')

        # Create Text Editor Box
        textbox = tk.Text(frame, relief='sunken', borderwidth=0, wrap='none')
        textbox.config(xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set, undo=True, autoseparators=True)

        # Keyboard / Click Bindings
        textbox.bind('<Control-s>', self.save_file)
        textbox.bind('<Control-o>', self.open_file)
        textbox.bind('<Control-n>', self.new_file)
        textbox.bind('<Control-a>', self.select_all)
        textbox.bind('<Control-w>', self.close_tab)
        textbox.bind('<Button-3>', self.right_click)
        textbox.bind('<Key>',self.processKey)

        # Pack the textbox
        textbox.pack(fill='both', expand=True)        
        
        # Configure Scrollbars
        xscrollbar.config(command=textbox.xview)
        yscrollbar.config(command=textbox.yview)

        #Creo que por aquí debería añadir los botones y entradas para añadir estudiantes y evaluaciones
		
        return textbox

    def nuevoEstudiante(self):
        nuevaLínea='\n'+' '*ESQUEMA['Nombre']+'|'+' '*ESQUEMA['Apellido']+len(self.tabs[ self.get_tab() ].evaluaciones)*('| '+' '*ESQUEMA['EVALUACIONES'])+'|      '
        self.tabs[ self.get_tab() ].textbox.insert('end',nuevaLínea)
    
    def nuevaEvaluacion(self):
        t=self.tabs[ self.get_tab() ].textbox
        t.insert('1.%d'%(len(t.get("1.0","2.0"))-7),'| evaluación : 0.0%')
        for lineNum,lineTxt in enumerate(t.get('2.0', 'end-1c').splitlines()):
            t.insert('%d.%d'%(2+lineNum,len(lineTxt)-7),'|'+'                  ')

    def processKey(self,event):
        if(len(event.char)==0 and event.keycode!=46): return 
        elif event.char=='|': return "break"
        tb=self.tabs[ self.get_tab() ].textbox
        insert=tb.index("insert")
        eol = tb.index("insert lineend")
        nextchar = tb.index("insert + %dc" % len(event.char))
        resto_de_la_linea=tb.get(nextchar,eol)
        if tb.get(insert,nextchar)=='|':
            tb.delete(insert,nextchar)
            tb.insert(insert,'|')
            resto_de_la_linea='|'+resto_de_la_linea
        if event.char=="\x08" and insert.split('.')[-1]=='0':
            return "break"
        elif eol != insert:
            for c,e in enumerate(resto_de_la_linea):
                if e=='|' or c+1==len(resto_de_la_linea):
                    if event.char=='\x08':
                        tb.insert(tb.index(f"insert +{c+1}c"),' ')
                    elif event.keycode==46:
                        tb.insert(tb.index(f"insert +{c}c"),' ')
                    else:
                        tb.delete(tb.index(f"insert +{c}c"), tb.index(f"insert +{c+1}c") )
                    break
        else:
            if event.keycode==46: return "break"
            tb.delete(tb.index("insert-1c"),eol)
        
        
    def open_file(self, *args):        
        # Open a window to browse to the file you would like to open, returns the directory.
        file_dir = (tkinter
         .filedialog
         .askopenfilename(initialdir=self.init_dir, title="Escoja archivo", filetypes=self.filetypes))
        
        # If directory is not the empty string, try to open the file. 
        if file_dir:
            try:
                # Open the file.
                file = open(file_dir)
                
                # Create a new tab.
                new_tab = ttk.Frame(self.nb)
                self.tabs[ new_tab ] = Document(new_tab, self.create_text_widget(new_tab), file_dir)
                self.nb.add(new_tab, text=os.path.basename(file_dir))
                self.nb.select( new_tab )
                            
                # Puts the contents of the file into the text widget.
                self.tabs[ new_tab ].textbox.insert('end', file.read())
                
                # Update hash
                self.tabs[ new_tab ].status = md5(tabs[ new_tab ].textbox.get(1.0, 'end').encode('utf-8'))
            except:
                return

    def save_as(self):
        curr_tab = self.get_tab()
    
        # Gets file directory and name of file to save.
        file_dir = (tkinter
         .filedialog
         .asksaveasfilename(initialdir=self.init_dir, title="Escoja archivo", filetypes=self.filetypes, defaultextension='.txt'))
        
        # Return if directory is still empty (user closes window without specifying file name).
        if not file_dir:
            return
         
        # Adds .txt suffix if not already included.
        if file_dir[-4:] != '.txt':
            file_dir += '.txt'
            
        self.tabs[ curr_tab ].file_dir = file_dir
        self.tabs[ curr_tab ].file_name = os.path.basename(file_dir)
        self.nb.tab( curr_tab, text=self.tabs[ curr_tab ].file_name) 
            
        # Writes text widget's contents to file.
        file = open(file_dir, 'w')
        file.write(self.tabs[ curr_tab ].textbox.get(1.0, 'end'))
        file.close()
        
        # Update hash
        self.tabs[ curr_tab ].status = md5(self.tabs[ curr_tab ].textbox.get(1.0, 'end').encode('utf-8'))
        
    def save_file(self, *args):
        curr_tab = self.get_tab()
        
        # If file directory is empty or Untitled, use save_as to get save information from user. 
        if not self.tabs[ curr_tab ].file_dir:
            self.save_as()

        # Otherwise save file to directory, overwriting existing file or creating a new one.
        else:
            with open(self.tabs[ curr_tab ].file_dir, 'w') as file:
                file.write(self.tabs[ curr_tab ].textbox.get(1.0, 'end'))
                
            # Update hash
            self.tabs[ curr_tab ].status = md5(self.tabs[ curr_tab ].textbox.get(1.0, 'end').encode('utf-8'))
                
    def new_file(self, *args):                
        # Create new tab
        new_tab = ttk.Frame(self.nb)
        self.tabs[ new_tab ] = Document(new_tab, self.create_text_widget(new_tab))
        self.tabs[ new_tab ].textbox.config(wrap='none')
        self.nb.add(new_tab, text='Sin título')
        self.nb.select( new_tab )
        
    def copy(self):
        # Clears the clipboard, copies selected contents.
        try: 
            sel = self.tabs[ self.get_tab() ].textbox.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.master.clipboard_clear()
            self.master.clipboard_append(sel)
        # If no text is selected.
        except tk.TclError:
            pass
            
    def delete(self):
        # Delete the selected text.
        try:
            self.tabs[ self.get_tab() ].textbox.delete(tk.SEL_FIRST, tk.SEL_LAST)
        # If no text is selected.
        except tk.TclError:
            pass        
    def cut(self):
        # Copies selection to the clipboard, then deletes selection.
        try: 
            sel = self.tabs[ self.get_tab() ].textbox.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.master.clipboard_clear()
            self.master.clipboard_append(sel)
            self.tabs[ self.get_tab() ].textbox.delete(tk.SEL_FIRST, tk.SEL_LAST)
        # If no text is selected.
        except tk.TclError:
            pass

    def paste(self):
        try: 
            self.tabs[ self.get_tab() ].textbox.insert(tk.INSERT, self.master.clipboard_get())
        except tk.TclError:
            pass
            
    def select_all(self, *args):
        curr_tab = self.get_tab()
        
        # Selects / highlights all the text.
        self.tabs[ curr_tab ].textbox.tag_add(tk.SEL, "1.0", tk.END)
        
        # Set mark position to the end and scroll to the end of selection.
        self.tabs[ curr_tab ].textbox.mark_set(tk.INSERT, tk.END)
        self.tabs[ curr_tab ].textbox.see(tk.INSERT)

    def undo(self):
        self.tabs[ self.get_tab() ].textbox.edit_undo()

    def right_click(self, event):
        self.right_click_menu.post(event.x_root, event.y_root)
        
    def right_click_tab(self, event):
        self.tab_right_click_menu.post(event.x_root, event.y_root)
        
    def close_tab(self, event=None):
        # Close the current tab if close is selected from file menu, or keyboard shortcut.
        if event is None or event.type == str( 2 ):
            selected_tab = self.get_tab()
        # Otherwise close the tab based on coordinates of center-click.
        else:
            try:
                index = event.widget.index('@%d,%d' % (event.x, event.y))
                selected_tab = self.nb._nametowidget( self.nb.tabs()[index] )
            except tk.TclError:
                return

        # Prompt to save changes before closing tab
        if self.save_changes():
            self.nb.forget( selected_tab )
            self.tabs.pop( selected_tab )

        # Exit if last tab is closed
        if self.nb.index("end") == 0:
            self.master.destroy()
        
    def exit(self):        
        # Check if any changes have been made.
        if self.save_changes():
            self.master.destroy()
        else:
            return
               
    def save_changes(self):
        curr_tab = self.get_tab()
        file_dir = self.tabs[ curr_tab ].file_dir
        
        # Check if any changes have been made, returns False if user chooses to cancel rather than select to save or not.
        if md5(self.tabs[ curr_tab ].textbox.get(1.0, 'end').encode('utf-8')).digest() != self.tabs[ curr_tab ].status.digest():
            # If changes were made since last save, ask if user wants to save.
            m = messagebox.askyesnocancel('Editor', '¿Quiere guardar los cambios hechos en ' + ('Sin título' if not file_dir else file_dir) + '?' )
            
            # If None, cancel.
            if m is None:
                return False
            # else if True, save.
            elif m is True:
                self.save_file()
            # else don't save.
            else:
                pass
                
        return True
    
    # Get the object of the current tab.
    def get_tab(self):
        return self.nb._nametowidget( self.nb.select() )
        
    def move_tab(self, event):
        '''
        Check if there is more than one tab.
        
        Use the y-coordinate of the current tab so that if the user moves the mouse up / down 
        out of the range of the tabs, the left / right movement still moves the tab.
        '''
        if self.nb.index("end") > 1:
            y = self.get_tab().winfo_y() - 5
            
            try:
                self.nb.insert( event.widget.index('@%d,%d' % (event.x, y)), self.nb.select() )
            except tk.TclError:
                return

def main(): 
    root = tk.Tk()
    app = Editor(root)
    root.mainloop()

if __name__ == '__main__':
    main()
    