import unittest
from ExergoEconomicAnalysisClasses.MainModules.main_module import Block, Connection, ArrayHandler


class BlockTestCases(unittest.TestCase):

    def testStr(self):

        array_handler = ArrayHandler()

        a = Block(1, array_handler)
        a.name = "prova"
        b = Block(2, array_handler)
        b.modify_ID(1)

        self.assertEqual(False, str(a) == str(b))

        b.name = "prova"

        self.assertEqual(True, str(a) == str(b))

    def testAdd(self):

        array_handler = ArrayHandler()

        a = Block(1, array_handler)
        conn1 = Connection(1)
        conn2 = Connection(2)

        a.add_connection(conn1, is_input=True)
        a.add_connection(conn2, is_input=False)

        b = Block(2, array_handler)
        b.add_connection(conn2, is_input=True)
        self.assertEqual(2, conn2.toID)

        b.modify_ID(3)
        self.assertEqual(3, conn2.toID)

    def testRemove(self):

        array_handler = ArrayHandler()

        a = Block(1, array_handler)
        conn1 = Connection(1)
        conn2 = Connection(2)

        a.add_connection(conn1, is_input=True)
        a.add_connection(conn2, is_input=False)

        b = Block(2, array_handler)
        b.add_connection(conn2, is_input=True)
        self.assertEqual(False, conn2.is_loss)

        b.remove_connection(conn2)
        self.assertEqual(-1, conn2.toID)
        self.assertEqual(True, conn2.is_loss)

    def testCheckCondition(self):
        class TestSubClass(Block):

            def __init__(self, inputID, main_class):
                super().__init__(inputID, main_class)

        def test_function(obj):

            try:
                obj.is_ready_for_calculation

            except:
                return False

            return True

        array_handler = ArrayHandler()
        a = Block(1, array_handler)
        b = TestSubClass(2, array_handler)

        self.assertTrue(test_function(a))
        self.assertFalse(test_function(b))

    def testListOrder(self):

        array_handler = ArrayHandler()

        block0 = Block(0, array_handler, is_support_block=True)
        block1 = Block(1, array_handler)
        block2 = Block(2, array_handler)

        block_list = list()
        block_list.append(block1)
        block_list.append(block0)
        block_list.append(block2)

        block_list.sort()
        print(block_list)

        self.assertTrue(block1 < block2)
        self.assertTrue(block0 > block2)
        self.assertTrue(block_list[-1] == block0)


if __name__ == '__main__':
    unittest.main()
