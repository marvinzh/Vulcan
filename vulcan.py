import argparse
import os
import logging
from typing import List

import uvicorn
from fastapi import FastAPI, Request

from reader.ReaderFactory import get_reader
from reader.DataReader import DataReader
from workflow import Workflow, WorkflowInstance
from endpoints import Endpoint

logging.basicConfig(
    format="%(asctime)s - %(filename)s[%(lineno)d] - %(levelname)s - %(message)s",
    level=logging.INFO,
)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--configs", nargs="*", type=str, default="")
    parser.add_argument("--config_type", type=str, choices=["yaml"], default="yaml")
    return parser.parse_args()


def read_configs(configs: str, config_type: str) -> List:
    if not configs:
        # todo(zbairong) get all config file recursively
        files = list(filter(lambda x: x.endswith("yml"), os.listdir("workflows")))
        configs = [os.path.join("workflows", file) for file in files]

    logging.info(f"found workflow configs: {configs}")
    reader = get_reader(config_type)
    readers = []
    for config in configs:
        config_reader = reader(config)
        readers.append(config_reader)

    return readers


def create_workflow_instance(config: DataReader):
    workflow_config = config.get_workflow()
    workflow = Workflow(workflow_config, config.get_workflow_id())
    workflow_instance = workflow.build()
    return workflow_instance


def create_endpoints(
    app: FastAPI, wfi_list: List[WorkflowInstance], config_list: List[DataReader]
):
    assert len(wfi_list) == len(config_list)
    for config, wfi in zip(config_list, wfi_list):
        endpoint_configs = config.get_endpoints()
        for endpoint_config in endpoint_configs:
            logging.info(f"bind endpoint {endpoint_config.get("path")} to workflow {wfi.workflow.id}")
            endpoint = Endpoint.create(endpoint_config, wfi)
            endpoint.bind(app)
            


def main(args):
    configs = read_configs(args.configs, args.config_type)
    wfi_list = []
    for config in configs:
        logging.info(f"create workflow instance for {config}")
        try:
            wfi = create_workflow_instance(config)
            wfi_list.append(wfi)
        except Exception:
            logging.error(f"create workflow instance for {config} failed")

    app = FastAPI(title="Vulcan", version="2024/01/21", description="")
    create_endpoints(app, wfi_list, configs)
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    args = parse_args()
    logging.info(f"args: {args}")
    main(args)
