from time import time
import os.path as op
import os
import re
import subprocess
import tempfile
import unicodedata
import warnings
import unittest
from typing import Optional


class TruncatedDataFilePath(object):
    SPACE = chr(32)
    SPACE_ESCAPE = chr(9601)

    def __init__(self, path: str, percentage: int = 100, use_chars=False):
        self._path = path
        self.path = None
        self.percentage = percentage
        self.use_chars = use_chars

    def __enter__(self):
        with open(self._path) as f:
            data = [r for r in f]
        _percentage = max(1, min(self.percentage, 100))
        if _percentage < 100:
            _size = max(1, int(len(data) * _percentage / 100))
            data = data[:_size]
        if self.use_chars:
            def process_line(line):
                sent, utterance_id = line.strip().rsplit(self.SPACE, 1)
                sent = sent.replace(self.SPACE, self.SPACE_ESCAPE)
                sent = self.SPACE.join(list(sent))
                return f'{sent}{self.SPACE}{utterance_id}\n'
            data = [process_line(s) for s in data]

        with tempfile.NamedTemporaryFile(
                mode='w', encoding='utf-8', delete=False) as f:
            for r in data:
                f.write(r)
            self.path = f.name
        return self.path

    def __exit__(self, exc_type, exc_value, exc_traceback):
        os.remove(self.path)


class FastWerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        warnings.filterwarnings("ignore")

        self.hypo_path = op.join('tests', 'data', 'hypo.trn')
        self.ref_path = op.join('tests', 'data', 'ref.trn')

    @classmethod
    def get_hypo_ref(cls, hypo_path: str, ref_path: str):
        hypo, ref = [], []
        with open(hypo_path) as f_h, open(ref_path) as f_r:
            for h, r in zip(f_h, f_r):
                hypo.append(h.strip().rsplit(' ', 1)[0])
                ref.append(r.strip().rsplit(' ', 1)[0])
        return hypo, ref

    @classmethod
    def get_score_and_time(cls, hypo_path: str, ref_path: str, char_level: bool = False):
        import fastwer
        hypo, ref = cls.get_hypo_ref(hypo_path, ref_path)
        start_time = time()
        wer = round(fastwer.score(hypo, ref, char_level=char_level), 1)
        elapsed = time() - start_time
        return wer, elapsed

    def test_wer_speed(self):
        _, elapsed = self.get_score_and_time(self.hypo_path, self.ref_path, char_level=False)
        self.assertLessEqual(elapsed, 0.5)
        print(f'{elapsed:.4f}s for WER')

    def test_cer_speed(self):
        _, elapsed = self.get_score_and_time(self.hypo_path, self.ref_path, char_level=True)
        self.assertLessEqual(elapsed, 2.0)
        print(f'{elapsed:.4f}s for CER')

    def test_unicode_cer(self):
        import fastwer

        # Canonically equivalent, but 4 and 5 code points respectively.
        nfc = unicodedata.normalize('NFC', 'café')
        nfd = unicodedata.normalize('NFD', 'café')
        self.assertEqual((len(nfc), len(nfd)), (4, 5))

        cases = [
            ('é', 'e', 100.0),
            ('你', '好', 100.0),
            ('a😀', 'a😃', 50.0),
            ('你好', '你', 100.0),
            (nfc, nfc, 0.0),
            # Normalization is the caller's responsibility, so the two forms
            # do not compare as equal.
            (nfd, nfc, 50.0),
            (nfc, nfd, 40.0),
        ]
        for hypo, ref, expected in cases:
            with self.subTest(hypo=hypo, ref=ref):
                self.assertEqual(
                    fastwer.score_sent(hypo, ref, char_level=True),
                    expected,
                )

        self.assertEqual(
            fastwer.score(['你', 'ab'], ['好', 'ac'], char_level=True),
            66.6667,
        )

    def test_invalid_utf8(self):
        import fastwer

        # pybind11 converts str to UTF-8 before the C++ sees it, so malformed
        # input can only arrive as bytes.
        cases = [
            b'\x80',              # continuation byte as lead
            b'\xff',              # invalid lead byte
            b'\xc3',              # truncated 2-byte sequence
            b'\xe4\xbd',          # truncated 3-byte sequence
            b'\xe4\x20\xa0',      # invalid continuation byte
            b'\xc0\xaf',          # overlong encoding of '/'
            b'\xe0\x80\xaf',      # overlong 3-byte encoding
            b'\xf0\x80\x80\xaf',  # overlong 4-byte encoding
            b'\xed\xa0\x80',      # UTF-16 surrogate code point
            b'\xf4\x90\x80\x80',  # beyond U+10FFFF
        ]
        for bad in cases:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    fastwer.score_sent(bad, 'a', char_level=True)
                with self.assertRaises(ValueError):
                    fastwer.score_sent('a', bad, char_level=True)

        # Well-formed bytes are tokenized by code point, same as str.
        self.assertEqual(
            fastwer.score_sent('你好'.encode(), '你', char_level=True),
            100.0,
        )

    def test_wer_cer_with_sclite(self):
        def get_sclite_wer(h_path: str, r_path: str) -> Optional[float]:
            whitespace_normalizer, space = re.compile(r'\s+'), chr(32)
            bin_path = os.environ.get('SCLITE_PATH', None)
            score = None
            if bin_path is not None and op.isfile(bin_path):
                cmd = f'{bin_path} -h {h_path} -r {r_path} -i rm'
                process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                for line in process.stdout.readlines():
                    s = line.decode('utf-8').strip()
                    if s.find('Sum/Avg') > -1:
                        s = whitespace_normalizer.sub(space, s)
                        score = float(s.split(space)[-3])
            else:
                print('Cannot locate sclite')
            return score

        for pct in [5, 10, 20, 25, 50]:
            with TruncatedDataFilePath(self.hypo_path, percentage=pct) as hypo_path, \
                    TruncatedDataFilePath(self.ref_path, percentage=pct) as ref_path, \
                    TruncatedDataFilePath(self.hypo_path, percentage=pct, use_chars=True) as hypo_chars_path, \
                    TruncatedDataFilePath(self.ref_path, percentage=pct, use_chars=True) as ref_chars_path:
                # WER
                delta = 0.1 + 1e-6
                sclite_wer = get_sclite_wer(hypo_path, ref_path)
                if sclite_wer is not None:
                    wer, _ = self.get_score_and_time(hypo_path, ref_path)
                    self.assertAlmostEqual(wer, sclite_wer, delta=delta)
                    print(f'FastWER/sclite WER delta <= {delta} ({wer} / {sclite_wer})')
                # CER
                sclite_cer = get_sclite_wer(hypo_chars_path, ref_chars_path)
                if sclite_cer is not None:
                    cer, _ = self.get_score_and_time(hypo_path, ref_path, char_level=True)
                    self.assertAlmostEqual(cer, sclite_cer, delta=delta)
                    print(f'FastWER/sclite CER delta <= {delta} ({cer} / {sclite_cer})')

    # def test_wer_with_vizseq(self):
    #     from vizseq.scorers.wer import WERScorer
    #     for pct in [1, 2, 5]:
    #         with TruncatedDataFilePath(self.hypo_path, percentage=pct) as hypo_path, \
    #                 TruncatedDataFilePath(self.ref_path, percentage=pct) as ref_path:
    #             wer, _ = self.get_score_and_time(hypo_path, ref_path, False)
    #             hypo, ref = self.get_hypo_ref(hypo_path, ref_path)
    #             vizseq_wer = WERScorer().score(hypo, [ref]).corpus_score
    #             self.assertAlmostEqual(wer, vizseq_wer, delta=0.1)
    #             print(f'FastWER - VizSeq: {wer} - {vizseq_wer}')
    #     print('Same WER with VizSeq')


if __name__ == '__main__':
    testcase = FastWerTestCase()
    testcase.setUp()
    testcase.test_wer_cer_with_sclite()
