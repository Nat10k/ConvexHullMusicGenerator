from tkinter.filedialog import askopenfilename
import customtkinter as ctk
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)
import pathlib
import math
from threading import *
from ConvexHull import ConvexHull
import Music
import os

class GUI (ctk.CTk) :
    def __init__(self):
        super().__init__()
        self.musicGenerator = Music.MusicGenerator()
        self.volume = ctk.DoubleVar()
        self.bpm = ctk.IntVar()
        self.melodyInstr = ctk.StringVar()
        self.chordInstr = ctk.StringVar()
        self.column1 = ctk.StringVar()
        self.column2 = ctk.StringVar()
        self.mode = ctk.IntVar()
        self.column1.set("Note axis")
        self.column2.set("Pitch axis")
        self.melodyInstr.set("")
        self.volume.set(0.3)
        self.bpm.set(120)
        self.mode.set(0)
        self.df = None
        self.hull = []

        self.title("Convex Hull Music Generator")

        # Graph 
        self.graphFrame = ctk.CTkFrame(self)
        self.graphFrame.grid(row=0, column=0)
        self.fig = plt.Figure(dpi=100)
        self.graphDisplay = FigureCanvasTkAgg(self.fig,self.graphFrame)
        self.graphDisplay.get_tk_widget().grid(row=0, column=0)
        self.progressionLbl = ctk.CTkLabel(self.graphFrame, text="Chord progression : ")
        self.progressionLbl._wraplength = 50
        self.progressionLbl.grid(row=1, column=0)
        self.keyLbl = ctk.CTkLabel(self.graphFrame, text="Key :")
        self.keyLbl.grid(row=2, column=0)

        # Inputs
        self.inputFrame = ctk.CTkFrame(self)
        self.inputFrame.grid(row=0, column=1)
        self.uploadFileBtn = ctk.CTkButton(self.inputFrame, text="Upload file", command=self.openDataFile)
        self.uploadFileBtn.grid(row=0, column=0, padx=15, pady=10)
        self.fileLbl = ctk.CTkLabel(self.inputFrame, text="")
        self.fileLbl.grid(row=0,column=1, padx=5, pady=10)
        self.dropDownBtn1 = ctk.CTkComboBox(self.inputFrame, values=[""], variable=self.column1, command=self.generateHull)
        self.dropDownBtn1.grid(row=1, column=0, padx=15, pady=10)
        self.dropDownBtn2 = ctk.CTkComboBox(self.inputFrame, values=[""], variable=self.column2, command=self.generateHull)
        self.dropDownBtn2.grid(row=1, column=1, padx=15, pady=10)
        self.generateMusicBtn = ctk.CTkButton(self.inputFrame, text="Generate Music", command=self.generateMusic)
        self.generateMusicBtn.grid(row=2, column=0, padx=15, pady=10)
        self.playBtn = ctk.CTkButton(self.inputFrame, text="Play", command=self.threadPlayMusic)
        self.playBtn.grid(row=2, column=1, padx=15, pady=10)
        self.modeLbl = ctk.CTkLabel(self.inputFrame, text="Select mapping mode")
        self.modeLbl.grid(row=3, column=0, columnspan=2, padx=15, pady=10)
        self.mapModeBtn = ctk.CTkRadioButton(self.inputFrame, text="Map", variable=self.mode, value=0)
        self.mapModeBtn.grid(row=4, column=0, padx=15, pady=10)
        self.modModeBtn = ctk.CTkRadioButton(self.inputFrame, text="Mod", variable=self.mode, value=1)
        self.modModeBtn.grid(row=4, column=1, padx=15, pady=10)
        self.volumeLabel = ctk.CTkLabel(self.inputFrame, text="Volume")
        self.volumeLabel.grid(row=5, column=0, padx=15, pady=10, columnspan=2)
        self.volumeSlider = ctk.CTkSlider(self.inputFrame, variable=self.volume, from_=0, to=1)
        self.volumeSlider.grid(row=6, column=0, padx=15, pady=10, columnspan=2)
        self.bpmLabel = ctk.CTkLabel(self.inputFrame,text="Beats Per Minute (BPM)")
        self.bpmLabel.grid(row=7, column=0, padx=15, pady=10, columnspan=2)
        self.bpmSlider = ctk.CTkSlider(self.inputFrame, variable=self.bpm, from_=60, to=200)
        self.bpmSlider.grid(row=8, column=0, padx=15, pady=10, columnspan=2)
        self.melodyInstrumentLbl = ctk.CTkLabel(self.inputFrame, text="Note instrument :")
        self.melodyInstrumentLbl.grid(row=9, column=0, padx=10, pady=10)
        self.melodyInstrumentTxtBox = ctk.CTkTextbox(self.inputFrame, height=20)
        self.melodyInstrumentTxtBox.grid(row=9, column=1, padx=10, pady=10)
        self.chordInstrumentLbl = ctk.CTkLabel(self.inputFrame, text="Chord instrument :")
        self.chordInstrumentLbl.grid(row=10, column=0, padx=10, pady=10)
        self.chordInstrumentTxtBox = ctk.CTkTextbox(self.inputFrame, height=20)
        self.chordInstrumentTxtBox.grid(row=10, column=1, padx=10, pady=10)
        self.instrumentGuideLbl = ctk.CTkLabel(self.inputFrame, text="Input 0 - 127 in the instrument fields\nComplete instrument list :\nhttps://fmslogo.sourceforge.io/manual/midi-instrument.html")
        self.instrumentGuideLbl.grid(row=11, column=0, padx=10, pady=10, columnspan=2)
        self.errorLbl = ctk.CTkLabel(self.inputFrame, text="", text_color="red")
        self.errorLbl.grid(row=12, column=0, padx=10, pady=10, columnspan=2)
    
    def openDataFile(self) :
        # Membuka file yang berisi data yang ingin dicari convex hull-nya
        filePath = askopenfilename(filetypes=[("text files", "*.csv"), ("text files", "*.json")])
        path = pathlib.Path(filePath)
        self.fileLbl.configure(text=path.name)
        if (path.suffix == ".csv") :
            self.df = pd.read_csv(filePath)
        elif (path.suffix == ".json") :
            self.df = pd.read_json(filePath)
        self.column1.set("Note axis")
        self.column2.set("Pitch axis")
        cols = []
        for col in self.df.columns :
            if (pd.api.types.is_numeric_dtype(self.df[col])) :
                cols.append(col)
        self.dropDownBtn1.configure(values=cols)
        self.dropDownBtn2.configure(values=cols)
    
    def generateHull(self, val) :
        # Membuat convex hull
        if (self.column1.get() != "Note axis" and self.column2.get() != "Pitch axis") :
            try :
                self.errorLbl.configure(text="")
                t = Thread(target=ConvexHull.searchHull, args=[list(zip(self.df[self.column1.get()],self.df[self.column2.get()])), self.hull])
                t.start()
                t.join()
                t = Thread(target=self.plotGraph, args=[self.hull])
                t.start()
            except :
                self.errorLbl.configure(text="Failed to generate hull")
        
    def generateMusic(self) :
        if (self.hull != []) :
            self.errorLbl.configure(text="")
            try : 
                melodyInstr = int(self.melodyInstrumentTxtBox.get("0.0", ctk.END))
                chordInstr = int(self.chordInstrumentTxtBox.get("0.0", ctk.END))
                if (melodyInstr < 0 or melodyInstr > 127 or chordInstr < 0 or chordInstr > 127) :
                    raise Exception()
                progression, key = self.musicGenerator.hullToTrack(self.hull, melodyInstr, chordInstr, self.bpm.get(), self.mode.get())
                progString = ""
                for i in range(len(progression)) :
                    if (len(progression[i]) > 0) :
                        progString += progression[i][0]
                        if i < len(progression)-1 :
                            progString += " - "
                self.progressionLbl.configure(text="Chord progression : " + progString)
                self.keyLbl.configure(text="Key : " + key)
            except :
                self.errorLbl.configure(text="Instrument not valid")

    def playMusic(self) :
        self.errorLbl.configure(text="")
        try :
            self.musicGenerator.play_music("Result.mid", self.volume.get())
        except :
            self.errorLbl.configure(text="Failed to load music")
    
    def threadPlayMusic(self) :
        t = Thread(target=self.playMusic)
        t.daemon = True
        t.start()
            
    def euclideanDist(self, c1, c2) :
        return math.sqrt(pow(c2[0] - c1[0], 2) + pow(c2[1] - c1[1], 2))

    def add_edge_to_graph(self, G, e1, e2, w) :
        G.add_edge(e1, e2, weight=w)

    def plotGraph(self, coords) :
        # Menggambar graf dari daftar koordinat
        pos = {i : (coords[i][0],coords[i][1]) for i in range(len(coords))}
        self.g = nx.Graph()
        edges = [(i,i+1,self.euclideanDist(coords[i],coords[i+1])) for i in range(len(coords)-1)]
        edges.append((len(coords)-1, 0, self.euclideanDist(coords[len(coords)-1], coords[0])))
        for e in edges :
            self.add_edge_to_graph(self.g, e[0], e[1], e[2])
        a = self.fig.add_subplot(111)
        nx.draw_networkx(self.g, pos=pos, ax=a, with_labels=True, node_color=['lightblue'],
                    node_size=500, font_size=14, font_weight='bold',
                    edge_color='black')
        self.graphDisplay.draw()

gui = GUI()
gui.protocol("WM_DELETE_WINDOW", gui.quit)
gui.mainloop()