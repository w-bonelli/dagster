import json

from dagster import check
from dagster.core.host_representation.external_data import ExternalPipelineSubsetResult
from dagster.core.reconstruction import PipelineReconstructionInfo
from dagster.serdes.ipc import read_unary_response
from dagster.seven import xplat_shlex_split
from dagster.utils.temp_file import get_temp_file_name

from .utils import execute_command_in_subprocess


def sync_get_external_pipeline_subset(local_pipeline_target, solid_selection=None):
    check.inst_param(local_pipeline_target, 'local_pipeline_target', PipelineReconstructionInfo)
    check.opt_list_param(solid_selection, 'solid_selection', of_type=str)

    with get_temp_file_name() as output_file:
        parts = (
            [
                local_pipeline_target.executable_path,
                '-m',
                'dagster',
                'api',
                'snapshot',
                'pipeline_subset',
                output_file,
            ]
            + xplat_shlex_split(local_pipeline_target.get_repo_cli_args())
            + [local_pipeline_target.pipeline_name]
        )

        if solid_selection:
            parts.append(
                '--solid-selection={solid_selection}'.format(
                    solid_selection=json.dumps(solid_selection)
                )
            )

        execute_command_in_subprocess(parts)

        external_pipeline_subset_result = read_unary_response(output_file)
        check.inst(external_pipeline_subset_result, ExternalPipelineSubsetResult)

        return external_pipeline_subset_result
