// Interfaces for the graph query data
export interface Node {
    id: string;
    group: string;
    order: number;
}

export interface Link {
    source: string;
    target: string;
    certainty: number;
    strength: number;
}

export interface NodeLink {
    id: number;
    patient: string;
    spec: {
        directed: boolean;
        multigraph: boolean;
        graph: Record<string, unknown>;
        nodes: Node[];
        links: Link[];
    };
}

// Interface for a DAG linked-list datastructure
export interface DAGLink {
    link: Link;
    dagnode: DAGNode;
}

export interface DAGNode {
    node: Node;
    children: DAGLink[];
    parents: DAGLink[];
}

/**
 * Convert node-link data into a mapping of doubly linked lists, all of
 * which can be traversed with depth first search.
 * @param {NodeLink} graphData - Input graph in node-link-format.
 * @returns {Map<string, DAGNode>} - A map of linkedlists for each node in the graph.
 */
export function nodeLinkToDAG(graphData: NodeLink): Map<string, DAGNode> {
    const dagMap = new Map<string, DAGNode>();
    for (const node of graphData.spec.nodes) {
        const dagNode = { node: node, children: [], parents: [] };
        dagMap.set(node.id, dagNode);
    }

    for (const link of graphData.spec.links) {
        const dagLinkChild: DAGLink = {
            link: link,
            dagnode: dagMap.get(link.target)!,
        };
        const dagLinkParent: DAGLink = {
            link: link,
            dagnode: dagMap.get(link.source)!,
        };

        const source = dagMap.get(link.source);
        const target = dagMap.get(link.target);
        source?.children.push(dagLinkChild);
        target?.parents.push(dagLinkParent);
    }

    return dagMap;
}

/**
 * Depth first travesing of the explainer graph given a DAGNode.
 * Finds all the paths/links down or up stream of a node or a link.
 * @param {DAGNode} dagNode - Input DAG-node.
 * @param {"link" | "node"} source - Flag, whether to start traversing the graph from a node or a link.
 * @param {"children" | "parents"} [mode="forward"] - Direction to traverse the graph.
 * @returns {Map<Link, Node>} - Link-node pairs representing all the nodes/links in a path.
 */
export function traverseNodes(
    dagNode: DAGNode,
    mode = "forward",
    source = "link",
    sourceId?: string
): Map<Link, Node> {
    const nodelinks = new Map<Link, Node>();
    const key = mode === "forward" ? "children" : "parents";

    if (source === "link") {
        // Only forward traversing when source === "link"
        // store the first matching parent node to the map.
        for (const parent of dagNode.parents) {
            if (parent.link.source === sourceId) {
                nodelinks.set(parent.link, parent.dagnode.node);
            }
        }
    } else if (source === "node") {
        // Add the current node to the map with a placeholder link.
        // Otherwise the current node won't be added to the final map since it
        // is not contained in the dagNode children or parents.
        const placeholderLink = {
            source: "",
            target: "",
            certainty: 0,
            strength: 0,
        };
        nodelinks.set(placeholderLink, dagNode.node);
    } else {
        throw new Error(
            `Illegal source argument. Got: ${source}. Allowed: "link", "node"`
        );
    }

    const traverse = (dagNode: DAGNode) => {
        for (const nextNode of dagNode[key]) {
            if (!nodelinks.has(nextNode.link)) {
                nodelinks.set(nextNode.link, nextNode.dagnode.node);
                traverse(nextNode.dagnode);
            }
        }
    };

    traverse(dagNode);
    return nodelinks;
}
