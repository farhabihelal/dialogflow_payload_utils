import os

from dialogflow_payload_gen.csv_exporter import CSVExporter

if __name__ == "__main__":
    title = "csv exporter"
    version = "0.1.0"
    author = "Farhabi Helal"
    email = "farhabi.helal@jp.honda-ri.com"

    import argparse

    default_config = {
        "project_id": "",
        "credential": "",
        "export_directory": "",
        "export_filename": "",
        "algorithm": "",
        "mode": "text",
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
    #     "mode": "text",
    # }

    root_dir = os.path.abspath(f"{os.path.dirname(__file__)}/..")
    agents_dir = os.path.abspath(os.path.join(root_dir, ".temp/keys"))
    exports_dir = os.path.abspath(os.path.join(root_dir, "exports"))

    config = {
        "project_id": "hospital-surveyor-agent-hwdb",
        "credential": os.path.abspath(os.path.join(agents_dir, "hsa.json")),
        "export_directory": exports_dir,
        "export_filename": "hsa.tsv",
        "algorithm": "dfs",
        "mode": "survey_questions",
    }

    exporter = CSVExporter(config)
    exporter.run()