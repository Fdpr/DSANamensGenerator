from tkinter import *
from tkinter.font import Font
from tkinter import ttk


class Application(Frame):

    generations = 25
    functions = None
    tree = None
    ftree = None
    textbar = None
    lastselected = None
    style_desc = None
    font_desc = None
    font_names = None

    def __init__(self, t, g, master=None):
        super().__init__(master)
        self.master = master
        self.pack(expand="true", fill="both")
        self.ftree = t
        self.functions = g
        self.create_widgets()

    def clickerbuilder(self, e):
        """The function is called whenever a treenode is clicked"""

        """This part handles calling the right generators and building the text"""
        currentselected = self.tree.selection()[0]
        fun = self.functions[currentselected]
        self.textbar.delete(1.0, END)
        lastindex = "1.0"
        listoftags = list()
        taglines = list()
        for i in range(self.generations):
            t = fun()
            lastindex = self.textbar.index(END)
            self.textbar.insert(END, t[0] + "\n")
            if len(t) > 2:
                curindex = self.textbar.index(END)
                self.textbar.insert(END, t[2] + "\n")
                taglines.append((lastindex, curindex))

        """Set the stylings"""
        self.textbar.tag_add("normal", "1.0", END)
        self.textbar.tag_configure("normal", justify="right", font=self.font_names, foreground="gray90")
        for (x, y) in taglines:
            print(x, y)
            self.textbar.tag_add(str(x+y), x, y)
            self.textbar.tag_configure(str(x+y), justify="right", font=self.font_desc, foreground="gray75")

        """This part handles the automatic opening and closing of nodes in tree"""
        self.tree.item(currentselected, open=TRUE)
        parent = self.tree.parent(currentselected)
        if parent == "":
            children = list(self.tree.get_children())
        else:
            children = list(self.tree.get_children(parent))
        children.remove(currentselected)
        for child in children:
            self.tree.item(child, open=FALSE)
        # children = tree.get_children()

    def create_widgets(self):
        scrollbar = Scrollbar(self)
        scrollbar.pack(side=RIGHT, fill=Y)

        """Styling"""
        font = Font(family="MS Sans Serif", size=10)
        self.font_desc = Font(family="Times", size=15)
        self.font_names = Font(family="times", size=18, weight="bold")
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", font=font, background="gray20", foreground="green",
                        fieldbackground="black",
                        rowheight=30)

        self.textbar = Text(self, background="gray20", padx=20, pady=10, spacing1=6)
        self.tree = ttk.Treeview(self, yscrollcommand=scrollbar.set, style="Treeview")

        self.tree.bind("<<TreeviewSelect>>", self.clickerbuilder)
        items = self.ftree["children"]
        for item in items:
            self.tree_insert(item, "", self.tree)

        self.tree.pack(side="right", expand="true", fill="both")
        scrollbar.config(command=self.tree.yview)
        self.textbar.pack(fill="both", expand="true")

    def tree_insert(self, item, parent, tree):
        ident = tree.insert(parent, 'end', item["name"], text=item["name"])
        # id.bind("<Button-1>", clickerbuilder(item["function"]))
        if item["children"] is not None:
            for children in item["children"]:
                self.tree_insert(children, ident, tree)


def start(t, g):
    root = Tk()
    app = Application(t, g, master=root)
    app.mainloop()