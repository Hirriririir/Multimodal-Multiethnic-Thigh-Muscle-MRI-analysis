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

import logging
import os
from typing import Any, Dict, Optional, Union
import torch

import lib.infers
import lib.trainers
from monai.networks.nets import SegResNetDS

from monailabel.interfaces.config import TaskConfig
from monailabel.interfaces.tasks.infer_v2 import InferTask
from monailabel.interfaces.tasks.train import TrainTask
from monailabel.utils.others.generic import download_file, strtobool

logger = logging.getLogger(__name__)


class SegmentationMuscle(TaskConfig):
    def init(self, name: str, model_dir: str, conf: Dict[str, str], planner: Any, **kwargs):
        super().init(name, model_dir, conf, planner, **kwargs)

        # Labels
        self.labels = {
            "SA": 1, # Sartorius
            "RF": 2, # Rectus femoris
            "VL": 3, # Vastus lateralis
            "VI": 4, # Vastus intermedius
            "VM": 5, # Vastus medialis
            "AM": 6, # adductor magnus
            "GR": 7, # Gracilis
            "BL": 8, # Biceps femoris long head
            "ST": 9, # Semitendinosus
            "SM": 10, # Semimembranosus
            "BB": 11, # Biceps femoris short head
        }



        # Model Files
        self.path = [
            os.path.join(self.model_dir, f"pretrained_{name}.pt"),  # pretrained
            os.path.join(self.model_dir, f"{name}.pt"),  # published
        ]

        # Download PreTrained Model
        if strtobool(self.conf.get("use_pretrained_model", "true")):
            url = f"{self.conf.get('pretrained_path', self.PRE_TRAINED_PATH)}"
            url = f"{url}/radiology_segmentation_muscle.pt"
            download_file(url, self.path[0])

        self.target_spacing = (0.7813000082969666, 0.7813000082969666, 4.0)  # target space for image
        self.roi_size = (336, 336, 88)

        # Network
        self.network = SegResNetDS(
            spatial_dims=3,
            norm = 'INSTANCE', 
            in_channels=1,
            out_channels=12,
            init_filters=32,
            blocks_down=(1, 2, 2, 4, 4),
            #blocks_up=(1, 1, 1),
            dsdepth=4,
            resolution = (0.7813000082969666, 0.7813000082969666, 4.0),
        )#.to(memory_format=torch.channels_last_3d)

    def infer(self) -> Union[InferTask, Dict[str, InferTask]]:
        task: InferTask = lib.infers.SegmentationMuscle(
            path=self.path,
            network=self.network,
            roi_size=self.roi_size,
            target_spacing=self.target_spacing,
            labels=self.labels,
            model_state_dict = "state_dict",
            preload=strtobool(self.conf.get("preload", "false")),
        )
        return task

    def trainer(self) -> Optional[TrainTask]:
        output_dir = os.path.join(self.model_dir, self.name)
        load_path = self.path[0] if os.path.exists(self.path[0]) else self.path[1]

        task: TrainTask = lib.trainers.SegmentationMuscle(
            model_dir=output_dir,
            network=self.network,
            #roi_size=self.roi_size,
            #target_spacing=self.target_spacing,
            load_path=load_path,
            publish_path=self.path[1],
            description="Train vertebra segmentation Model",
            labels=self.labels,
        )
        return task
