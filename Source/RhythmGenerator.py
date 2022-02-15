from musx import Note, choose, rhythm


class RhythmGenerator:

    def __init__(self, tempo, pattern_len, chords, key):
        self.key = key
        self.chords = chords
        self.tempo = tempo
        self.pattern_len = pattern_len

    def hihats(self, score):
        choose_rhy = choose([0.25, 0.5], [1.2 - (self.tempo - 60) / 100, 1])

        for i in range(self.pattern_len * 8):
            rhy = next(choose_rhy)
            for j in range(int(1 / rhy / 2)):
                note = Note(time=score.now + rhythm((j * 0.0625), self.tempo, 0.25),
                            duration=rhythm(rhy / 4, self.tempo, 0.25), pitch=39, amplitude=1, instrument=1)
                score.add(note)
            yield rhythm(0.125, self.tempo, 0.25)

    def groove_baby(self, score, prob, timing):
        if next(prob):
            note = Note(time=timing, duration=0.125, pitch=40, instrument=1)
            score.add(note)

    def aux_snare(self, score):
        prob1 = choose([0, 1], [0.8, 1.4])
        prob2 = choose([0, 1], [1, 1])

        for i in range(int(self.pattern_len / 2)):
            timing = score.now + rhythm(0.25 + i * 2, self.tempo, 0.25)
            self.groove_baby(score, prob2, timing)

            timing = score.now + rhythm(0.625 + i * 2, self.tempo, 0.25)
            self.groove_baby(score, prob1, timing)

            timing = score.now + rhythm(0.875 + i * 2, self.tempo, 0.25)
            self.groove_baby(score, prob1, timing)

            timing = score.now + rhythm(1.375 + i * 2, self.tempo, 0.25)
            self.groove_baby(score, prob2, timing)

            timing = score.now + rhythm(1.75 + i * 2, self.tempo, 0.25)
            self.groove_baby(score, prob2, timing)

        yield self.pattern_len

    def snare(self, score):
        rhy = rhythm(0.5, self.tempo, 0.25)
        for i in range(self.pattern_len):
            note = Note(time=score.now + rhy, duration=rhy, pitch=38, instrument=1)
            score.add(note)
            yield rhythm(1, self.tempo, 0.25)

    def add_kick_and_bass_note(self, score, prob, timing, dur, chord, bass):
        if next(prob) == 1:
            note = Note(time=timing, duration=dur, pitch=36, instrument=1)
            score.add(note)

            if bass:
                bass_pitch = 60 + self.key + chord
                note = Note(time=timing, duration=dur, pitch=bass_pitch, instrument=8)
                score.add(note)

    def kick(self, score, bass):
        probability1 = choose([0, 1], [0.2, 1])
        probability2 = choose([0, 1], [0.2, 1])
        probability3 = choose([0, 1], [0.6, 1])
        dur = rhythm(0.125, self.tempo, 0.25)

        for j in range(int(self.pattern_len / 2)):
            self.add_kick_and_bass_note(score, probability1, score.now, dur, self.chords[0 + j * 2], bass)

            timing = score.now + rhythm(1.25, self.tempo, 0.25)
            self.add_kick_and_bass_note(score, probability2, timing, dur, self.chords[1 + j * 2], bass)

            timing = score.now + rhythm(0.75, self.tempo, 0.25)
            self.add_kick_and_bass_note(score, probability3, timing, dur, self.chords[0 + j * 2], bass)

            timing = score.now + rhythm(0.375, self.tempo, 0.25)
            self.add_kick_and_bass_note(score, probability3, timing, dur, self.chords[0 + j * 2], bass)

            timing = score.now + rhythm(1.875, self.tempo, 0.25)
            self.add_kick_and_bass_note(score, probability3, timing, dur, self.chords[1 + j * 2], bass)

            yield rhythm(int(self.pattern_len / 2), self.tempo, 0.25)

    def generate_rhythm(self, score):
        score.compose(self.hihats(score))
        score.compose(self.snare(score))
        score.compose(self.aux_snare(score))
        yield rhythm(self.pattern_len, self.tempo, 0.25)

    def generate_kick_pattern(self, score, bass=True):
        score.compose(self.kick(score, bass))
        yield rhythm(self.pattern_len, self.tempo, 0.25)

