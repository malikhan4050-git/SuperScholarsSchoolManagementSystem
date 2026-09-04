import unittest

import arabic_reshaper
from bidi.algorithm import get_display

from app.utils.challan_printer import normalize_urdu_text


class UrduRenderingTest(unittest.TestCase):
    def test_urdu_text_is_rtl_display_ready(self):
        sample = "براہ کرم مقررہ تاریخ سے پہلے فیس جمع کرائیں"
        expected = get_display(arabic_reshaper.reshape(sample))
        actual = normalize_urdu_text(sample)
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
