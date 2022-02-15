import copy
import sys
import threading
import time
import rtmidi
from musx import Score, Note, Seq, MidiEvent, note_on, note_off, choose

from ChordGenerator import ChordGenerator
from RhythmGenerator import RhythmGenerator


def _notes_to_midi(seq):
    """
    Converts a sequence of notes into a sequence of time-ordered midi messages.

    Parameters
    ----------
    seq : Seq
        A sequence containing Note objects.
    """
    midi = Seq()
    for note in seq:
        key = int(note.pitch if isinstance(note.pitch, (int, float)) else note.pitch.keynum())
        vel = int(note.amplitude * 127)
        chan = note.instrument
        on = MidiEvent(note_on(chan, key, vel), note.time)
        off = MidiEvent(note_off(chan, key, 127), note.time + note.duration)
        midi.add(on)
        midi.add(off)
    return midi


def _midi_player(midi, port):
    """
    Thread function that plays a list of midi messages out the port.

    Parameters
    ----------
    midi : list
        A time sorted list of MidiEvent objects
    port : rtmidi.Port
        An open rtmidi output port.
    """
    length = len(midi)
    nexttime = midi[0].time
    thistime = nexttime
    i = 0

    while i < length:
        if midi[i].time == thistime:
            port.send_message(midi[i].message)
            i += 1
            continue
        nexttime = midi[i].time
        time.sleep(nexttime - thistime)
        thistime = nexttime


def play_midi(seq, port, block=True):
    """
    Plays a Note or MidiEvent sequence out an open rtmidi output port. If
    the sequence contains notes they are first converted into midi events
    before playback.

    Parameters
    ----------
    seq : Seq
        A sequence of Note or MidiEvent objects.
    port : rtmidi.MidiOut
        An open rtmidi MidiOut object.
    block : bool
        If true then midi_play() will block for the duration of the playback.
    """
    if not seq.events:
        raise ValueError(f"no midi events to play")
    if not 'rtmidi' in sys.modules:
        raise RuntimeError(f"module rtmidi is not loaded")
    if not isinstance(port, sys.modules['rtmidi'].MidiOut):
        raise TypeError(f"port is not an instance of rtmidi.MidiOut")
    if isinstance(seq[0], Note):
        seq = _notes_to_midi(seq)
    player = threading.Thread(target=_midi_player, args=(seq.events, port))  # , daemon=True
    # start the playback
    player.start()
    if block:
        # wait until playback is complete before returning from function
        player.join()


def play_beat(port, tempo, key, instrument, octave=0):
    chord_gen = ChordGenerator(tempo, key, instrument, octave)
    rhythm_gen = RhythmGenerator(tempo, 4, chord_gen.chords, chord_gen.key)

    blank = Score(out=Seq())

    rhythm = copy.deepcopy(blank)
    rhythm.compose(rhythm_gen.generate_rhythm(rhythm))

    chords = copy.deepcopy(blank)
    chords.compose(chord_gen.generate_chords(chords))

    rhythm_and_chords = copy.deepcopy(rhythm)
    rhythm_and_chords.compose(chord_gen.generate_chords(rhythm_and_chords))

    chords_and_drums = copy.deepcopy(rhythm_and_chords)
    chords_and_drums.compose(rhythm_gen.generate_kick_pattern(chords_and_drums, bass=False))

    full_mix = copy.deepcopy(rhythm_and_chords)
    full_mix.compose(rhythm_gen.generate_kick_pattern(full_mix))

    prob1 = choose([0, 1], [1, 1])
    prob2 = choose([0, 1], [0.5, 1])

    play_midi(chords.out, port)
    play_midi(rhythm_and_chords.out, port)

    play_midi(full_mix.out, port)
    play_midi(full_mix.out, port)

    if next(prob1):
        play_midi(rhythm_and_chords.out, port)
    else:
        play_midi(chords_and_drums.out, port)

    play_midi(full_mix.out, port)
    play_midi(full_mix.out, port)

    if next(prob1):
        play_midi(rhythm_and_chords.out, port)
    else:
        play_midi(chords_and_drums.out, port)
    if next(prob2):
        play_midi(chords.out, port)


if __name__ == '__main__':
    midi_out = rtmidi.MidiOut()
    out_ports = midi_out.get_ports()
    print("midi out ports:", out_ports)

    midi_out.open_port(midi_out.get_ports().index('IAC Driver poly'))

    # Change the beat's tempo, key, and instrument
    play_beat(midi_out, 180, 'F', 'guitar', octave=0)
