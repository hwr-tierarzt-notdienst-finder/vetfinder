import textwrap
from pathlib import Path

from shared import data_collection
from shared import file_system
from shared import log


class TestPipelineFactory:

    def test_create_from_module_creates_pipeline_that_runs_correct_steps(self) -> None:
        current_dir = Path(__file__).parent
        temp_module_path = current_dir / "temp_module"
        temp_logs_dir = current_dir / "temp_logs"

        factory = data_collection.PipelineFactory(
            get_all_vets_from_db=lambda: [],
            replace_vets_in_db=lambda _: None,
            create_logger=lambda name: log.LoggerFactoryTimeBasedRolloverSingleDirDotDelimitedFiles(
                temp_logs_dir
            ).create(name)
        )

        with file_system.temp_dir(temp_logs_dir):
            with file_system.temp_dir(
                temp_module_path,
                [
                    {
                        "type": "file",
                        "name": "child_module1.py",
                        "contents": textwrap.dedent(
                            """
                            from logging import Logger
                            from typing import Iterable
                            
                            from shared.models import Vet
                            
                            
                            def collect(logger: Logger, vets: Iterable[Vet]) -> Iterable[Vet]:
                                logger.info("running collect step")
                                
                                return vets
                            """
                        )
                    },
                    {
                        "type": "file",
                        "name": "child_module2.py",
                        "contents": textwrap.dedent(
                            """
                            from logging import Logger
                            from typing import Iterable
                            
                            from shared.models import Vet
                            
                            
                            def collect_from_json(logger: Logger, vets: Iterable[Vet]) -> Iterable[Vet]:
                                logger.info("running collect:from_json step")
                                
                                return vets
                                
                                
                            def replace(
                                logger: Logger, 
                                vets_in_db: Iterable[Vet], 
                                collected_vets: Iterable[Vet]
                            ) -> Iterable[Vet]:
                                logger.info("running replace step")
                                
                                return vets_in_db, collected_vets
                            """
                        )
                    },
                    {
                        "type": "file",
                        "name": "child_module3.py",
                        "contents": textwrap.dedent(
                            """
                            from logging import Logger
                            from typing import Iterable
                            
                            from shared.models import Vet
                            
                            
                            def collect_from_json(logger: Logger, vets: Iterable[Vet]) -> Iterable[Vet]:
                                logger.info("running collect:from_json step")
                                
                                return vets
                                
                                
                            def validate(logger: Logger, vets: Iterable[Vet]) -> None:
                                logger.info("running validate step")
                                
                            
                            def normalize_location(logger: Logger, vets: Iterable[Vet]) -> Iterable[Vet]:
                                logger.info("running normalize:location")
                                
                                return vets
                                
                                
                            def replace(
                                logger: Logger, 
                                vets_in_db: Iterable[Vet], 
                                collected_vets: Iterable[Vet]
                            ) -> Iterable[Vet]:
                                logger.info("running replace step")
                                
                                return vets_in_db, collected_vets
                            """
                        )
                    },
                ],
            ):
                from temp_module import child_module1
                from temp_module import child_module2
                from temp_module import child_module3

                pipeline1 = factory.create_from_module(child_module1)
                pipeline1.run([])
                expected_log_line_matchers_for_pipeline1 = [
                    ("contains", "Step collect"),
                    ("end", "running collect step"),
                    ("contains", "Step collect")
                ]
                file_system.matching_file_contents(
                    temp_logs_dir / "child_module1.info",
                    expected_log_line_matchers_for_pipeline1,
                )

                pipeline2 = factory.create_from_module(child_module2)
                pipeline2.run([])
                expected_log_line_matchers_for_pipeline2 = [
                    ("contains", "Step collect:from_json"),
                    ("end", "running collect:from_json step"),
                    ("contains", "Step collect:from_json"),
                    ("contains", "Step replace"),
                    ("end", "running replace step"),
                    ("contains", "Step replace")
                ]
                file_system.matching_file_contents(
                    temp_logs_dir / "child_module2.info",
                    expected_log_line_matchers_for_pipeline2,
                )

                pipeline3 = factory.create_from_module(child_module3)
                pipeline3.run([])
                expected_log_line_matchers_for_pipeline3 = [
                    ("contains", "Step collect"),
                    ("end", "running collect step"),
                    ("contains", "Step collect"),
                    ("contains", "Step validate"),
                    ("end", "running validate step"),
                    ("contains", "Step validate"),
                    ("contains", "Step normalize:location"),
                    ("end", "running normalize:location step"),
                    ("contains", "Step normalize"),
                    ("contains", "Step replace"),
                    ("end", "running replace step"),
                    ("contains", "Step replace")
                ]
                file_system.matching_file_contents(
                    temp_logs_dir / "child_module1.info",
                    expected_log_line_matchers_for_pipeline3,
                )
