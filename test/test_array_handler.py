import unittest
from src.MainModules.main_module import ArrayHandler, Connection


def generate_test_array_handler():
    array_handler = ArrayHandler()

    array_handler.append_block("Generic")
    array_handler.append_block("Generic")
    array_handler.append_block("Generic")
    array_handler.append_block("Generic")

    new_connection = array_handler.append_connection(to_block=array_handler.block_list[0])
    new_connection.exergy_value = 400.0
    new_connection.set_cost(10.0)

    new_connection = array_handler.append_connection(to_block=array_handler.block_list[2])
    new_connection.exergy_value = 700.0
    new_connection.set_cost(7.5)

    new_connection = array_handler.append_connection(from_block=0, to_block=1)
    new_connection.exergy_value = 300.

    new_connection = array_handler.append_connection(from_block=2, to_block=1)
    new_connection.exergy_value = 300.

    new_connection = array_handler.append_connection(from_block=1)
    new_connection.exergy_value = 100.

    new_connection = array_handler.append_connection(from_block=1, to_block=3)
    new_connection.exergy_value = 200.

    new_connection = array_handler.append_connection(from_block=3)
    new_connection.exergy_value = 150.
    new_connection.is_useful_effect = True

    return array_handler


class MyTestCase(unittest.TestCase):

    def testDynamicImport(self):
        def import_and_check_name(name, block_arr):
            block_arr.append_block(name)
            return name == type(block_arr.block_list[-1]).__name__

        array_handler = ArrayHandler()

        self.assertTrue(import_and_check_name("Expander", array_handler))
        self.assertFalse(import_and_check_name("NotABlock", array_handler))

        print(array_handler)

    def testCalculation(self):
        array_handler = generate_test_array_handler()

        print(array_handler)
        array_handler.calculate()

        self.assertAlmostEqual(61.667, array_handler.block_list[-1].output_connections[0].rel_cost, delta=2)


if __name__ == '__main__':
    unittest.main()
