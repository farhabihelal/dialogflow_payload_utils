import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}/../../src"))

from dialogflow_payload_gen.exporter_xl_with_parent import ExporterXLWithParent


class ESExporterWithParent(ExporterXLWithParent):
    def __init__(self, config: dict) -> None:
        super().__init__(config)

    def get_sheets(self, rows: list):
        sheets = super().get_sheets(rows)
        return self.get_demo_sheets(sheets)

    def get_demo_sheets(self, sheets=None):
        session_data = self._config["session_data"]

        demo_sheets = {}

        for day in session_data:
            for session in session_data[day]:
                sheet_name = f"day-{day}-session-{session}"
                if not demo_sheets.get(sheet_name):
                    demo_sheets[sheet_name] = []

                for intent_name in session_data[day][session]:
                    intents = sheets[self.process_sheet_name(intent_name)]
                    demo_sheets[sheet_name].extend(intents)

        return demo_sheets


if __name__ == "__main__":
    title = "es exporter"
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

    # config = {
    #     "project_id": args.project_id,
    #     "credential": args.credential,
    #     "export_directory": args.export_directory,
    #     "export_filename": args.export_filename,
    #     "algorithm": "dfs",
    # }

    root_dir = os.path.abspath(f"{os.path.dirname(__file__)}/../../")
    agents_dir = os.path.abspath(os.path.join(root_dir, ".temp/keys"))
    exports_dir = os.path.abspath(os.path.join(root_dir, "exports"))

    from es_data import session_data

    # agent_filename = "es.json"
    # agent_filename = "es2.json"
    # agent_filename = "child-in-hospital.json"
    # agent_filename = "child-in-hospital-2.json"
    # agent_filename = "system-intents.json"
    agent_filename = "haru-test.json"
    agent_name = os.path.splitext(agent_filename)[0]

    config = {
        "credential": os.path.abspath(os.path.join(agents_dir, agent_filename)),
        "export_directory": exports_dir,
        "export_filename": "es_day_2_es_export.xlsx",
        "algorithm": "dfs",
        "mode": "text_rr",
        # "session_data": session_data[agent_name],
        "session_data": session_data["es"],
        "language_code": "es",
    }

    exporter = ESExporterWithParent(config)
    exporter.run()
