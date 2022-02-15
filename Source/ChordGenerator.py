from musx import markov, rhythm, Note, choose


class ChordGenerator:
    def __init__(self, tempo, key, instrument='guitar', octave=0):
        self.tempo = tempo
        self.octave = octave
        self.key = None
        self.set_key(key)
        self.chords = []
        self.init_chords()

        if instrument == 'guitar':
            self.inst = 4
        elif instrument == 'synth':
            self.inst = 5
        elif instrument == 'piano':
            self.inst = 6

    def set_key(self, key):
        key_dict = {
            'c': 0,
            'c#': 1,
            'db': 1,
            'd': 2,
            'd#': 3,
            'eb': 3,
            'e': 4,
            'f': 5,
            'f#': 6,
            'gb': 6,
            'g': 7,
            'g#': 8,
            'ab': 8,
            'a': 9,
            'a#': 10,
            'bb': 10,
            'b': 11
        }

        self.key = key_dict[key.lower()]
        print(self.key)

    def init_chords(self):
        rules = {-1: [[0, 1]],
                 0: [[0, .4], [3, 0], [5, .5], [8, .3], [10, .4]],
                 3: [[0, 0.2], [3, 0.1], [5, 0.6], [7, 0.1], [8, 0.2], [10, 0.7]],
                 5: [[0, 0.3], [3, 0], [5, 0.4], [7, 0.6], [8, 0.1], [10, 0.4]],
                 (7,): [[7, 1]],
                 8: [[0, 0.2], [3, 0], [5, 0.6], [7, 0.4], [8, 0.2], [10, 0.2]],
                 10: [[0, 0.5], [3, 0], [5, 0.4], [7, 0.1], [8, 0.4], [10, 0.3]]
                 }

        pat = markov(rules)
        for _ in range(4):
            self.chords.append(next(pat))

        print(self.chords)

    def generate_chords(self, score):
        chord_dict = {
            0: [0, 3, 7],
            3: [3, 7, 10],
            5: [5, 8, 12],
            7: [-5, -1, 2],
            8: [-4, 0, 3],
            10: [-2, 2, 5]
        }

        dur = rhythm(1, self.tempo, 0.25)

        for i in range(4):
            cur_chord = chord_dict[self.chords[i]]
            for j in range(3):
                if j < 2:
                    arp_len = 3
                else:
                    arp_len = 2
                for n in range(arp_len):
                    if n > 0:
                        amp = 0.4
                        prob = choose([0, 1], [1, 1 - (self.tempo - 80) / 100])
                    else:
                        amp = 0.6
                        prob = choose([0, 1], [1, 0])

                    note = Note(time=score.now + rhythm(0.125, self.tempo, 0.25) * (n + j * 3),
                                duration=rhythm(0.125, self.tempo, 0.25),
                                pitch=48 + self.key + cur_chord[n] + self.octave * 12, amplitude=amp, instrument=self.inst)
                    score.add(note)

                    if next(prob):
                        note = Note(time=score.now + rhythm(0.125, self.tempo, 0.25) * (n + j * 3) + rhythm(0.0625, self.tempo, 0.25),
                                    duration=rhythm(0.0625, self.tempo, 0.25),
                                    pitch=48 + self.key + cur_chord[n-1] + self.octave * 12, amplitude=0.05, instrument=self.inst)
                        score.add(note)

            yield dur



