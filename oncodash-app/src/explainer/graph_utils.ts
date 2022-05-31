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
 * Depth first travesing of the explainer graph given a node.
 * Finds all the paths/links down or up stream of a node.
 * @param {DAGNode} dagNode - Input DAG-node.
 * @param {string} [mode="forward"] - Direction to traverse the graph. One of "forward", "backward".
 * @returns {Map<Link, Node>} - Link-node pairs representing all the nodes/links in a path.
 */
export function traverseNodes(
    dagNode: DAGNode,
    mode = "forward"
): Map<Link, Node> {
    const nodelinks = new Map<Link, Node>();
    const key = mode === "forward" ? "children" : "parents";

    // HACK: Add the current node to the map with a placeholder link.
    // Otherwise the current node won't be added to the final map since it
    // is not contained in the dagNode children or parents.
    const placeholderLink = {
        source: "",
        target: "",
        certainty: 0,
        strength: 0,
    };
    nodelinks.set(placeholderLink, dagNode.node);

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

/**
 * Depth first travesing of the children links of the explainer graph.
 * Finds all the nodes/links down stream of a node and also the first parent.
 * @param {DAGNode} dagNode - Input DAG-node.
 * @param {string} source - The source node id of the currently active link.
 * @returns {Map<Link, Node>} - Link-node pairs representing all the nodes/links in a path.
 */
export function traverseLinks(
    dagNode: DAGNode,
    source: string
): Map<Link, Node> {
    const nodelinks = new Map<Link, Node>();

    // store the first matching parent node to the map.
    for (const parent of dagNode.parents) {
        if (parent.link.source === source) {
            nodelinks.set(parent.link, parent.dagnode.node);
        }
    }

    const traverse = (dagNode: DAGNode) => {
        for (const nextNode of dagNode["children"]) {
            if (!nodelinks.has(nextNode.link)) {
                nodelinks.set(nextNode.link, nextNode.dagnode.node);
                traverse(nextNode.dagnode);
            }
        }
    };

    traverse(dagNode);
    return nodelinks;
}
