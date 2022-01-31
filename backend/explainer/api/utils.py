import pandas as pd
import networkx as nx
from pathlib import Path
from typing import Dict, Union, Callable
from typing_extensions import TypedDict


class IndTab2Json:
    def __init__(
        self,
        path: Union[Path, str],
        separator: str = ",",
        index_key: str = "indicationindex",
        group_key: str = "Patient",
        certainty_key: str = "certainty",
        format: str = "nodelink",
        df_transform: Callable = None,
    ) -> None:
        """
        Helper class to convert the input indication table into JSON.

        Example of the indication table format:

        | idx | Patient | Sample | Gene  | Mutation | Indication | Certainty |
        |-----|---------|--------|-------|----------|------------|-----------|
        | 0   | P1      | P1_s1  | BRCA1 | p.GGX    | Drug1      | 2         |
        | 1   | P1      | P1_s2  | BRCA2 | p.TTX    | Drug2      | 1         |
        | 2   | P2      | P2_s1  | RAD51 | p.FFX    | Drug1      | 1         |
        | 3   | P2      | P2_s2  | BRCA1 | p.GGX    | Drug1      | 2         |
        | 4   | P2      | P2_s3  | CHEK2 | p.DDX    | Drug3      | 3         |
        | 5   | P3      | P3_s3  | BRCA1 | p.RRX    | Drug1      | 2         |

        Args:
        ---------
            path (Path, str):
                Path to the indication table
            separator (str, default=","):
                The value separator of the indication csv file.
            index_key (str, default="indicationindex"):
                The column name for the indication index.
            group_key (str, default="Patient"):
                The column of the dataframe that will be used to
                group the JSON at the top-level.
            certinty_key (str, default="certainty"):
                The column of the dataframe that contains the certainty
                values
            format (str, default="nodelink"):
                The json format the table is converted into.
                One of: ("nodelink", "cytoscape").
            df_transform (Callable):
                A function applied to the indication table. If some
                wrangling is needed for the table before converting to
                JSON.
        """
        if format not in ("nodelink", "cytoscape"):
            raise ValueError(
                f"""
                Invalid value for argument `format`. Got: {format}.
                Allowed: {("nodelink", "cytoscape")}."""
            )

        self.path = Path(path)
        self.format = format
        self.group_key = group_key
        self.index_key = index_key
        self.certainty_key = certainty_key
        self.separator = separator

        self.indf = pd.read_csv(self.path, sep=self.separator, index_col=self.index_key)

        if df_transform is not None:
            self.indf = df_transform(self.indf)

    @property
    def network_spec(self) -> Dict[str, TypedDict]:
        """
        Get the JSON network specifications for all the groups in the
        indication table.
        """
        if self.format == "cytoscape":
            graphs = self._table2cytoscape()
        elif self.format == "nodelink":
            graphs = self._table2nodelinks()

        return graphs

    def _table2graphs(self) -> Dict[str, nx.DiGraph]:
        """
        Convert the indication table into networkx directed graphs
        """
        graphs = {}
        node_cols = [
            col
            for col in self.indf.columns
            if col not in (self.group_key, self.certainty_key)
        ]

        for n, p in self.indf.groupby(self.group_key):

            sub_graphs = []
            for _, row in p.iterrows():
                g = nx.path_graph(row[node_cols].values, create_using=nx.DiGraph)

                # set node attrs
                node_attrs = {
                    v: {"group": k, "order": i}
                    for i, (k, v) in enumerate(row.iteritems())
                }
                nx.set_node_attributes(g, node_attrs)

                # set edge attrs
                edge_attrs = {
                    e: {
                        "certainty": 1.0 / row[self.certainty_key],
                        "strength": row[self.certainty_key],
                    }
                    for e in g.edges
                }
                nx.set_edge_attributes(g, edge_attrs)

                sub_graphs.append(g)

            G = nx.compose_all(sub_graphs)
            graphs[n] = G

        return graphs

    def _table2nodelinks(self) -> Dict[str, TypedDict]:
        """
        Convert the input table into node link format that is
        serializable to JSON and usable in Javascript documents.
        """
        graphs = self._table2graphs()

        for n, g in graphs.items():
            graphs[n] = nx.node_link_data(g)

        return graphs

    def _table2cytoscape(self) -> Dict[str, TypedDict]:
        """
        Convert the input table into Cytoscape JSON format that is
        serializable to JSON and usable in Cytoscape.js applications.
        """
        graphs = self._table2graphs()

        for n, g in graphs.items():
            graphs[n] = nx.cytoscape_data(g)

        return graphs


def split_samplestr(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ad hoc split of the 'Sample' column into 'Tissue' and 'Timepoint'
    columns.
    """
    df[["P", "Sample"]] = df["Sample"].str.split("_", n=1, expand=True)
    df = df.drop(columns=["P"])

    return df
