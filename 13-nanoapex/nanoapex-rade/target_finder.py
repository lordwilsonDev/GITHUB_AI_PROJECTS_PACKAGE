from tree_sitter import Language, Parser
import tree_sitter_python as tspython
import os
import datetime

TRIGGER_MARKER = "# @nanoapex"

def has_nanoapex_trigger(source_text: str) -> bool:
    return TRIGGER_MARKER in source_text

def save_snippet_to_memory(function_name, content, source_path=None):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"nano_memory/{function_name}_{ts}.nano"

    with open(filename, "w") as f:
        f.write(content)

    # Enhanced logging as requested in mission brief
    print(f"[RADE] snippet captured | function={function_name} | path={source_path or 'unknown'} | nano={filename}")

class TargetFinder:
    def __init__(self):
        self.language = Language(tspython.language())
        self.parser = Parser(self.language)

    def list_functions(self, filepath):
        with open(filepath, "rb") as f:
            code = f.read()

        tree = self.parser.parse(code)
        root = tree.root_node

        functions = []
        self._find_functions(root, code, functions)

        return functions

    def _find_functions(self, node, code, result):
        # Look for Python function definition nodes
        if node.type == "function_definition":
            name_node = node.child_by_field_name("name")
            name = code[name_node.start_byte:name_node.end_byte].decode()
            result.append(name)

        # Recurse children nodes
        for child in node.children:
            self._find_functions(child, code, result)

    def extract_function_body(self, filepath, function_name):
        with open(filepath, "rb") as f:
            code = f.read()

        tree = self.parser.parse(code)
        root = tree.root_node

        return self._extract_function_body(root, code, function_name)

    def _extract_function_body(self, node, code, target_name):
        if node.type == "function_definition":
            name_node = node.child_by_field_name("name")
            name = code[name_node.start_byte:name_node.end_byte].decode()
            if name == target_name:
                return code[node.start_byte:node.end_byte].decode()

        for child in node.children:
            result = self._extract_function_body(child, code, target_name)
            if result:
                return result

        return None


if __name__ == "__main__":
    tf = TargetFinder()

    fname = "playground_nanoapex.py"  # scratch file only

    funcs = tf.list_functions(fname)
    print("[Finder] Functions:", funcs)

    for func_name in funcs:
        body = tf.extract_function_body(fname, func_name)
        if not body:
            continue

        if has_nanoapex_trigger(body):
            print(f"[RADE] @nanoapex detected | function={func_name} | path={fname}")
            save_snippet_to_memory(func_name, body, fname)
        else:
            print(f"[Skip] {func_name} has no @nanoapex marker, ignoring.")
