from tree_sitter import Language, Parser,Query, QueryCursor
import tree_sitter_python as tspython

# Initialize the Tree-sitter parser for Python
PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

def parse_python_code(source_code):
    """Parse Python source code into a syntax tree."""
    return parser.parse(source_code)

def build_call_graph(tree, source_code):
    """Build a call graph from the syntax tree."""
    call_graph = {}

    # Define a query to capture function definitions and calls
    query = Query(
        PY_LANGUAGE,
        """
    (function_definition
    name: (identifier) @function.def
    body: (block) @function.block)

    (call
    function: (identifier) @function.call
    arguments: (argument_list) @function.args)
    """,
    )

    # Get all captures from the query
    captures = QueryCursor(query).captures(tree.root_node)
    print(captures)
    # Track function definitions
    # function_defs = set()
    # for node, capture_name in captures:
    #     if capture_name == "function.def":
    #         func_name = source_code[node.start_byte:node.end_byte].decode("utf8")
    #         function_defs.add(func_name)
    #         if func_name not in call_graph:
    #             call_graph[func_name] = []

    # # Build the call graph
    # current_function = None
    # cursor = tree.walk()

    # def traverse(node):
    #     nonlocal current_function
    #     # Check if this is a function definition
    #     if node.type == "function_definition":
    #         name_node = node.child_by_field_name("name")
    #         if name_node:
    #             current_function = source_code[name_node.start_byte:name_node.end_byte].decode("utf8")

    #     # Check if this is a call node
    #     if node.type == "call":
    #         func_node = node.child_by_field_name("function")
    #         if func_node and func_node.type == "identifier":
    #             called_func = source_code[func_node.start_byte:func_node.end_byte].decode("utf8")
    #             if current_function and called_func in function_defs:
    #                 call_graph[current_function].append(called_func)

    #     # Traverse children
    #     for child in node.children:
    #         traverse(child)

    #     # Reset current_function when exiting a function definition
    #     if node.type == "function_definition":
    #         current_function = None

    # traverse(tree.root_node)
    block_to_func = {}
    for func_node in captures['function.def']:
        # Find the corresponding block
        for block_node in captures['function.block']:
            # The function definition's block starts at the same line
            if block_node.start_point[0] == func_node.start_point[0] + 1:
                block_to_func[block_node] = func_node.text.decode('utf-8')
                break

    # Build the call graph
    for call_node in captures['function.call']:
        caller = None
        # Find the function block that contains the call
        for block_node, func_name in block_to_func.items():
            if block_node.start_point <= call_node.start_point and block_node.end_point >= call_node.end_point:
                caller = func_name
                break
        
        callee = call_node.text.decode('utf-8')
        if caller and caller != callee:
            if caller not in call_graph:
                call_graph[caller] = []
            if callee not in call_graph[caller]:
                call_graph[caller].append(callee)
    return call_graph

def main():
    # Example Python code
    with open('treesitter_code_analyzer/src/code_analyzer/parser.py', 'rb') as f:
            code = f.read()

    # Parse the code and build the call graph
    tree = parse_python_code(code)
    call_graph = build_call_graph(tree, code)

    # Print the call graph
    print("Call Graph:")
    for caller, callees in call_graph.items():
        print(f"{caller} calls:")
        for callee in callees:
            print(f"  - {callee}")

if __name__ == "__main__":
    main()