import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from dialogflow_payload_gen.exporter import Exporter

from do.base_datarow import DataRow


class ExporterDFS(Exporter):
    def __init__(self, config: dict) -> None:
        super().__init__(config)

    def get_dfs_data(self):
        root_intents = self.dialogflow.get_root_intents()

        data = {}
        for root in root_intents:
            children = self.dfs(root)
            data[root.intent_obj.display_name] = children

        return {k: data[k] for k in sorted(data.keys())}

    def gen_rows(self):

        dfs_data = self.get_dfs_data()

        dfs_data_flattened = []
        for intents in dfs_data.values():
            dfs_data_flattened.extend([x.display_name for x in intents])

        data = {k: self.data[k] for k in dfs_data_flattened}

        super().gen_rows(data=data)

    def dfs(self, root):
        stack = []
        visited = []

        stack.append(root)

        while len(stack) > 0:
            node = stack.pop()
            if node.children:
                stack.extend(node.children)

            visited.append(node)

        return visited


if __name__ == "__main__":

    title = "csv exporter dfs"
    version = "0.1.0"
    author = "Farhabi Helal"
    email = "farhabi.helal@jp.honda-ri.com"

    import argparse

    default_config = {
        "project_id": "",
        "credential": "",
        "export_directory": "",
        "export_filename": "",
    }

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--project_id",
        dest="project_id",
        type=str,
        default=default_config.get("project_id", ""),
        help="Google Cloud Project Id",
    )
    parser.add_argument(
        "--credential",
        dest="credential",
        type=str,
        default=default_config.get("credential", ""),
        help="Path to Google Cloud Project credential",
    )
    parser.add_argument(
        "--export_directory",
        dest="export_directory",
        type=str,
        default=default_config.get("export_directory", ""),
        help="Absolute path to export directory",
    )
    parser.add_argument(
        "--export_filename",
        dest="export_filename",
        type=str,
        default=default_config.get("export_filename", ""),
        help="Name of the exported file",
    )

    args, args_list = parser.parse_known_args()

    config = {
        "project_id": args.project_id,
        "credential": args.credential,
        "export_directory": args.export_directory,
        "export_filename": args.export_filename,
    }

    exporter = ExporterDFS(config)
    exporter.run()
