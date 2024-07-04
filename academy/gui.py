import tkinter.ttk as ttk
import tkinter as tk
from tkinter import font
from tkinter.messagebox import showinfo
import pandas as pd
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from functools import partial
from academy import bpod, queues
from academy.utils import utils
from academy.arduino import arduino
from academy.task_collection import task_collection
from academy.camera import cam1, cam2, cam3
from user import settings
import time

from academy import time_utils


class Gui(tk.Frame):
    def __init__(self):

        self.window = tk.Tk()
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=20)
        self.window.option_add("*Font", default_font)
        self.window.title("ACADEMY box " + str(settings.BOX_NAME))
        self.width = 1850
        self.height = 1025
        geometry = str(self.width) + "x" + str(self.height)
        self.window.geometry(geometry)

        back = tk.Frame(master=self.window, bg="black")
        back.pack_propagate(0)

        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        self.subject = None
        self.subject_name = "None"
        # self.subject_var = tk.StringVar()
        self.event_labels = []
        self.entries = []  # 0 is trials, 1 is time
        self.properties = []  # properties of the entries
        self.boolvars = []  # when the properties are bool
        self.blue = ttk.Style(self.window)
        self.blue.configure("blue.TButton", foreground="blue", fontsize=6)
        self.red = ttk.Style(self.window)
        self.red.configure("red.TButton", foreground="red", fontsize=6)
        self.green = ttk.Style(self.window)
        self.green.configure("green.TButton", foreground="green", fontsize=3)
        self.black = ttk.Style(self.window)
        self.green.configure("black.TButton", foreground="black", fontsize=6)
        self.subject0_combo = None
        self.subject_combo = None
        self.task_combo = None
        self.task_label = None
        self.task_label2 = None
        self.task_label3 = None
        self.task_label4 = None
        self.task_value = None
        self.task_value2 = None
        self.task_value3 = None
        self.task_value4 = None
        self.subject_value = None
        self.exit_button = None
        self.reload_button = None
        self.subject_button = None
        self.subject_button2 = None
        self.upload_button = None
        self.title = None
        self.task_buttons = []
        self.image_label1 = None
        self.image_label2 = None
        self.image_label3 = None
        self.tags_on_off1 = None
        self.tags_on_off2 = None
        self.tags_on_off3 = None
        self.cams_on_off = None
        self.canvas = None
        self.counter = 0
        self.target = 200  # each 200 frames of tkinter we update the plot
        tk.Frame.__init__(self, self.window, width=self.width, height=self.height)

        # this needs to be in the end
        try:
            from user.rt_plots import fig
        except:
            fig = None

        self.fig = fig

        self.a = 0
        self.b = 0

        self.start()

    def start(self):
        self.draw()
        self.pack()

    def draw(self):
        margin = 2
        cell = 10
        first_cell = 25
        three_cells = cell * 3
        all_no_margins = first_cell + cell * 10
        row = 0

        if utils.state != 7:  # no setting

            x1 = 1290
            x2 = 1485
            x3 = 1680

            # title
            self.title = tk.Label(self, text="TASKS:", anchor="w", fg="blue")
            self.title.place(x=x2, y=5, height=15, width=250)

            # tags
            if utils.reading_tags == 0:
                self.tags_on_off1 = ttk.Button(
                    self,
                    text="Tag read AUTO = OFF",
                    command=self.tags_on_off1_button,
                    style="red.TButton",
                )
                self.tags_on_off2 = ttk.Button(
                    self,
                    text="Tag read DAY = OFF",
                    command=self.tags_on_off2_button,
                    style="red.TButton",
                )
                self.tags_on_off3 = ttk.Button(
                    self,
                    text="Tag read NIGHT = OFF",
                    command=self.tags_on_off3_button,
                    style="red.TButton",
                )
            elif utils.reading_tags == 1:
                self.tags_on_off1 = ttk.Button(
                    self,
                    text="Tag read AUTO = ON",
                    command=self.tags_on_off1_button,
                    style="green.TButton",
                )
                self.tags_on_off2 = ttk.Button(
                    self,
                    text="Tag read DAY = OFF",
                    command=self.tags_on_off2_button,
                    style="red.TButton",
                )
                self.tags_on_off3 = ttk.Button(
                    self,
                    text="Tag read NIGHT = OFF",
                    command=self.tags_on_off3_button,
                    style="red.TButton",
                )
            elif utils.reading_tags == 2:
                self.tags_on_off1 = ttk.Button(
                    self,
                    text="Tag read AUTO = OFF",
                    command=self.tags_on_off1_button,
                    style="red.TButton",
                )
                self.tags_on_off2 = ttk.Button(
                    self,
                    text="Tag read DAY = ON",
                    command=self.tags_on_off2_button,
                    style="green.TButton",
                )
                self.tags_on_off3 = ttk.Button(
                    self,
                    text="Tag read NIGHT = OFF",
                    command=self.tags_on_off3_button,
                    style="red.TButton",
                )
            else:
                self.tags_on_off1 = ttk.Button(
                    self,
                    text="Tag read AUTO = OFF",
                    command=self.tags_on_off1_button,
                    style="green.TButton",
                )
                self.tags_on_off2 = ttk.Button(
                    self,
                    text="Tag read DAY = OFF",
                    command=self.tags_on_off2_button,
                    style="red.TButton",
                )
                self.tags_on_off3 = ttk.Button(
                    self,
                    text="Tag read NIGHT = ON",
                    command=self.tags_on_off3_button,
                    style="red.TButton",
                )

            self.tags_on_off1.place(x=x1, y=10, height=20, width=160)
            self.tags_on_off2.place(x=x1, y=30, height=20, width=160)
            self.tags_on_off3.place(x=x1, y=50, height=20, width=160)

            ttk.Separator(self, orient=tk.HORIZONTAL).place(
                x=x1 - 10, y=70, height=4, width=190
            )

            # camera button
            self.cams_on_off = ttk.Button(
                self,
                text="Preview Cams",
                command=self.cams_on_off_button,
                style="green.TButton",
            )
            self.cams_on_off.place(x=x1, y=74, height=20, width=160)

            ttk.Separator(self, orient=tk.HORIZONTAL).place(
                x=x1 - 10, y=94, height=4, width=190
            )

            # doors
            ttk.Button(
                self, text="Open door 1", command=self.open_door1, style="green.TButton"
            ).place(x=x1, y=98, height=20, width=160)
            ttk.Button(
                self, text="Close door 1", command=self.close_door1, style="red.TButton"
            ).place(x=x1, y=118, height=20, width=160)
            ttk.Button(
                self, text="Open door 2", command=self.open_door2, style="green.TButton"
            ).place(x=x1, y=138, height=20, width=160)
            ttk.Button(
                self, text="Close door 2", command=self.close_door2, style="red.TButton"
            ).place(x=x1, y=158, height=20, width=160)
            ttk.Button(
                self,
                text="Open inner door",
                command=self.open_inner_door,
                style="green.TButton",
            ).place(x=x1, y=178, height=20, width=160)
            ttk.Button(
                self,
                text="Close inner door",
                command=self.close_inner_door,
                style="red.TButton",
            ).place(x=x1, y=198, height=20, width=160)

            ttk.Separator(self, orient=tk.HORIZONTAL).place(
                x=x1 - 10, y=118, height=4, width=190
            )

            # buzzer
            ttk.Button(
                self,
                text="Play buzzer 1",
                command=self.play_buzzer1,
                style="blue.TButton",
            ).place(x=x1, y=222, height=20, width=160)
            ttk.Button(
                self,
                text="Play buzzer 2",
                command=self.play_buzzer2,
                style="blue.TButton",
            ).place(x=x1, y=242, height=20, width=160)

            ttk.Separator(self, orient=tk.HORIZONTAL).place(
                x=x1 - 10, y=262, height=4, width=190
            )

            # temperature
            ttk.Button(
                self,
                text="Get temperature",
                command=self.get_temperature,
                style="blue.TButton",
            ).place(x=x1, y=266, height=20, width=160)

            ttk.Separator(self, orient=tk.HORIZONTAL).place(
                x=x1 - 10, y=290, height=4, width=190
            )

            # scale
            ttk.Button(
                self, text="Tare scale", command=self.tare_scale, style="blue.TButton"
            ).place(x=x1, y=294, height=20, width=160)
            ttk.Button(
                self, text="Get weight", command=self.get_weight, style="blue.TButton"
            ).place(x=x1, y=314, height=20, width=160)

            ttk.Separator(self, orient=tk.HORIZONTAL).place(
                x=x1 - 10, y=334, height=4, width=190
            )

            # x_max
            ttk.Button(
                self, text="+ days", command=self.x_max_bigger, style="green.TButton"
            ).place(x=x1 + 80, y=338, height=20, width=80)
            ttk.Button(
                self, text="- days", command=self.x_max_smaller, style="red.TButton"
            ).place(x=x1, y=338, height=20, width=80)

            # plots button
            self.upload_button = ttk.Button(
                self,
                text="Update plots (" + str(utils.x_max) + " days)",
                command=self.update_canvas,
                style="blue.TButton",
            )
            self.upload_button.place(x=x1, y=358, width=160, height=20)

            # tasks
            self.task_buttons = []
            y = 20
            for task in task_collection.tasks:
                button = ttk.Button(
                    self,
                    text=task.task,
                    command=partial(self.task_action, task.task),
                    style="blue.TButton",
                )
                button.place(x=x2, y=y, height=20, width=160)
                self.task_buttons.append(button)
                y += 20

            # subject info
            self.subject_button = ttk.Button(
                self,
                text="ADD SUBJECT INFO",
                command=self.add_subject_info,
                style="blue.TButton",
            )
            self.subject_button.place(x=x3, y=10, width=160, height=20)

            # subjects
            possible_subjects = sorted(
                list({subject.name for subject in utils.subjects.items})
            )
            possible_subjects = possible_subjects + ["NEW"]
            self.subject_combo = ttk.Combobox(self, state="disabled")
            self.subject_combo.place(x=x3, y=30, width=160, height=20)
            self.subject_combo["values"] = possible_subjects
            self.subject_combo.bind("<<ComboboxSelected>>", self.update_subject_combo)
            self.subject_combo.set("")
            self.task_combo = ttk.Combobox(self, state="disabled")
            self.task_combo.place(x=x3, y=50, width=160, height=20)
            values = ["Add control weight", "Add basal weight", "Add manual water"]
            values += [task.task for task in task_collection.tasks]
            self.task_combo["values"] = values
            self.task_combo.bind("<<ComboboxSelected>>", self.update_task_combo)
            self.task_combo.set("")

            self.task_label = tk.Label(self, text="")
            self.task_label.place(x=x3, y=70, width=75, height=20)

            self.task_value = tk.Entry(self, state="disabled")
            self.task_value.place(x=x3 + 75, y=70, width=75, height=20)

            self.task_label2 = tk.Label(self, text="")
            self.task_label2.place(x=x3, y=90, width=75, height=20)

            self.task_value2 = tk.Entry(self, state="disabled")
            self.task_value2.place(x=x3 + 75, y=90, width=75, height=20)

            self.task_label3 = tk.Label(self, text="")
            self.task_label3.place(x=x3, y=110, width=75, height=20)

            self.task_value3 = tk.Entry(self, state="disabled")
            self.task_value3.place(x=x3 + 75, y=110, width=75, height=20)

            self.task_label4 = tk.Label(self, text="")
            self.task_label4.place(x=x3, y=130, width=75, height=20)

            self.task_value4 = tk.Entry(self, state="disabled")
            self.task_value4.place(x=x3 + 75, y=130, width=75, height=20)

            self.subject_button2 = ttk.Button(
                self,
                text="",
                command=self.add_subject_info2,
                style="blue.TButton",
                state="disabled",
            )
            self.subject_button2.place(x=x3, y=150, width=160, height=20)

            # reload tasks
            self.reload_button = ttk.Button(
                self,
                text="RELOAD ACADEMY",
                command=self.reload_tasks,
                style="red.TButton",
            )
            self.reload_button.place(x=x3, y=250, width=160, height=20)

            # exit task
            self.exit_button = ttk.Button(
                self,
                text="EXIT TASK",
                command=self.exit_task,
                style="red.TButton",
                state="disabled",
            )
            self.exit_button.place(x=x3, y=350, width=160, height=20)

            # cameras
            self.image_label1 = tk.Label(self, anchor="w", justify="left")
            self.image_label1.place(x=640, y=0, width=640, height=380)

            self.image_label2 = tk.Label(self, anchor="w", justify="left")
            self.image_label2.place(x=0, y=480, width=640, height=340)

            self.image_label3 = tk.Label(self, anchor="w", justify="left")
            self.image_label3.place(x=0, y=0, width=640, height=480)

            # events
            y = 820
            self.event_labels = []
            for i in range(10):
                label = tk.Label(self, text="", anchor="w")
                label.place(x=10, y=y, width=620, height=18)
                y += 18
                self.event_labels.append(label)

            # plots
            try:
                self.canvas = FigureCanvasTkAgg(self.fig, master=self)
                self.canvas.get_tk_widget().place(x=640, y=380, width=1210, height=645)
            except:
                utils.log("Academy", " not created in rt_plots", "ERROR")
                pass

        else:  # setting task

            # first row in 8 parts
            tk.Label(self, text="", anchor="w", width=margin).grid(row=row, column=0)
            tk.Label(self, text="", anchor="w", width=first_cell).grid(
                row=row, column=1
            )
            tk.Label(self, text="", anchor="w", width=cell).grid(row=row, column=2)
            tk.Label(self, text="", anchor="w", width=cell).grid(row=row, column=3)
            tk.Label(self, text="", anchor="w", width=cell).grid(row=row, column=4)
            tk.Label(self, text="", anchor="w", width=cell).grid(row=row, column=5)
            tk.Label(self, text="", anchor="w", width=cell).grid(row=row, column=6)
            tk.Label(self, text="", anchor="w", width=cell).grid(row=row, column=7)
            tk.Label(self, text="", anchor="w", width=cell).grid(row=row, column=8)
            tk.Label(self, text="", anchor="w", width=cell).grid(row=row, column=9)
            tk.Label(self, text="", anchor="w", width=cell).grid(row=row, column=10)
            tk.Label(self, text="", anchor="w", width=cell).grid(row=row, column=11)
            tk.Label(self, text="", anchor="w", width=margin).grid(row=row, column=12)
            row += 1

            run_task_flag = True
            self.entries = []
            self.boolvars = []

            # name of task
            tk.Label(self, text=utils.gui_name, anchor="w", width=all_no_margins).grid(
                row=row, column=1, columnspan=11
            )
            row += 1
            ttk.Separator(self, orient=tk.HORIZONTAL).grid(
                row=row, column=1, columnspan=11, sticky="ew"
            )
            row += 1

            # space
            tk.Label(self, text="", anchor="w", width=margin).grid(row=row, column=0)
            row += 1

            # task info
            if utils.task.info is not None:
                tk.Label(
                    self, text=str(utils.task.info), anchor="w", width=all_no_margins
                ).grid(row=row, column=1, columnspan=11)
                row += 1
                tk.Label(self, text="", anchor="w", width=margin).grid(
                    row=row, column=0
                )
                row += 1

            # subject
            possible_subjects = sorted(
                list({subject.name for subject in utils.subjects.items})
            )
            possible_subjects = ["None"] + possible_subjects

            tk.Label(self, text="subject", anchor="e", width=first_cell).grid(
                row=row, column=1
            )

            self.subject0_combo = ttk.Combobox(self, width=15)
            self.subject0_combo.grid(row=row, column=2, columnspan=3, sticky="nsw")

            self.subject0_combo["values"] = possible_subjects

            try:
                position = possible_subjects.index(utils.task.subject)
            except ValueError:
                position = 0
            self.subject0_combo.current(position)

            # self.subject0_combo.bind('<<ComboboxSelected>>', self.update_subject0_combo)
            # self.subject0_combo.set('')

            row += 1

            # combo = ttk.Combobox(self, width=15, textvariable=self.subject_var)
            # combo['values'] = possible_subjects

            # try:
            #    position = possible_subjects.index(utils.task.subject)
            # except ValueError:
            #    position = 0
            # combo.current(position)

            # combo.grid(row=row, column=2, columnspan=3, sticky='nsw')
            # row += 1

            # space
            tk.Label(self, text="", anchor="w", width=margin).grid(row=row, column=0)
            row += 1

            # inputs
            all_inputs = utils.task.gui_input_fixed + utils.task.gui_input
            all_inputs_and_outputs = all_inputs + utils.task.gui_output
            all_inputs_and_outputs = (
                pd.Series(all_inputs_and_outputs).drop_duplicates().tolist()
            )

            for name in all_inputs_and_outputs:
                attribute = getattr(utils.task, name)
                if type(attribute) == bool:
                    # boolean variable
                    var = tk.BooleanVar()
                    var.set(attribute)
                    tk.Label(self, text=name, anchor="e", width=first_cell).grid(
                        row=row, column=1
                    )
                    check = tk.Checkbutton(self, variable=var, width=cell)
                    if name not in all_inputs:
                        check.configure(state="disabled")
                    check.grid(row=row, column=2)
                    self.entries.append(check)
                    self.boolvars.append(var)
                    row += 1
                elif type(attribute) == list:
                    # list
                    if len(attribute) <= 10:
                        # numbers
                        for i in range(len(attribute)):
                            tk.Label(
                                self, text=str(i + 1), anchor="w", width=margin
                            ).grid(row=row, column=i + 2)
                        row += 1

                        # name list
                        tk.Label(self, text=name, anchor="e", width=first_cell).grid(
                            row=row, column=1
                        )

                        if type(attribute[0]) == bool:
                            # boolean variables
                            for i in range(len(attribute)):
                                var = tk.BooleanVar()
                                var.set(attribute[i])
                                check = tk.Checkbutton(self, variable=var, width=cell)
                                if name not in all_inputs:
                                    check.configure(state="disabled")
                                check.grid(row=row, column=2 + i)
                                self.entries.append(check)
                                self.boolvars.append(var)
                            row += 1
                        else:
                            # float variables
                            for i in range(len(attribute)):
                                entry = tk.Entry(self, width=cell)
                                entry.insert(0, attribute[i])
                                if name not in all_inputs:
                                    entry.configure(state="disabled")
                                entry.grid(row=row, column=2 + i)
                                self.entries.append(entry)
                            row += 1
                    else:
                        # error
                        mytext = name + " list is too large (maximum 10 values)"
                        tk.Label(
                            self, text=mytext, anchor="w", width=all_no_margins
                        ).grid(row=row, column=1, columnspan=11)
                        run_task_flag = False
                        row += 1
                else:
                    # float variable
                    tk.Label(self, text=name, anchor="e", width=first_cell).grid(
                        row=row, column=1
                    )
                    entry = tk.Entry(self, width=cell)
                    entry.insert(0, attribute)
                    if name not in all_inputs:
                        entry.configure(state="disabled")
                    entry.grid(row=row, column=2)
                    self.entries.append(entry)
                    row += 1

            # spaces
            tk.Label(self, text="", anchor="w", width=margin).grid(row=row, column=0)
            row += 1
            tk.Label(self, text="", anchor="w", width=margin).grid(row=row, column=0)
            row += 1

            # run task
            if run_task_flag:
                ttk.Button(
                    self,
                    text="RUN TASK",
                    command=self.run_task,
                    width=three_cells,
                    style="blue.TButton",
                ).grid(row=row, column=2, columnspan=3, sticky="nsw")
                row += 1

            # space
            tk.Label(self, text="", anchor="w", width=margin).grid(row=row, column=0)
            row += 1

            # cancel task
            ttk.Button(
                self,
                text="DONE",
                command=self.cancel,
                width=three_cells,
                style="red.TButton",
            ).grid(row=row, column=2, columnspan=3, sticky="nsw")

    def close(self):
        self.pack_forget()
        self.window.destroy()

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.pack_forget()

    def reload(self):
        try:
            queues.reload_canvas.get_nowait()
            # print('drawing canvas')
            self.canvas.draw()
            # print('finish?')
        except Exception:
            pass

        if utils.change_gui:
            utils.change_gui = False

            if utils.change_gui7:
                utils.change_gui7 = False
                self.clear_and_draw()
                # print("ok drawing again")

            if utils.state == 0:
                self.title.configure(text="TASKS")
                self.cams_on_off["state"] = "normal"
                self.exit_button["state"] = "disabled"
                for button in self.task_buttons:
                    button["state"] = "normal"

            elif utils.state in [1, 2, 3, 4, 5]:
                self.title.configure(text=utils.gui_name)
                self.cams_on_off["state"] = "disabled"
                self.exit_button["state"] = "normal"
                for button in self.task_buttons:
                    button["state"] = "disabled"

            elif utils.state == 6:
                self.title.configure(text=utils.gui_name)
                self.cams_on_off["state"] = "disabled"
                self.exit_button["state"] = "disabled"
                for button in self.task_buttons:
                    button["state"] = "disabled"

            elif utils.state in [8, 9]:
                self.title.configure(text=utils.gui_name)
                if self.subject_name == "None":
                    self.cams_on_off["state"] = "normal"
                else:
                    self.cams_on_off["state"] = "disabled"
                self.exit_button["state"] = "normal"
                for button in self.task_buttons:
                    button["state"] = "disabled"

        else:
            self.update_image()
            self.update_events()
            self.window.update()

            # self.a = time_utils.now_seconds()
            # print((self.a - self.b) * 1000)
            # self.b = self.a

    def clear_and_draw(self):
        self.clear_frame()
        tk.Frame.__init__(self, self.window, width=self.width, height=self.height)
        self.draw()
        self.pack()
        self.reload()

    def reload_tasks(self):
        utils.relaunch = True

        if utils.state != 0:
            showinfo("RELAUNCH", "The system will relaunch when the box is empty.")

    def tags_on_off1_button(self):
        if utils.reading_tags == 1:
            utils.reading_tags = 0
        else:
            utils.reading_tags = 1
        self.change_reading_tags()

    def tags_on_off2_button(self):
        if utils.reading_tags == 2:
            utils.reading_tags = 0
        else:
            utils.reading_tags = 2
        self.change_reading_tags()

    def tags_on_off3_button(self):
        if utils.reading_tags == 3:
            utils.reading_tags = 0
        else:
            utils.reading_tags = 3
        self.change_reading_tags()

    def cams_on_off_button(self):
        if self.cams_on_off["text"] == "Preview Cams":
            self.cams_on_off.configure(text="Hide Cams")
            self.cams_on_off.configure(style="red.TButton")
            cam2.put_state("active")
            cam3.put_state("active")
        else:
            self.cams_on_off.configure(text="Preview Cams")
            self.cams_on_off.configure(style="green.TButton")
            cam2.put_state("inactive")
            cam3.put_state("inactive")

    @staticmethod
    def task_action(name):
        for task in task_collection.tasks:
            if task.task == name:
                utils.task = task
                utils.task.init_variables()
        utils.gui_name = name
        utils.change_to_state = 7  # setting.task

    def run_task(self):
        if len(utils.task.gui_output) == 0:
            utils.task.init_variables()

        try:
            # self.subject_name = self.subject_var.get()
            self.subject_name = self.subject0_combo.get()
            self.subject = utils.subjects.read_last_value_excluding(
                "name",
                self.subject_name,
                "task",
                ["manual_water", "control_weight", "basal_weight"],
            )

            print(self.subject_name)
            print(self.subject)

            i = 0
            self.properties = []
            for item in self.entries:
                if type(item) == tk.Entry:
                    self.properties.append(float(item.get()))
                else:
                    self.properties.append(self.boolvars[i].get())
                    i += 1

            j = 0
            gui_input = utils.task.gui_input_fixed + utils.task.gui_input
            for name in gui_input:
                attribute = getattr(utils.task, name)
                if type(attribute) == list:
                    length = len(attribute)
                    values = self.properties[j : j + length]
                    setattr(utils.task, name, values)
                    j += length
                else:
                    setattr(utils.task, name, self.properties[j])
                    j += 1

            utils.gui_name = self.subject_name + " " + utils.gui_name

        except ValueError:
            return

        utils.task.configure_gui()
        utils.subject = self.subject
        utils.change_to_state = 8  # running direct task

    def update_image(self):
        try:
            frame = cam1.image_queue.get_nowait()
            a = Image.fromarray(frame[20:400, :, :])
            b = ImageTk.PhotoImage(image=a, master=self.window)
            self.image_label1.configure(image=b)
            self.image_label1._image_cache = b  # avoid garbage collection
        except Exception:
            pass

        try:
            frame = cam2.image_queue.get_nowait()
            a = Image.fromarray(frame[140:, :, :])
            b = ImageTk.PhotoImage(image=a, master=self.window)
            self.image_label2.configure(image=b)
            self.image_label2._image_cache = b  # avoid garbage collection
        except Exception:
            pass

        try:
            frame = cam3.image_queue.get_nowait()
            a = Image.fromarray(frame)
            b = ImageTk.PhotoImage(image=a, master=self.window)
            self.image_label3.configure(image=b)
            self.image_label3._image_cache = b  # avoid garbage collection
        except Exception:
            pass

    def update_events(self):
        if utils.state != 7:
            last_events = utils.events.items[-10:]
            idx = 0
            for event in last_events:
                label = self.event_labels[idx]
                text = (
                    event.date
                    + "     "
                    + str(event.subject)
                    + "     "
                    + str(event.description)
                )
                if event.type == "ERROR":
                    label["fg"] = "red"
                elif event.type == "START":
                    label["fg"] = "blue"
                    text += "     " + "START"
                elif event.type == "END":
                    label["fg"] = "purple"
                    text += "     " + "END"
                else:
                    label["fg"] = "gray"
                label["text"] = text
                idx += 1

    def add_subject_info(self):
        self.subject_button["state"] = "disabled"
        self.subject_button2["state"] = "normal"
        self.subject_button["text"] = ""
        self.subject_button2["text"] = "DONE"
        self.task_label["text"] = "value:"
        self.task_label2["text"] = ""
        self.task_label3["text"] = ""
        self.task_label4["text"] = ""

        self.subject_combo["state"] = "normal"
        self.task_combo["state"] = "normal"
        self.task_value["state"] = "normal"
        self.task_value2["state"] = "disabled"
        self.task_value3["state"] = "disabled"
        self.task_value4["state"] = "disabled"

        self.subject_combo.current(0)
        try:
            self.subject0_combo.current(0)
        except:
            pass
        try:
            self.task_combo.current(0)
        except:
            pass

    def add_subject_info2(self):
        subject = self.subject_combo.get()
        task = self.task_combo.get()
        value = self.task_value.get()
        value2 = self.task_value2.get()
        if subject == "NEW":
            value3 = self.task_value3.get()
            value4 = self.task_value4.get()
            self.add_subject_data2(task, value, value2, value3, value4)
        else:
            self.add_subject_data(subject, task, value, value2)

        self.subject_button["state"] = "normal"
        self.subject_button2["state"] = "disabled"
        self.subject_button["text"] = "ADD SUBJECT INFO"
        self.subject_button2["text"] = ""
        self.task_label["text"] = ""
        self.task_label2["text"] = ""
        self.task_label3["text"] = ""
        self.task_label4["text"] = ""
        self.subject_combo.set("")
        self.task_combo.set("")

        self.subject_combo["state"] = "disabled"
        self.task_combo["state"] = "disabled"
        self.task_value["state"] = "disabled"
        self.task_value2["state"] = "disabled"
        self.task_value3["state"] = "disabled"
        self.task_value4["state"] = "disabled"

    def x_max_bigger(self):
        utils.x_max += 1
        self.upload_button["text"] = "Update plots (" + str(utils.x_max) + " days)"

    def x_max_smaller(self):
        if utils.x_max > 1:
            utils.x_max -= 1
            self.upload_button["text"] = "Update plots (" + str(utils.x_max) + " days)"

    def update_subject_combo(self, value):
        subject = self.subject_combo.get()

        if subject == "NEW":
            self.task_combo["values"] = [task.task for task in task_collection.tasks]
            self.task_label["text"] = "name:"
            self.task_label2["text"] = "tag"
            self.task_label3["text"] = "stage"
            self.task_label4["text"] = "substage"
            self.task_value["state"] = "normal"
            self.task_value2["state"] = "normal"
            self.task_value3["state"] = "normal"
            self.task_value4["state"] = "normal"
        else:
            values = ["Add control weight", "Add basal weight", "Add manual water"]
            values += [task.task for task in task_collection.tasks]
            self.task_combo["values"] = values
            self.task_label["text"] = "value:"
            self.task_label2["text"] = ""
            self.task_value["state"] = "normal"
            self.task_value2["state"] = "disabled"
            self.task_value3["state"] = "disabled"
            self.task_value4["state"] = "disabled"

        self.task_value.delete(0, "end")
        self.task_value2.delete(0, "end")
        self.task_value3.delete(0, "end")
        self.task_value4.delete(0, "end")
        self.task_combo.current(0)

    def update_task_combo(self, value):
        task = self.task_combo.get()

        if task in ["Add control weight", "Add basal weight", "Add manual water"]:
            self.task_label["text"] = "value:"
            self.task_label2["text"] = ""
            self.task_value["state"] = "normal"
            self.task_value2["state"] = "disabled"
            self.task_value3["state"] = "disabled"
            self.task_value4["state"] = "disabled"
        else:
            self.task_label["text"] = "stage:"
            self.task_label2["text"] = "substage"
            self.task_value["state"] = "normal"
            self.task_value2["state"] = "normal"
            self.task_value3["state"] = "disabled"
            self.task_value4["state"] = "disabled"

    def add_subject_data(self, subject, task, value, value2):
        try:
            subject_item = utils.subjects.read_last_value_excluding(
                "name",
                subject,
                "task",
                ["manual_water", "control_weight", "basal_weight"],
            )

            value = float(value)

            if task == "Add control weight":
                utils.subjects.add_new_item(
                    {
                        "task": "control_weight",
                        "stage": 0.0,
                        "substage": 0.0,
                        "wait_seconds": 0.0,
                        "weight": value,
                        "water": 0.0,
                    },
                    item=subject_item,
                )
            elif task == "Add basal weight":
                utils.subjects.add_new_item(
                    {
                        "task": "basal_weight",
                        "stage": 0.0,
                        "substage": 0.0,
                        "wait_seconds": 0.0,
                        "weight": value,
                        "water": 0.0,
                    },
                    item=subject_item,
                )
            elif task == "Add manual water":
                utils.subjects.add_new_item(
                    {
                        "task": "manual_water",
                        "stage": 0.0,
                        "substage": 0.0,
                        "wait_seconds": 0.0,
                        "weight": 0.0,
                        "water": value,
                    },
                    item=subject_item,
                )
            else:
                value2 = float(value2)
                utils.subjects.add_new_item(
                    {
                        "name": subject,
                        "water": 0.0,
                        "task": task,
                        "stage": value,
                        "substage": value2,
                        "wait_seconds": 0.0,
                    },
                    item=subject_item,
                )

            showinfo("SAVED", "Subject data saved")

        except Exception:
            showinfo("ERROR", "Error saving data")

        self.task_value.delete(0, "end")
        self.task_value2.delete(0, "end")

    def add_subject_data2(self, task, subject, tag, stage, substage):
        try:
            stage = stage
            substage = substage

            utils.subjects.add_new_item(
                {
                    "name": subject,
                    "tag": tag,
                    "weight": 0.0,
                    "water": 0.0,
                    "task": task,
                    "stage": stage,
                    "substage": substage,
                    "wait_seconds": 0.0,
                }
            )

            task_collection.create_subjects_dict()
            showinfo("SAVED", "Subject data saved")
        except Exception:
            showinfo("ERROR", "Error saving data")

        self.task_value.delete(0, "end")
        self.task_value2.delete(0, "end")
        self.task_value3.delete(0, "end")
        self.task_value4.delete(0, "end")

    def change_reading_tags(self):
        if utils.reading_tags == 0:
            self.tags_on_off1.configure(text="Tag read AUTO = OFF")
            self.tags_on_off1.configure(style="red.TButton")
            self.tags_on_off2.configure(text="Tag read DAY = OFF")
            self.tags_on_off2.configure(style="red.TButton")
            self.tags_on_off3.configure(text="Tag read NIGHT = OFF")
            self.tags_on_off3.configure(style="red.TButton")
            arduino.turn_led_off()
            cam1.put_state("daily")
            #cam2.put_state("daily")
        elif utils.reading_tags == 1:
            self.tags_on_off1.configure(text="Tag read AUTO = ON")
            self.tags_on_off1.configure(style="green.TButton")
            self.tags_on_off2.configure(text="Tag read DAY = OFF")
            self.tags_on_off2.configure(style="red.TButton")
            self.tags_on_off3.configure(text="Tag read NIGHT = OFF")
            self.tags_on_off3.configure(style="red.TButton")
            arduino.turn_led_on()
            cam1.put_state("daily")
            #cam2.put_state("daily")
        elif utils.reading_tags == 2:
            self.tags_on_off1.configure(text="Tag read AUTO = OFF")
            self.tags_on_off1.configure(style="red.TButton")
            self.tags_on_off2.configure(text="Tag read DAY = ON")
            self.tags_on_off2.configure(style="green.TButton")
            self.tags_on_off3.configure(text="Tag read NIGHT = OFF")
            self.tags_on_off3.configure(style="red.TButton")
            arduino.turn_led_on()
            cam1.put_state("day")
            #cam2.put_state("day")
        else:
            self.tags_on_off1.configure(text="Tag read AUTO = OFF")
            self.tags_on_off1.configure(style="red.TButton")
            self.tags_on_off2.configure(text="Tag read DAY = OFF")
            self.tags_on_off2.configure(style="red.TButton")
            self.tags_on_off3.configure(text="Tag read NIGHT = ON")
            self.tags_on_off3.configure(style="green.TButton")
            arduino.turn_led_on()
            cam1.put_state("night")
            #cam2.put_state("night")

    @staticmethod
    def close_window():
        queues.tags.put(("a", "EXIT_ACADEMY"))

    @staticmethod
    def exit_task():
        queues.tags.put(("a", "EXIT_TASK"))

    @staticmethod
    def update_canvas():
        if utils.state != 7:
            queues.update_plots.put(True)

    @staticmethod
    def open_door1():
        arduino.open_door1()

    @staticmethod
    def open_door2():
        arduino.open_door2()

    @staticmethod
    def close_door1():
        arduino.close_door1()

    @staticmethod
    def close_door2():
        arduino.close_door2()

    @staticmethod
    def open_inner_door():
        bpod.open_inner_door(utils.task)

    @staticmethod
    def close_inner_door():
        bpod.close_inner_door(utils.task)

    @staticmethod
    def play_buzzer1():
        bpod.play_buzzer1(utils.task)

    @staticmethod
    def play_buzzer2():
        bpod.play_buzzer2(utils.task)

    @staticmethod
    def cancel():
        utils.change_to_state = 0

    @staticmethod
    def get_temperature():
        arduino.get_temperature()

    @staticmethod
    def tare_scale():
        arduino.tare_scale()

    @staticmethod
    def get_weight():
        arduino.get_weight()


class FakeWindow:
    def __init__(self):
        self.connected = False

    def update(self):
        pass


gui = Gui()
