import libcst as cst
from pathlib import Path
from typing import List


class StubGenerator(cst.CSTVisitor):
    def __init__(self, class_name: str) -> None:
        self.stubs: List[str] = []
        self.class_name = class_name

    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        class_name = self.class_name
        if node.name.value == class_name:
            self.stubs.append(f"class {node.name.value}:")
            for item in node.body.body:
                if isinstance(item, cst.FunctionDef):
                    func_name = item.name.value
                    params = ", ".join(
                        (
                            f"{param.name.value}: {param.annotation.annotation.value}"
                            if param.annotation
                            else param.name.value
                        )
                        for param in item.params.params
                    )
                    return_type = (
                        item.returns.annotation.value if item.returns else "None"
                    )
                    self.stubs.append(
                        f"    def {func_name}({params}) -> {return_type}: ..."
                    )


def generate_stubs(class_name: str, file_path: str, output_path: str) -> None:
    with open(file_path, "r") as source:
        code = source.read()
        module = cst.parse_module(code)
        generator = StubGenerator(class_name)
        module.visit(generator)

    with open(output_path, "w") as output:
        output.write("\n".join(generator.stubs))


project_directory = "/home/probity/projects/download-our-finances"
stubs_sources = {
    "HMRC": "cls_hmrc",
    # "HMRC_Calculation": "cls_hmrc_calculation",
    # "LogHelper": "cls_helper_log",
}

for class_name, source in stubs_sources.items():
    source_file = f"{project_directory}/{source}.py"
    output_file = f"{project_directory}/stubs/{source}.pyi"
    generate_stubs(class_name, source_file, output_file)
