from tkinter import *
from tkinter import ttk


class Application(Frame):

    generations = 25
    functions = None
    tree = None
    ftree = None
    textbar = None
    lastselected = None
    opennodes = []

    def __init__(self, t, g, master=None):
        super().__init__(master)
        self.master = master
        self.pack(expand="true", fill="both")
        self.ftree = t
        self.functions = g
        self.create_widgets()

    def clickerbuilder(self, e):
        """The function is called whenever a treenode is clicked"""
        s = list()
        currentselected = self.tree.selection()[0]
        fun = self.functions[currentselected]
        for i in range(self.generations):
            t = fun()
            s.append(t[0])
            s.append(str(t[1]))
        r = "\n".join(s)
        self.textbar.delete(1.0, END)
        self.textbar.insert(END, r)
        self.tree.item(currentselected, open=TRUE)
        if currentselected in self.opennodes:
            self.tree.item(currentselected, open=FALSE)
            self.opennodes.remove(currentselected)
        else:
            self.opennodes.append(currentselected)
        self.lastselected = currentselected
        
    def create_widgets(self):
        scrollbar = Scrollbar(self)
        scrollbar.pack(side=LEFT, fill=Y)

        self.textbar = Text(self)
        self.tree = ttk.Treeview(self, yscrollcommand=scrollbar.set)

        self.tree.bind("<<TreeviewSelect>>", self.clickerbuilder)
        items = self.ftree["children"]
        for item in items:
            self.insert(item, "", self.tree)

        self.tree.pack(side="left", expand="true", fill="both")
        scrollbar.config(command=self.tree.yview)
        self.textbar.pack(fill="both", expand="true")

    def insert(self, item, parent, tree):
        ident = tree.insert(parent, 'end', item["name"], text=item["name"])
        # id.bind("<Button-1>", clickerbuilder(item["function"]))
        if item["children"] is not None:
            for children in item["children"]:
                self.insert(children, ident, tree)


def start(t, g):
    root = Tk()
    app = Application(t, g, master=root)
    app.mainloop()