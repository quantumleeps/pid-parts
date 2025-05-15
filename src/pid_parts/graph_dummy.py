# src/pid_parts/graph_dummy.py
from langgraph.graph import Graph


def build_dummy_graph():
    g = Graph()

    # placeholder node that does nothing
    def pass_through(state):  # noqa: remove later
        return state

    g.add_node("Start", pass_through)
    g.set_entry_point("Start")

    return g


if __name__ == "__main__":
    print("Building dummy graph…")
    graph = build_dummy_graph()
    print("Nodes:", graph.nodes)
