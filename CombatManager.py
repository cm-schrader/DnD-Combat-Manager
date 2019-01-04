import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
from random import randint
import pickle
from bs4 import BeautifulSoup as bs
import urllib.request
import webbrowser

class Window(tk.Tk):
    """A tk window which containts combat and gui functions"""
    def __init__(self):
        super().__init__()
        self.__incrament = 1
        self.winfo_toplevel().title("DnD Combat Manager")  # Add a menu and put help in it and init all?
        try:
            self.iconbitmap("dndicon.ico")
        except tk._tkinter.TclError:
            None
        self.resizable(False, False)
        self.__mainframe = tk.Frame(self, width=700, height=500)
        self.__mainframe.pack(side=tk.RIGHT)
        self.__buttonframe = tk.Frame(self.__mainframe)
        self.__buttonframe.grid(row=2, column=2, sticky=tk.S)
        self.__battlebox = tk.Listbox(self.__mainframe, width=50, height=30)  # Add a scroll bar
        self.__battlebox.grid(row=1, column=0, rowspan=6)
        self.__log = tk.Text(self.__mainframe, width=37, height=30, wrap=tk.WORD, state=tk.DISABLED)
        self.__log.grid(row=1, column=3, rowspan=6)
        self.__new = tk.Button(self.__buttonframe, text="New Combatant", command=None)
        self.gridbutton(self.__new)
        self.__remove = tk.Button(self.__buttonframe, text="Remove Combatant", command=None)
        self.gridbutton(self.__remove)
        self.__search = tk.Button(self.__buttonframe, text="Search for Combatant", command=None)
        self.gridbutton(self.__search)
        self.__dmg = tk.Button(self.__buttonframe, text="Damage", command=None)
        self.gridbutton(self.__dmg)
        self.__heal = tk.Button(self.__buttonframe, text="Heal", command=None)
        self.gridbutton(self.__heal)
        self.__initiative = tk.Button(self.__buttonframe, text="Roll Initiative", command=None)
        self.gridbutton(self.__initiative)
        self.__roll = tk.Button(self.__buttonframe, text="Roll Dice", command=None)
        self.gridbutton(self.__roll)
        self.__actionsname = tk.Label(self.__mainframe, text="Actions")
        self.__actionsname.grid(row=1, column=2, sticky=tk.S)
        self.__dice = tk.Entry(self.__buttonframe, width=8)
        self.__dice.grid(row=9, column=2)
        self.__dicelbl = tk.Label(self.__buttonframe, text="Dice")
        self.__dicelbl.grid(row=8, column=2, sticky=tk.S)

        # Scroll Bar
        self.__logscroll = tk.Scrollbar(self.__mainframe)
        self.__logscroll.grid(row=1, column=4, rowspan=6, sticky=tk.N + tk.S)
        self.__log.config(yscrollcommand=self.__logscroll.set)
        self.__logscroll.config(command=self.__log.yview)

        self.__combatscroll = tk.Scrollbar(self.__mainframe)
        self.__combatscroll.grid(row=1, column=1, rowspan=6, sticky=tk.N + tk.S)
        self.__battlebox.config(yscrollcommand=self.__combatscroll.set)
        self.__combatscroll.config(command=self.__battlebox.yview)

        # Button Commands
        self.__roll.config(command=self.rolldice)
        self.__new.config(command=self.newenemy)
        self.__initiative.config(command=self.rollinitiative)
        self.__dmg.config(command=self.damage)
        self.__heal.config(command=self.heal)
        self.__remove.config(command=self.remove)
        self.__search.config(command=self.search)
        self.protocol("WM_DELETE_WINDOW", self.quitfunc)

        # Menu
        self.__menubar = tk.Menu(self, tearoff=0)
        self.__menubar.add_command(label="Save", command=self.save)
        self.__menubar.add_command(label="Load", command=self.load)
        self.__menubar.add_command(label="Clear", command=self.new)
        self.__menubar.add_separator()
        self.__menubar.add_command(label="Search Roll20", command=roll20)
        self.__menubar.add_command(label="Help", command=self.docx)
        self.config(menu=self.__menubar)

        self.combatants = list()  # Name, hp, initiative, initiative mod, max hp
        self.unsavedwork = False

    def search(self):
        target = None
        try:
            index = self.__battlebox.curselection()[0]
            target = self.combatants[index]
            roll20(querry=target[0].split("#")[0])
        except (TypeError, IndexError):
            self.logprint("No Target!")

    def clearlog(self):
        """
        Clears the log
        :return: None
        """
        self.__log.config(state=tk.NORMAL)
        self.__log.delete("1.0", tk.END)
        self.__log.see(tk.END)
        self.__log.config(state=tk.DISABLED)

    def new(self):
        """
        Makes a new combat
        :return: None
        """
        if len(self.combatants) != 0:
            if not self.unsavedwork or \
                    messagebox.askyesno("End the Battle?",
                                        "Are you sure you want to end the battle combat without saving?"):
                self.combatants = list()
                self.clearlog()
                self.unsavedwork = False
                self.updatelist()

    def save(self):
        """
        Pickles the combatants list for future use.
        :return: None
        """
        filename = filedialog.asksaveasfilename(title="Save Combat", filetypes=[("Combat Manager Pickle File", "*.cpkl")])
        split = filename.split(".")
        nofiletype = False
        if len(split) == 1:
            nofiletype = True
        elif split[-1] != "cpkl":
            nofiletype = True
        if nofiletype:
            filename = filename + ".cpkl"
        try:
            with open(filename, "wb") as file:
                pickle.dump((self.combatants, self.__log.get("1.0", tk.END)), file)
                self.logprint("Combat saved as " + filename)
                self.unsavedwork = False
        except FileNotFoundError:
            if filename != "":
                messagebox.showerror("File Not Found", filename + " could not be found.")

    def load(self):
        """
        Loads a pickled combatants list.
        :return: None
        """
        filename = filedialog.askopenfilename(title="Load Combat", filetypes=[("Combat Manager Pickle File", "*.cpkl")])
        try:
            with open(filename, "rb") as file:
                data = pickle.load(file)
                self.combatants = data[0]
                self.clearlog()
                self.__log.config(state=tk.NORMAL)
                self.__log.insert(tk.END, data[1])
                self.__log.config(state=tk.DISABLED)
                self.logprint(filename.split("/")[-1] + " has been loaded.")
                self.unsavedwork = False
        except FileNotFoundError:
            if filename != "":
                messagebox.showerror("File Not Found", filename + " could not be found.")
        self.updatelist()


    def remove(self):
        """
        Removes the selected target from combat.
        :return: None
        """
        target = None
        try:
            index = self.__battlebox.curselection()[0]
            target = self.combatants[index]
        except (TypeError, IndexError):
            self.logprint("No target!")
        if target is not None:
            self.combatants.remove(target)
            self.logprint("{0} has left the fight!".format(target[0]))
            self.updatelist()

    def damage(self):
        """
        Damages the selected target for the amount specified in the dice box.
        :return: None
        """
        target = None
        try:
            index = self.__battlebox.curselection()[0]
            target = self.combatants[index]
        except (TypeError, IndexError):
            self.logprint("No target!")
        dmgval = parsedice(self.__dice.get())[0]
        if dmgval is not -1 and target is not None:
            target[1] -= dmgval
            if abs(target[1]) >= target[4]:
                self.logprint("{0} has died from Massive Damage!".format(target[0]))
            elif target[1] < 1:
                self.logprint("{0} has been downed!".format(target[0]))
            if target[1] < 1:
                target[1] = 0
        elif dmgval == -1:
            self.logprint("No dice value!")
        self.updatelist()

    def heal(self):
        """
        Heals the selected creature for the amount specified in the dice box.
        :return: None
        """
        target = None
        try:
            index = self.__battlebox.curselection()[0]
            target = self.combatants[index]
        except (TypeError, IndexError):
            self.logprint("No Target!")
        if target is not None:
            if target[1] == 0:
                self.logprint("{0} is back in combat!".format(target[0]))
            healval = parsedice(self.__dice.get())[0]
            target[1] += healval
            if target[1] > target[4]:
                target[1] = target[4]
                self.logprint("{0} is back to max hp!".format(target[0]))
            self.updatelist()

    def rollinitiative(self):
        """
        Rolls initiative for all creatures and updates the list.
        :return: None
        """
        for creature in self.combatants:
            if creature[3][0] is not None and creature[3][0] != "@":
                creature[2] = parsedice("d20+{0}".format(creature[3]))[0]
            else:
                creature[2] = int(creature[3][1:])
        self.updatelist()
        self.logprint("Initiative has been rolled!")

    def updatelist(self):
        """
        Updates the listbox to reflect new changes.
        :return:
        """
        try:
            selectedindex = self.__battlebox.curselection()[0]
        except IndexError:
            selectedindex = 0
        self.combatants = sorted(self.combatants, key=lambda x: -x[2])  # Sort combatants by initiative
        self.__battlebox.delete(0, tk.END)
        for creature in self.combatants:
            if creature[2] == -1:
                initiativeroll = "[  ]"
            elif creature[2] < 10:
                initiativeroll = "[ {0}]".format(creature[2])
            else:
                initiativeroll = "[{0}]".format(creature[2])
            if creature[1] < 1:
                health = "down"
            else:
                health = "{0} hp".format(creature[1])
            self.__battlebox.insert(tk.END, "{0} {1}: {2}".format(initiativeroll, creature[0], health))
        self.__battlebox.select_set(selectedindex)

    def gridbutton(self, widget):
        """
        Conveniently grids a widget.
        :param widget: widget to be placed.
        :return: None
        """
        widget.grid(row=self.__incrament, column=2, sticky=tk.W + tk.E)
        self.__incrament += 1

    def rolldice(self):
        """
        Rolls a dice of a given value and prints it to the log.  Has no side effects.
        :return: None
        """
        result = parsedice(self.__dice.get())
        if result[0] != -1:
            if result[1] is True:
                self.logprint("Natural 1!")
            elif result[2] is True:
                self.logprint("Natural 20!")
            else:
                try:
                    self.logprint("result: " + str(result[0]))
                except None:
                    pass
        else:
            self.logprint("Invalid Dice Roll!")

    def newenemy(self):
        """
        Opens a window to create a new creature.
        :return: None
        """
        arguments = simpledialog.askstring("New Combatant", "[Name],[hp],[init mod]")
        if arguments is not None and arguments != "":
            arguments = arguments.split(",")
            if 2 <= len(arguments) <= 3:  # Assert correct number of arguments
                try:
                    name, hp = arguments[0].strip(), arguments[1].replace(" ", "")
                    initmod = "0"
                    if len(arguments) == 3:
                        initmod = arguments[2].replace(" ", "")
                        if initmod[0] == "@":
                            int(initmod[1:])
                        else:
                            int(initmod)
                    creature = self.find(name)
                    if creature is None:
                        name = str(name)
                        hp = parsedice(hp)[0]
                        if hp != -1:
                            self.combatants.append([name, int(hp), -1, initmod, int(hp)])
                            self.logprint("{0} has joined the fight!".format(name))
                        else:
                            self.logprint("Invalid hp die!")
                    else:
                        self.logprint("That creature already exists!")
                except (ValueError, IndexError):
                    self.logprint("Invalid arguments!")
            else:
                self.logprint("Too many or too few arguments!")
        self.updatelist()

    def logprint(self, string):
        """
        Prints a string to the log and scrolls to it.
        :param string: String to be printed.
        :return: None
        """
        self.__log.config(state=tk.NORMAL)
        self.__log.insert(tk.END, string + "\n")
        self.__log.see(tk.END)
        self.__log.config(state=tk.DISABLED)
        self.unsavedwork = True

    def docx(self):
        """
        Opens the documentation in notepad.
        :return: None
        """
        webbrowser.open("read me.txt")

    def find(self, target):
        """
        Finds the index of a creature in the combatants list.
        :param target: string name of the target.
        :return: None if the creature does not exist or an integer of its index.
        """
        findings = None
        for creature in self.combatants:
            if creature[0] == target:
                findings = self.combatants.index(creature)
        return findings

    def quitfunc(self):
        """
        Runs when the window is closed.
        :return: None
        """
        end = True
        if self.unsavedwork:
            if not messagebox.askyesno("Quit?", "Are you sure you want to quit without saving?"):
                end = False
        if end:
            self.destroy()


def parsedice(die):
    """
    Parses a string dice value.
    :param die: String in the form of #d#+#.  As long as the order is followed, nonimportant values may be omitted.
    :return: Tuple including an integer result, a boolean indicating a natural one, and a boolean indicating a natural
                twenty.
    """
    result = 0
    natone = False
    nattwenty = False
    try:
        result = int(die)
    except ValueError:
        try:
            times, tobesplit = die.split("d")
            try:
                diesize, modifier = tobesplit.split("+")
            except ValueError:
                diesize = tobesplit
                modifier = 0
            if times == "":
                times = 1
            else:
                times = int(times)
            for i in range(0, int(times)):
                premod = randint(1, int(diesize))
                result += premod
            result += int(modifier)
            if int(times) == 1 and int(diesize) == 20:
                if premod == 1:
                    natone = True
                elif premod == 20:
                    nattwenty = True
        except ValueError:
            result = "-1"
    return int(result), natone, nattwenty


def roll20(querry=None):
    """
    Searches roll20.net for a querry and opens the search in a webbrowser.
    :param querry: String to search for.  If none is provided, asks the user.
    :return: None
    """
    if querry is None:
        querry = simpledialog.askstring("Search Roll20", "Search Roll20.net for:")
    if querry is not None:
        url = "https://roll20.net/compendium/dnd5e/searchbook/?terms=" + querry
        webbrowser.open(url)



if __name__ == "__main__":
    gui = Window()
    while gui:
        try:
            gui.update()
            gui.update_idletasks()
        except tk._tkinter.TclError:
            gui = False
