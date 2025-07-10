from method_sorter import MethodSorter


def main():
    directory = "/home/probity/projects/download-our-finances/"
    classes = [
        ["cls_helper_config", "Config"],
        ["cls_helper_date_time", "DateTimeHelper"],
        ["cls_helper_google", "GoogleHelper"],
        ["cls_helper_log", "LogHelper"],
        ["sqlalchemy_helper", "SQLAlchemyHelper"],
        ["cls_hmrc", "HMRC"],
        ["cls_hmrc_calculation", "HMRC_Calculation"],
        ["cls_method_sorter", "ClassFinder"],
        ["cls_method_sorter", "ClassTransformer"],
        ["cls_method_sorter", "MethodCollector"],
        ["cls_method_sorter", "MethodSorter"],
        ["cls_table_hmrc_constants_by_year", "HMRC_ConstantsByYear"],
        ["cls_table_hmrc_overrides_by_year", "HMRC_OverridesByYear"],
        ["cls_table_hmrc_people_details", "HMRCPeopleDetails"],
    ]

    sort_classes(directory, classes)


def sort_classes(directory, classes):
    for basename, class_name in classes:
        sort_class_methods_in_file(directory, basename, class_name)


def sort_class_methods_in_file(directory, basename, class_name):
    file_path = directory + basename + ".py"

    method_sorter = MethodSorter(file_path, class_name)
    method_sorter.sort_methods_in_class()


if __name__ == "__main__":
    main()
