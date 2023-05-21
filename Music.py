import mingus.containers as container
import mingus.core.keys as keys
import mingus.core.chords as chords
import mingus.core.notes as notes
import mingus.core.progressions as progressions
from mingus.midi import midi_file_out as midiOut
from mingus.containers.instrument import MidiInstrument
import random
import pygame

class MusicGenerator :
    def __init__(self) -> None:
        self.keysList = []
        self.keysList.extend(keys.major_keys)
        self.keysList.extend(keys.minor_keys)
        freq = 44100   
        bitsize = -16   
        channels = 2 
        buffer = 1024 
        pygame.mixer.init(freq, bitsize, channels, buffer)
        progressionList = progressions.numerals
        # Daftar progression yang enak didengar. Sumber : https://mixedinkey.com/captain-plugins/wiki/best-chord-progressions/
        #                                                 https://www.musical-u.com/learn/exploring-common-chord-progressions/
        goodProgressions = [["vi", "V", "IV", "V"], ["IV", "I6", "ii"], ["I", "V6", "vi", "V"], ["I", "V", "vi", "iii", "IV"],
                            ["i", "III", "VII", "VI"], ["i", "V", "vi","IV"], ["i", "VII", "III", "VI"], ["I", "vi", "IV", "V"],
                            ["I", "IV", "vi", "V"], ["I", "V", "vi", "IV"], ["I", "IV", "V"], ["ii", "V", "I"], ["vi", "IV", "I", "V"]]

    def mapValue(self, value, min1, max1, min2, max2) :
        # Figure out how 'wide' each range is
        leftSpan = max1 - min1
        rightSpan = max2 - min2

        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - min1) / float(leftSpan)

        # Convert the 0-1 range into a value in the right range.
        return int(min2 + (valueScaled * rightSpan))

    def searchLineEquation(self, p1, p2) :
        # Search the line equation for line p1 p2
        m = (p2[1]-p1[1])/(p2[0]-p1[0])
        c = p1[1] - m*p1[0]
        return m,c

    def hullToNote(self, hull, mode) :
        # Mengubah setiap titik dalam convex hull menjadi not mayor (sumbu x) dan minor (sumbu y)
        noteList = []
        octave = []
        if (mode == 0) : # Map
            max_X = max(hull, key=lambda coor : coor[0])[0]
            min_X = min(hull, key=lambda coor : coor[0])[0]
            max_Y = max(hull, key=lambda coor : coor[1])[1]
            min_Y = min(hull, key=lambda coor : coor[1])[1]
            for coor in hull :
                noteList.append(notes.int_to_note(self.mapValue(coor[0], min_X, max_X, 0, 11)))
                octave.append(self.mapValue(coor[1], min_Y, max_Y, 3, 8))
        else : # Mod
            for coor in hull :
                noteList.append(notes.int_to_note(int(coor[0] % 12)))
                octave.append(int(coor[1] % 6) + 3)
        return noteList, octave

    def hullToTrack(self, hull, melodyInstrument, chordInstrument, bpm, mode) :
        # Ubah setiap vertex pada convex hull menjadi not
        noteList, octave = self.hullToNote(hull, mode)
        # Tentukan kunci not-not dalam convex hull. Jika tidak ada yang sesuai, gunakan key major C dan minor a
        key = "C"
        lastNumOfSame = 0
        for k in self.keysList :
            currNotesList = keys.get_notes(k)
            numOfSame = 0
            for n in set(noteList) :
                if n in currNotesList :
                    numOfSame += 1
            if (numOfSame > lastNumOfSame) :
                key = k
                lastNumOfSame = numOfSame
        melodyInstrum = MidiInstrument()
        melodyInstrum.instrument_nr = melodyInstrument
        chordInstrum = MidiInstrument()
        chordInstrum.instrument_nr = chordInstrument
        trackMelody = container.Track(melodyInstrum)
        trackChord = container.Track(chordInstrum)
        progression = []
        for i in range(len(noteList)) : 
            currChord = chords.triad(noteList[i], key)
            progression.append(progressions.determine(currChord, key, True))
            chordDuration = random.choice([1,2,4])
            currDuration = 0
            while currDuration < 1/chordDuration :
                noteLength = random.choice([2,4,8])
                if noteLength < chordDuration :
                    noteLength = chordDuration
                trackMelody.add_notes(container.NoteContainer(container.Note(random.choice(currChord), octave[i])), noteLength)
                currDuration += 1/noteLength
            trackChord.add_notes(currChord, chordDuration)
        com = container.Composition()
        com.add_track(trackMelody)
        com.add_track(trackChord)
        midiOut.write_Composition("Result.mid", com, bpm=bpm)
        return progression, key
    
    def play_music(self, music_file, volume):
        pygame.mixer.music.set_volume(volume)
        clock = pygame.time.Clock()
        try:
            pygame.mixer.music.load(music_file)
        except pygame.error:
            return
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            # check if playback has finished
            clock.tick(30)