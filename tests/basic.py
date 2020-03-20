from time import time
import os.path as op

import unittest


class FastWerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.hypo, self.ref = [], []
        with open(op.join('tests', 'data', 'ref.trn')) as f_r, open(op.join('tests', 'data', 'hypo.trn')) as f_h:
            for i, (h, r) in enumerate(zip(f_r, f_h)):
                self.hypo.append(h.strip().rsplit(' ', 1)[0])
                self.ref.append(r.strip().rsplit(' ', 1)[0])

    @classmethod
    def get_score_and_time(cls, hypo, ref, char_level: bool = False):
        import fastwer
        start_time = time()
        score = fastwer.score(hypo, ref, char_level=char_level)
        elapsed = time() - start_time
        return score, elapsed

    def test_wer_speed(self):
        _, elapsed = self.get_score_and_time(self.hypo, self.ref, char_level=False)
        self.assertLessEqual(elapsed, 0.5)
        print(f'{elapsed:.4f}s for WER')

    def test_cer_speed(self):
        _, elapsed = self.get_score_and_time(self.hypo, self.ref, char_level=True)
        self.assertLessEqual(elapsed, 2.0)
        print(f'{elapsed:.4f}s for CER')

    def test_wer_with_vizseq(self):
        from vizseq.scorers.wer import WERScorer
        first_n = 100
        hypo, ref = self.hypo[:first_n], self.ref[:first_n]
        score, _ = self.get_score_and_time(hypo, ref, False)
        vizseq_score = WERScorer().score(hypo, [ref]).corpus_score
        self.assertAlmostEqual(score, vizseq_score, places=2)
        print('Same WER with VizSeq')

    # def test_cer_with_vizseq(self):
    #     from vizseq.scorers.wer import WERScorer
    #     first_n = 100
    #     hypo, ref = self.hypo[:first_n], self.ref[:first_n]
    #     score, _ = self.get_score_and_time(hypo, ref, True)
    #     hypo_chars, ref_chars = [' '.join(list(hh)) for hh in hypo], [' '.join(list(rr)) for rr in ref]
    #     vizseq_score = WERScorer().score(hypo_chars, [ref_chars]).corpus_score
    #     self.assertAlmostEqual(score, vizseq_score, places=2)
    #     print('Same CER with VizSeq')
