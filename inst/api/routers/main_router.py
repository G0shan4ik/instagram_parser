from typing import Optional

from fastapi import APIRouter

from inst.parser.pars_inst_video import ParsVideoManager
from inst.parser.pars_inst_bio import ParsBioManager

from inst.api.datamodels import BaseData


main_router = APIRouter(
    tags=['ParsInst']
)

@main_router.post(
    '/instagram/get_profile_info'
)
async def get_profile_info(
    data: BaseData
):
    bio_manager: ParsBioManager = ParsBioManager()
    res_json: Optional[dict] = await bio_manager.run(
        links=data.links,
        print_data=data.print_data
    )

    return res_json


@main_router.post(
    '/instagram/get_video_info'
)
async def get_video_info(
    data: BaseData
):
    bio_manager: ParsVideoManager = ParsVideoManager()
    res_json: Optional[dict] = await bio_manager.run(
        links=data.links,
        per_second=data.per_second,
        print_data=data.print_data
    )

    return res_json
