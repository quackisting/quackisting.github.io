##GUI/Song info collection
from tkinter import *
from tkinter.filedialog import *
import winsound as ws
import subprocess as sp
from tinytag import TinyTag
from tkinter import ttk

##Graphing/Audio Visualizer
import pyaudio
import struct
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

global songs
songs = []
songNamesList = {}
root = Tk()
leftFrame = ttk.Frame(root, relief="groove", borderwidth=10)
frame = ttk.Frame(leftFrame, relief="groove", borderwidth=10)

#######################################################################################################################################################

##The function has a boolean parameter named cleanSongs that decides whether or not the called
#line wants to clear the songs.
##For every widget in the object root (the tk master window), destroy all the widgets.
##Create a frame that resides on the left side and initiate all essential buttons. Also,
#initialize the audio visualizer graph into root.
def clearReplace(cleanSongs):
    if cleanSongs:
        del songs[:]
        songNamesList.clear()
        initSongButtons()
    for widget in root.winfo_children():
        widget.destroy()    
    
    leftFrame = ttk.Frame(root, relief="groove", borderwidth=10)
    frame = ttk.Frame(leftFrame, relief="groove", borderwidth=10)
    Label(root, text="The program only supports wav files. You need ffmpeg installed to convert to .wav.").pack()
    Button(frame, text="Choose Songs", width = 25, command=chooseSongs).pack(side=LEFT, expand=True) ##Create a button that the user can click on to choose their songs.
    Button(frame, text="Clear Songs", command=lambda:clearReplace(True)).pack(side=LEFT, expand=True)
    Button(frame, text="STOP", command=lambda: stopSong()).pack(side=LEFT, expand=True)
    Button(frame, text="Convert Songs Into WAV", command=lambda: convertFFMPEG(songs)).pack()
    frame.pack()
    canvas = FigureCanvasTkAgg(fig, master = leftFrame)
    canvas.get_tk_widget().pack()
    leftFrame.pack(expand=True, side=LEFT)

#######################################################################################################################################################

##INITIALIZING AUDIO CHANNEL FOR AUDIO VISUALIZER
CHUNK = 1024 * 4
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

##creating an instance of the pyaudio object
p = pyaudio.PyAudio()

##opening an audio stream
stream = p.open(
    format = FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    output=True,
    frames_per_buffer=CHUNK
)

##setting a figure, and axes 
fig, ax = plt.subplots()

x= np.arange(0,2 * CHUNK, 2)
line, = ax.plot(x, np.random.rand(CHUNK))
##setting the limits of the graph
ax.set_ylim(0,255)
ax.set_xlim(0, CHUNK)

##remove the axes legends because they ugly
plt.axis('off')

##initializing the canvas of the graph onto the tk root object
canvas = FigureCanvasTkAgg(fig, master = root)
canvas.get_tk_widget().pack()
    
##a function that updates the graph 
def updateGraph():
    
    data = stream.read(CHUNK)
    data_int = struct.unpack(str(CHUNK)+'h', data)
    line.set_ydata(data_int)
    fig.canvas.draw()
    fig.canvas.flush_events()
    
    root.after(30, updateGraph)



#plt.show()  
#######################################################################################################################################################


##a function that clears, and replaces all tkinter widgets, then prompts the user for song choices.
#with this input, a loop runs that runs through the entire list of songs, removes bloat
#text (as a result of the data being a textiowrapper), then appending those songs into a new 
#song list. Then, the function calls the evaluateSongList function, and then also
#calls the initSongButtons function.
def chooseSongs():
    clearReplace(False)
    temp = askopenfiles(mode = "r") ##open a file dialog to request file input from user
    for x in range(len(temp)): ##for every file that the user input, remove bloat IOWrapper text out of the string and then append it to the Songs list.
        tempSong = str(temp[x])
        tempSong = tempSong.replace("<_io.TextIOWrapper name='", "")
        tempSong = tempSong.replace("<_io.TextIOWrapper name=\"", "")
        tempSong = tempSong.replace("' mode='r' encoding='cp1252'>", "")
        tempSong = tempSong.replace("\" mode='r' encoding='cp1252'>", "")
        songs.append(tempSong)
    evaluateSongList() ##Call the evaluateSongList Function
    initSongButtons()



##Runs through the list of all the song names and makes them a button. Each button, onClick,
#calls lambda startSong(y). y=the order of the song.
def initSongButtons():
    for y, SL_NAME in songNamesList.items(): ##For every item in songNamesList, create a tkinter button.
        Button(root, text=f"{y + 1} - {SL_NAME}", command= lambda y=y: startSong(y)).pack() ##I'mn having an issue at startSong(y). After all of the buttons have been created, if the user clicks
        ##on a button, the function only returns the last song in SongNamesList. This is an issue because the user should be able to choose any song.

##The function has a parameter songsGiven, which should be the list {songs}. Then, the function
#uses a loop to run through the entire list, replacing "mp3" and "flac" into "wav". Then,
#it adds this string literal to the variable wavFormat.
##With wavFormat, subprocess runs a command through cmd. FFMPEG must be installed on the
#host computer. With this command, ffmpeg converts either an mp3 file or a flac file into
#a wav file in order for winsound to interpret the data correctly, as winsound cannot play
#mp3 or flac files.
def convertFFMPEG(songsGiven):
    for song in songsGiven:
        if "mp3" in song:
            wavFormat = song.replace("mp3", "wav")
        elif "flac" in song:
            wavFormat = song.replace("flac", "wav")
        sp.run(f"ffmpeg -i \"{song}\" \"{wavFormat}\"", shell =True)
    clearReplace(True)
    initSongButtons()

##Takes in a song index integer as a parameter, then uses winsound to play the sound using
#songs[songsIndex]
def startSong(songIndex):
    clearReplace(False)
    initSongButtons()
    Label(root, text = songNamesList[songIndex]).pack() ##output the song that the user clicked on
    ws.PlaySound(songs[songIndex], ws.SND_ASYNC)
    
##Stops all audio playback using winSound.
def stopSong():
    ws.PlaySound(None, ws.SND_FILENAME)
    clearReplace(False)
    initSongButtons()

##Loops through the entire list of songs. TinyTag gets the audio album, title, and artist using
#the .wav file metadata thats embedded in the file.
##With this metadata, the loop updates a dictionary named songNamesList for every song there is
#with a string literal including the album, title, and artist.
def evaluateSongList():
    for i, x in enumerate(songs): ##for every item in songs
        audio = TinyTag.get(x)
        song_name = f"[{audio.album}]: {audio.title} - {audio.artist}"
        songNamesList.update({i:song_name})

#######################################################################################################################################################

##Use the master.after(milliseconds, function) tkinter function to call the updateGraph function()
#parallel with all other functions. Without this specific call, the program will not run correctly.
root.after(30, updateGraph)
clearReplace(False)

##Ensure the tkinter window stays open during the program.
root.mainloop()
