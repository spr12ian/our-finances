from method_sorter import MethodSorter

file_path = "/home/probity/projects/download-our-finances/cls_test_class.py"
class_name = "Test_Class"

method_sorter = MethodSorter(file_path, class_name)
method_sorter.sort_methods_in_class()
