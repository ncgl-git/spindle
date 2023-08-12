import unittest
from unittest import mock
from spindle.spool import Spool


class TestSpool(unittest.TestCase):
    def setUp(self) -> None:
        Spool._spools = {}
        Spool.reset_attributes()

    def tearDown(self) -> None:
        Spool._spools = {}
        Spool.reset_attributes()

    def test_spool_attribute_access(self):
        """Test that a Spool can access an attribute set to it."""
        class T0(Spool):
            key = "T0"

            def unwind(self, **kwargs):
                return list(self.items)

            def stitch(**kwargs):
                return

            def backstitch(**kwargs):
                return

        expected = [1, 2, 3, 4, 5]

        Spool.set_attributes(items=expected)

        self.assertEqual(expected, T0().unwind())

    def test_subclasses_register(self):
        """Test that subclasses register to the class attribute."""
        class T1(Spool):
            key = "T1"

            def unwind(**kwargs):
                return []

            def stitch(**kwargs):
                return

            def backstitch(**kwargs):
                return

        class T2(Spool):
            key = "T2"

            def unwind(**kwargs):
                return []

            def stitch(**kwargs):
                return

            def backstitch(**kwargs):
                return

        class T3(Spool):
            key = "T3"

            def unwind(**kwargs):
                return []

            def stitch(**kwargs):
                return

            def backstitch(**kwargs):
                return

        self.assertSetEqual({"T1", "T2", "T3"}, set(Spool._spools))
