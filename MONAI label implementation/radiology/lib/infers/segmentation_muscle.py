# Copyright (c) MONAI Consortium
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Callable, Sequence
import torch  
import numpy as np

from monai.inferers import Inferer, SlidingWindowInferer, SlidingWindowInfererAdapt, SimpleInferer

from monai.transforms import (
    Activationsd,
    AsDiscreted,
    EnsureChannelFirstd,
    EnsureTyped,
    LoadImaged,
    NormalizeIntensityd,
    ScaleIntensityRanged,
    Spacingd,
    SpatialPadd,
    ToDeviced,
    Invertd,
    Compose,
    Orientationd,
    SaveImaged

)

from monailabel.interfaces.tasks.infer_v2 import InferType
from monailabel.tasks.infer.basic_infer import BasicInferTask
from monailabel.transform.post import Restored


class SegmentationMuscle(BasicInferTask):
    """
    This provides Inference Engine for pre-trained thigh muscle segmentation (SegResNet) model.
    """

    def __init__(
        self,
        path,
        network=None,
        type=InferType.SEGMENTATION,
        target_spacing=(0.7813000082969666, 0.7813000082969666, 4.0),
        labels=None,
        dimension=3,
        description="A pre-trained model for human thigh muscle segmentation (IDEAL fat/IDEAL water/T1/T2/STIR)",
        **kwargs,
    ):
        super().__init__(
            path=path,
            network=network,
            type=type,
            labels=labels,
            dimension=dimension,
            description=description,
            **kwargs,
        )
        self.target_spacing = target_spacing

    def pre_transforms(self, data=None) -> Sequence[Callable]:
        return [
            LoadImaged(keys="image", reader="ITKReader"),
            EnsureTyped(keys="image", device=data.get("device") if data else None),
            EnsureChannelFirstd(keys="image"),
            Spacingd(keys="image", mode="bilinear", pixdim=[0.7813000082969666, 0.7813000082969666, 4.0], dtype=torch.float32, allow_missing_keys=True),
            NormalizeIntensityd(keys="image", nonzero=True, channel_wise=True),
        ]

    def inferer(self, data=None) -> Inferer:
        return SlidingWindowInfererAdapt(roi_size=(336, 336, 88),
                                    sw_batch_size=1,
                                    overlap=0.625,
                                    mode="gaussian",
                                    cache_roi_weight_map=False,
                                    progress=False)
        

    def post_transforms(self, data=None) -> Sequence[Callable]:
        
        
        return [
            EnsureTyped(keys="pred", device=data.get("device") if data else None),
            Activationsd(keys="pred", softmax=True),
            AsDiscreted(keys="pred", argmax=True),  
            Restored(keys="pred", ref_image="image"), 
            
            
        ]
