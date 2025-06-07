from pathlib import Path

import libcst as cst


class MethodSorter:
    def __init__(self, file_path: Path, class_name: str):
        self.file_path = file_path
        self.class_name = class_name

        # Validate file path
        if not self.file_path.is_file():
            raise FileNotFoundError(f"File not found: {self.file_path}")

    def sort_methods_in_class(self) -> Any:
        """Sorts top-level methods in the specified class alphabetically."""
        # Read the source file
        try:
            with self.file_path.open("r") as source:
                code = source.read()
                module = cst.parse_module(code)
        except Exception as e:
            raise RuntimeError(f"Failed to parse the file: {e}")

        # Locate the target class
        class_finder = ClassFinder(self.class_name)
        module.visit(class_finder)

        if not class_finder.class_node:
            raise ValueError(f"Class '{self.class_name}' not found in {self.file_path}")

        # Collect and sort top-level methods
        method_collector = MethodCollector()
        class_finder.class_node.visit(method_collector)

        if not method_collector.methods:
            print(f"No methods found in class '{self.class_name}'. No changes made.")
            return

        sorted_methods = sorted(method_collector.methods, key=lambda x: x.name.value)

        # Replace the existing methods with sorted ones, preserving other class body items
        new_class_body = [
            node
            for node in class_finder.class_node.body.body
            if not isinstance(node, cst.FunctionDef)
        ] + sorted_methods

        # Create a new class node with the sorted methods
        new_class_node = class_finder.class_node.with_changes(
            body=cst.IndentedBlock(body=new_class_body)
        )

        # Replace the old class node with the new one in the module
        transformer = ClassTransformer(self.class_name, new_class_node)
        modified_module = module.visit(transformer)

        # Write the modified code back to the file
        try:
            with self.file_path.open("w") as source:
                source.write(modified_module.code)
            print(f"Methods in class '{self.class_name}' sorted successfully.")
        except Exception as e:
            raise RuntimeError(f"Failed to write the sorted class to the file: {e}")


class ClassFinder(cst.CSTVisitor):
    def __init__(self, class_name):
        self.class_name = class_name
        self.class_node = None

    def visit_ClassDef(self, node):
        if node.name.value == self.class_name:
            self.class_node = node


class MethodCollector(cst.CSTVisitor):
    def __init__(self) -> None:
        self.methods = []

    def visit_FunctionDef(self, node):
        self.methods.append(node)


class ClassTransformer(cst.CSTTransformer):
    def __init__(self, class_name, new_class_node):
        self.class_name = class_name
        self.new_class_node = new_class_node

    def leave_ClassDef(self, original_node, updated_node):
        if original_node.name.value == self.class_name:
            return self.new_class_node
        return updated_node
